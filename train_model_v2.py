"""
Train improved model with real features + calculate business-relevant metrics
Focus: Top-10 prediction accuracy (who scores points?)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    mean_absolute_error,
    accuracy_score,
    classification_report,
    roc_auc_score,
    brier_score_loss,
    log_loss
)
import joblib
import json

DATA_DIR = Path("data")
CLEAN_DIR = DATA_DIR / "clean"
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("TRAINING v4 MODEL - UCI-BASED INFERENCE FOR NEW RIDERS")
print("=" * 60)

# Load enriched data
results_path = CLEAN_DIR / "results_with_features.csv"
print(f"\nLoading: {results_path}")
df = pd.read_csv(results_path, parse_dates=["race_date"])

print(f"Total observations: {len(df)}")
print(f"Date range: {df['race_date'].min()} to {df['race_date'].max()}")

# Filter to valid results
df = df[df["Place"].notna() & (df["Place"] > 0)].copy()
print(f"Valid results: {len(df)}")

# Create target variables
df["is_top10"] = (df["Place"] <= 10).astype(int)
df["is_top3"] = (df["Place"] <= 3).astype(int)

print(f"\nTarget distribution:")
print(f"  Top-10 finishes: {df['is_top10'].sum()} ({100*df['is_top10'].mean():.1f}%)")
print(f"  Top-3 finishes: {df['is_top3'].sum()} ({100*df['is_top3'].mean():.1f}%)")

# Define feature set
print("\n" + "=" * 60)
print("FEATURE SELECTION")
print("=" * 60)

numeric_features = [
    "uci_points_normalized",
    "races_so_far",
    "avg_place_last3",
    "best_place_last5",
    "last_place",
    "days_since_last_race",
    "last_carried_points",
    "last_scored_points",
    "top3_rate_career",
    "top10_rate_career",
    "series_appearances",
    "is_elite",
    "is_women"
]

categorical_features = [
    "points_tier",
    "team_tier"
]

print(f"\nNumeric features: {len(numeric_features)}")
for f in numeric_features:
    print(f"  - {f}")

print(f"\nCategorical features: {len(categorical_features)}")
for f in categorical_features:
    print(f"  - {f}")

# Prepare features
X = df[numeric_features + categorical_features].copy()
y_top10 = df["is_top10"].copy()
y_top3 = df["is_top3"].copy()

# One-hot encode categoricals
X = pd.get_dummies(X, columns=categorical_features, drop_first=True)

# Fill NaN with smart defaults
print("\n" + "=" * 60)
print("HANDLING MISSING VALUES (v4 - UCI-BASED INFERENCE)")
print("=" * 60)

# v4 IMPROVEMENT: Use UCI points to infer expected performance for new riders
# Instead of generic percentile, use linear regression: place = 9.31 + 51.36 * uci_normalized
# NOTE: UCI "Carried Points" are inverted (lower points = better ranking)
# So: low uci_normalized = strong rider → predicts low place (strong finish)
#     high uci_normalized = weak rider → predicts high place (weak finish)

import config

# Fill place-related NaN values using UCI-based inference
print("\nApplying UCI-based inference for missing historical data...")

for col in ["avg_place_last3", "best_place_last5", "last_place"]:
    mask = X[col].isna()
    if mask.sum() > 0:
        # For each NaN, infer place from UCI points
        X.loc[mask, col] = (
            config.UCI_PLACE_INTERCEPT +
            config.UCI_PLACE_SLOPE * X.loc[mask, "uci_points_normalized"]
        ).clip(5, 70)  # Bound to reasonable range

print(f"  ✓ Inferred {mask.sum()} place values from UCI points")
print(f"    Example: Strong rider (UCI norm=0.17) → place≈18 (strong finish)")
print(f"             Weak rider (UCI norm=0.60) → place≈40 (weak finish)")

# Fill remaining non-place features with standard defaults
fill_values = {
    "uci_points_normalized": 0,  # Truly unknown rider
    "races_so_far": 0,
    "days_since_last_race": 14,  # Typical race frequency
    "last_carried_points": 0,
    "last_scored_points": 0,
    "top3_rate_career": 0,
    "top10_rate_career": 0,
    "series_appearances": 0,
    "is_elite": 0,
    "is_women": 0
}

X = X.fillna(fill_values)

print(f"\nMissing values after fill: {X.isna().sum().sum()}")

# Train/test split by DATE (chronological)
print("\n" + "=" * 60)
print("TRAIN/TEST SPLIT (CHRONOLOGICAL)")
print("=" * 60)

# Use early races for train, recent races for test
df_sorted = df.sort_values("race_date")
split_idx = int(len(df_sorted) * 0.8)

train_indices = df_sorted.index[:split_idx]
test_indices = df_sorted.index[split_idx:]

X_train = X.loc[train_indices]
X_test = X.loc[test_indices]
y_top10_train = y_top10.loc[train_indices]
y_top10_test = y_top10.loc[test_indices]
y_top3_train = y_top3.loc[train_indices]
y_top3_test = y_top3.loc[test_indices]

print(f"\nTrain set: {len(X_train)} observations")
print(f"Test set: {len(X_test)} observations")
print(f"Train date range: {df_sorted.loc[train_indices, 'race_date'].min()} to {df_sorted.loc[train_indices, 'race_date'].max()}")
print(f"Test date range: {df_sorted.loc[test_indices, 'race_date'].min()} to {df_sorted.loc[test_indices, 'race_date'].max()}")

# Train Top-10 classifier
print("\n" + "=" * 60)
print("TRAINING TOP-10 CLASSIFIER")
print("=" * 60)

model_top10 = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"  # Handle class imbalance
)

model_top10.fit(X_train, y_top10_train)
print("✓ Base model trained")

# Calibrate probabilities (Platt scaling)
print("\n📊 Calibrating probabilities with Platt scaling...")
model_top10_calibrated = CalibratedClassifierCV(
    model_top10,
    method='sigmoid',  # Platt scaling
    cv='prefit'  # Use pre-trained model
)
model_top10_calibrated.fit(X_train, y_top10_train)
print("✓ Model calibrated")

# Predict with calibrated model
y_top10_pred = model_top10_calibrated.predict(X_test)
y_top10_pred_proba = model_top10_calibrated.predict_proba(X_test)[:, 1]

# Evaluate
accuracy = accuracy_score(y_top10_test, y_top10_pred)
try:
    auc = roc_auc_score(y_top10_test, y_top10_pred_proba)
    brier = brier_score_loss(y_top10_test, y_top10_pred_proba)
    logloss = log_loss(y_top10_test, y_top10_pred_proba)
except:
    auc = 0.0
    brier = 0.0
    logloss = 0.0

print(f"\n✓ TOP-10 ACCURACY: {100*accuracy:.1f}%")
if auc > 0:
    print(f"✓ AUC-ROC: {auc:.3f}")
    print(f"✓ Brier Score: {brier:.4f} (lower is better, 0.2 is good)")
    print(f"✓ Log Loss: {logloss:.4f}")

print("\nClassification Report:")
print(classification_report(y_top10_test, y_top10_pred, target_names=["Outside Top-10", "Top-10"]))

# Calculate baseline (always predict by UCI points)
baseline_pred = (df.loc[test_indices, "uci_points_normalized"] > df.loc[test_indices, "uci_points_normalized"].median()).astype(int)
baseline_acc = accuracy_score(y_top10_test, baseline_pred)
print(f"\nBaseline (UCI points only): {100*baseline_acc:.1f}%")
print(f"Improvement over baseline: +{100*(accuracy - baseline_acc):.1f}%")

# Feature importance
print("\n" + "=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model_top10.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 features:")
print(feature_importance.head(10).to_string(index=False))

# Train Top-3 classifier (bonus)
print("\n" + "=" * 60)
print("TRAINING TOP-3 CLASSIFIER (PODIUM)")
print("=" * 60)

model_top3 = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

model_top3.fit(X_train, y_top3_train)

# Calibrate Top-3 model as well
print("\n📊 Calibrating Top-3 model...")
model_top3_calibrated = CalibratedClassifierCV(
    model_top3,
    method='sigmoid',
    cv='prefit'
)
model_top3_calibrated.fit(X_train, y_top3_train)
print("✓ Top-3 model calibrated")

y_top3_pred = model_top3_calibrated.predict(X_test)

accuracy_top3 = accuracy_score(y_top3_test, y_top3_pred)
print(f"\n✓ TOP-3 ACCURACY: {100*accuracy_top3:.1f}%")

# Save models
print("\n" + "=" * 60)
print("SAVING MODELS")
print("=" * 60)

joblib.dump(model_top10_calibrated, MODELS_DIR / "top10_classifier.joblib")
joblib.dump(model_top3_calibrated, MODELS_DIR / "top3_classifier.joblib")

# Save metadata
meta = {
    "features": X.columns.tolist(),
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "fill_values": fill_values,
    "top10_accuracy": float(accuracy),
    "top10_auc": float(auc) if auc > 0 else None,
    "top10_brier_score": float(brier) if brier > 0 else None,
    "top10_log_loss": float(logloss) if logloss > 0 else None,
    "top3_accuracy": float(accuracy_top3),
    "baseline_accuracy": float(baseline_acc),
    "improvement_vs_baseline": float(accuracy - baseline_acc),
    "train_size": len(X_train),
    "test_size": len(X_test),
    "calibration_method": "sigmoid (Platt scaling)",
    "training_date": str(pd.Timestamp.now())
}

with open(MODELS_DIR / "model_metadata.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"✓ Saved models to {MODELS_DIR}/")
print(f"  - top10_classifier.joblib")
print(f"  - top3_classifier.joblib")
print(f"  - model_metadata.json")

# Summary
print("\n" + "=" * 60)
print("TRAINING SUMMARY")
print("=" * 60)

print(f"\n✅ MODEL PERFORMANCE:")
print(f"  Top-10 Accuracy: {100*accuracy:.1f}%")
print(f"  Top-3 Accuracy: {100*accuracy_top3:.1f}%")
print(f"  Baseline (UCI only): {100*baseline_acc:.1f}%")
print(f"  Improvement: +{100*(accuracy - baseline_acc):.1f}%")
if brier > 0:
    print(f"  Brier Score: {brier:.4f} (calibration quality)")
    print(f"  AUC-ROC: {auc:.3f}")

print(f"\n✅ DATA:")
print(f"  Total races: {df['race_id'].nunique()}")
print(f"  Total riders: {df['rider_name'].nunique()}")
print(f"  Total observations: {len(df)}")

print(f"\n✅ READY FOR USER TESTING:")
print(f"  Model predicts which riders will finish Top-10")
print(f"  {100*accuracy:.0f}% accuracy on recent races")
print(f"  {100*(accuracy - baseline_acc):.0f}% better than just using UCI points")

print("\n" + "=" * 60)
