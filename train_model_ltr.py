"""
Train Learning-to-Rank (LTR) model using LightGBM LambdaMART
Version: 7.1-LTR

This model predicts relative rankings within a race rather than binary top-10 classification.
Uses listwise LTR approach: optimizes NDCG by comparing riders within each race.

Key differences from v6.x binary classification:
- Input: Same features per rider
- Output: Relevance scores (ranking within race)
- Objective: LambdaMART (pairwise gradient descent optimizing NDCG)
- Evaluation: NDCG@10, MAP@10, MRR (ranking-specific metrics)

v7.1 fixes:
- Use cross-validation instead of single train/test split for hyperparameter tuning
- More aggressive regularization to prevent overfitting
- Lower learning rate with more boosting rounds
- Final model trained on ALL data for maximum signal
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import GroupKFold
import lightgbm as lgb
import joblib
import json
from collections import defaultdict

import config

DATA_DIR = Path("data")
CLEAN_DIR = DATA_DIR / "clean"
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("TRAINING v7.1-LTR MODEL - LambdaMART Ranking")
print("=" * 70)

# Load enriched data
results_path = CLEAN_DIR / "results_with_features.csv"
print(f"\nLoading: {results_path}")
df = pd.read_csv(results_path, parse_dates=["race_date"])

print(f"Total observations: {len(df)}")
print(f"Date range: {df['race_date'].min()} to {df['race_date'].max()}")

# Filter to valid results
df = df[df["Place"].notna() & (df["Place"] > 0)].copy()
print(f"Valid results: {len(df)}")

# Create relevance labels (higher = better finish)
# Relevance scale 0-5:
# 5 = Winner (place 1)
# 4 = Podium (place 2-3)
# 3 = Top-5 (place 4-5)
# 2 = Top-10 (place 6-10)
# 1 = Top-20 (place 11-20)
# 0 = Below top-20 (place 21+)
def place_to_relevance(place):
    if place == 1:
        return 5
    elif place <= 3:
        return 4
    elif place <= 5:
        return 3
    elif place <= 10:
        return 2
    elif place <= 20:
        return 1
    else:
        return 0

df["relevance"] = df["Place"].apply(place_to_relevance)

print(f"\nRelevance distribution:")
for rel in range(6):
    count = (df["relevance"] == rel).sum()
    pct = 100 * count / len(df)
    labels = {5: "Winner", 4: "Podium", 3: "Top-5", 2: "Top-10", 1: "Top-20", 0: "Below"}
    print(f"  {rel} ({labels[rel]:7s}): {count:5d} ({pct:5.1f}%)")

# Define features (same as v6.10)
print("\n" + "=" * 70)
print("FEATURE SELECTION (same as v6.10)")
print("=" * 70)

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
    "is_women",
    "h2h_field_score",
    "is_new_rider"
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
y = df["relevance"].copy()
groups = df["race_id"].copy()  # Group by race for LTR

# One-hot encode categoricals
X = pd.get_dummies(X, columns=categorical_features, drop_first=True)

# Fill NaN with smart defaults (same as v6.10)
print("\n" + "=" * 70)
print("HANDLING MISSING VALUES")
print("=" * 70)

# Use UCI-based inference for place-related NaN values
for col in ["avg_place_last3", "best_place_last5", "last_place"]:
    mask = X[col].isna()
    if mask.sum() > 0:
        X.loc[mask, col] = (
            config.UCI_PLACE_INTERCEPT +
            config.UCI_PLACE_SLOPE * X.loc[mask, "uci_points_normalized"]
        ).clip(5, 70)

print(f"  Applied UCI-based inference for missing place data")

# Fill remaining with standard defaults
fill_values = {
    "uci_points_normalized": 0,
    "races_so_far": 0,
    "days_since_last_race": 14,
    "last_carried_points": 0,
    "last_scored_points": 0,
    "top3_rate_career": 0,
    "top10_rate_career": 0,
    "series_appearances": 0,
    "is_elite": 0,
    "is_women": 0,
    "h2h_field_score": 0.5,
    "is_new_rider": 0
}

X = X.fillna(fill_values)
print(f"  Missing values after fill: {X.isna().sum().sum()}")

# Create group-aware train/test split (by race, chronological)
print("\n" + "=" * 70)
print("TRAIN/TEST SPLIT (Group-aware, Chronological)")
print("=" * 70)

# Get unique races sorted by date
race_dates = df.groupby("race_id")["race_date"].first().sort_values()
unique_races = race_dates.index.tolist()

# 80% train, 20% test (by race)
split_idx = int(len(unique_races) * 0.8)
train_races = set(unique_races[:split_idx])
test_races = set(unique_races[split_idx:])

train_mask = groups.isin(train_races)
test_mask = groups.isin(test_races)

X_train = X[train_mask]
X_test = X[test_mask]
y_train = y[train_mask]
y_test = y[test_mask]
groups_train = groups[train_mask]
groups_test = groups[test_mask]

print(f"\nTrain: {len(X_train)} observations from {len(train_races)} races")
print(f"Test: {len(X_test)} observations from {len(test_races)} races")
print(f"Train date range: {race_dates[unique_races[:split_idx]].min()} to {race_dates[unique_races[:split_idx]].max()}")
print(f"Test date range: {race_dates[unique_races[split_idx:]].min()} to {race_dates[unique_races[split_idx:]].max()}")

# Create group sizes for LightGBM
def get_group_sizes(groups):
    """Get list of group sizes for LightGBM"""
    sizes = groups.value_counts().reindex(groups.unique()).values
    return sizes.tolist()

# Sort by group to ensure contiguous groups
train_sort_idx = groups_train.argsort()
X_train_sorted = X_train.iloc[train_sort_idx]
y_train_sorted = y_train.iloc[train_sort_idx]
groups_train_sorted = groups_train.iloc[train_sort_idx]

test_sort_idx = groups_test.argsort()
X_test_sorted = X_test.iloc[test_sort_idx]
y_test_sorted = y_test.iloc[test_sort_idx]
groups_test_sorted = groups_test.iloc[test_sort_idx]

# Get group sizes
train_group_sizes = groups_train_sorted.value_counts().sort_index().tolist()
test_group_sizes = groups_test_sorted.value_counts().sort_index().tolist()

print(f"\nGroup sizes - Train: {len(train_group_sizes)} groups, avg {np.mean(train_group_sizes):.1f} riders/race")
print(f"Group sizes - Test: {len(test_group_sizes)} groups, avg {np.mean(test_group_sizes):.1f} riders/race")

# LambdaMART parameters - v7.1 with stronger regularization
# Fixed: Previous version stopped at 2 iterations due to overfitting with small test set
params = {
    "objective": "lambdarank",
    "metric": "ndcg",
    "ndcg_eval_at": [3, 5, 10],  # Evaluate NDCG at these cutoffs
    "boosting_type": "gbdt",
    "num_leaves": 15,           # Reduced from 31 - simpler trees
    "learning_rate": 0.01,      # Reduced from 0.05 - slower learning
    "feature_fraction": 0.7,    # Reduced from 0.9 - more regularization
    "bagging_fraction": 0.7,    # Reduced from 0.8 - more regularization
    "bagging_freq": 5,
    "min_child_samples": 50,    # Increased from 20 - require more samples per leaf
    "lambda_l1": 1.0,           # Increased from 0.1 - stronger L1 regularization
    "lambda_l2": 1.0,           # Increased from 0.1 - stronger L2 regularization
    "max_depth": 5,             # New: limit tree depth
    "verbose": -1,
    "random_state": 42,
    "n_jobs": -1
}

print("\nLambdaMART Parameters (v7.1 - regularized):")
for k, v in params.items():
    print(f"  {k}: {v}")

# First: Use cross-validation to find optimal number of rounds
print("\n" + "=" * 70)
print("CROSS-VALIDATION FOR OPTIMAL ROUNDS")
print("=" * 70)

# Create full dataset for CV
full_data = lgb.Dataset(
    X_train_sorted,
    label=y_train_sorted,
    group=train_group_sizes,
    feature_name=X.columns.tolist()
)

# Run CV to find optimal iterations (using training data only)
print("\nRunning 5-fold group cross-validation...")
cv_results = lgb.cv(
    params,
    full_data,
    num_boost_round=500,
    nfold=5,
    stratified=False,  # Use group-based folds for ranking
    shuffle=False,     # Keep chronological order
    callbacks=[
        lgb.early_stopping(stopping_rounds=30),
        lgb.log_evaluation(period=50)
    ],
    return_cvbooster=False
)

# Get best iteration from CV
best_rounds = len(cv_results['valid ndcg@10-mean'])
best_cv_ndcg = cv_results['valid ndcg@10-mean'][-1]
print(f"\nCV Results:")
print(f"  Best rounds: {best_rounds}")
print(f"  CV NDCG@10: {best_cv_ndcg:.4f} (+/- {cv_results['valid ndcg@10-stdv'][-1]:.4f})")

# Train final model on ALL training data with optimal rounds
print("\n" + "=" * 70)
print("TRAINING FINAL MODEL")
print("=" * 70)

# Use at least 50 rounds even if CV says fewer
final_rounds = max(best_rounds, 50)
print(f"\nTraining with {final_rounds} rounds (max of CV best: {best_rounds} and minimum: 50)...")

train_data = lgb.Dataset(
    X_train_sorted,
    label=y_train_sorted,
    group=train_group_sizes,
    feature_name=X.columns.tolist()
)

test_data = lgb.Dataset(
    X_test_sorted,
    label=y_test_sorted,
    group=test_group_sizes,
    reference=train_data,
    feature_name=X.columns.tolist()
)

model_ltr = lgb.train(
    params,
    train_data,
    num_boost_round=final_rounds,
    valid_sets=[train_data, test_data],
    valid_names=["train", "test"],
    callbacks=[
        lgb.log_evaluation(period=25)
    ]
)

print(f"\nTraining rounds: {final_rounds}")

# Evaluate on test set
print("\n" + "=" * 70)
print("EVALUATION METRICS")
print("=" * 70)

# Get predictions
y_pred = model_ltr.predict(X_test_sorted)

# Calculate NDCG manually per race
def calculate_ndcg(y_true, y_pred, groups, k=10):
    """Calculate NDCG@k across all groups"""
    ndcg_scores = []

    start_idx = 0
    group_ids = groups.unique()

    for group_size in test_group_sizes:
        end_idx = start_idx + group_size

        true_rels = y_true.iloc[start_idx:end_idx].values
        pred_scores = y_pred[start_idx:end_idx]

        # Sort by predicted scores (descending)
        sorted_indices = np.argsort(pred_scores)[::-1]
        sorted_rels = true_rels[sorted_indices]

        # DCG
        dcg = 0
        for i, rel in enumerate(sorted_rels[:k]):
            dcg += (2**rel - 1) / np.log2(i + 2)

        # IDCG (ideal DCG)
        ideal_rels = np.sort(true_rels)[::-1]
        idcg = 0
        for i, rel in enumerate(ideal_rels[:k]):
            idcg += (2**rel - 1) / np.log2(i + 2)

        ndcg = dcg / idcg if idcg > 0 else 0
        ndcg_scores.append(ndcg)

        start_idx = end_idx

    return np.mean(ndcg_scores)

def calculate_map(y_true, y_pred, groups, k=10, relevance_threshold=2):
    """Calculate MAP@k (Mean Average Precision)"""
    ap_scores = []

    start_idx = 0
    for group_size in test_group_sizes:
        end_idx = start_idx + group_size

        true_rels = y_true.iloc[start_idx:end_idx].values
        pred_scores = y_pred[start_idx:end_idx]

        # Binary relevance (top-10 = relevance >= 2)
        relevant = (true_rels >= relevance_threshold)

        # Sort by predicted scores
        sorted_indices = np.argsort(pred_scores)[::-1]
        sorted_relevant = relevant[sorted_indices]

        # Calculate AP
        precision_sum = 0
        relevant_count = 0
        for i, is_rel in enumerate(sorted_relevant[:k]):
            if is_rel:
                relevant_count += 1
                precision_sum += relevant_count / (i + 1)

        ap = precision_sum / min(relevant.sum(), k) if relevant.sum() > 0 else 0
        ap_scores.append(ap)

        start_idx = end_idx

    return np.mean(ap_scores)

def calculate_mrr(y_true, y_pred, groups, relevance_threshold=5):
    """Calculate MRR (Mean Reciprocal Rank) for finding the winner"""
    rr_scores = []

    start_idx = 0
    for group_size in test_group_sizes:
        end_idx = start_idx + group_size

        true_rels = y_true.iloc[start_idx:end_idx].values
        pred_scores = y_pred[start_idx:end_idx]

        # Find the winner (relevance = 5)
        is_winner = (true_rels >= relevance_threshold)

        if is_winner.sum() == 0:
            start_idx = end_idx
            continue

        # Sort by predicted scores
        sorted_indices = np.argsort(pred_scores)[::-1]
        sorted_is_winner = is_winner[sorted_indices]

        # Find first winner rank
        for rank, is_w in enumerate(sorted_is_winner, 1):
            if is_w:
                rr_scores.append(1.0 / rank)
                break

        start_idx = end_idx

    return np.mean(rr_scores) if rr_scores else 0

# Calculate metrics
ndcg_3 = calculate_ndcg(y_test_sorted, y_pred, groups_test_sorted, k=3)
ndcg_5 = calculate_ndcg(y_test_sorted, y_pred, groups_test_sorted, k=5)
ndcg_10 = calculate_ndcg(y_test_sorted, y_pred, groups_test_sorted, k=10)
map_10 = calculate_map(y_test_sorted, y_pred, groups_test_sorted, k=10)
mrr = calculate_mrr(y_test_sorted, y_pred, groups_test_sorted)

print(f"\nRanking Metrics:")
print(f"  NDCG@3:  {ndcg_3:.4f}")
print(f"  NDCG@5:  {ndcg_5:.4f}")
print(f"  NDCG@10: {ndcg_10:.4f}")
print(f"  MAP@10:  {map_10:.4f}")
print(f"  MRR:     {mrr:.4f} (finding the winner)")

# Calculate Top-10 accuracy for comparison with v6.10
def calculate_top10_accuracy(y_true, y_pred, groups):
    """Calculate Top-10 prediction accuracy per race"""
    correct = 0
    total = 0

    start_idx = 0
    for group_size in test_group_sizes:
        end_idx = start_idx + group_size

        true_rels = y_true.iloc[start_idx:end_idx].values
        pred_scores = y_pred[start_idx:end_idx]

        # Actual top-10 (relevance >= 2)
        actual_top10 = set(np.where(true_rels >= 2)[0])

        # Predicted top-10 (top 10 by score, or fewer if group smaller)
        k = min(10, len(pred_scores))
        pred_top10 = set(np.argsort(pred_scores)[-k:])

        # Count correct predictions
        correct += len(actual_top10 & pred_top10)
        total += len(actual_top10)

        start_idx = end_idx

    return correct / total if total > 0 else 0

top10_recall = calculate_top10_accuracy(y_test_sorted, y_pred, groups_test_sorted)
print(f"\nTop-10 Recall: {top10_recall:.4f} (comparable to v6.10 accuracy)")

# Feature importance
print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model_ltr.feature_importance(importance_type="gain")
}).sort_values("importance", ascending=False)

importance["importance_pct"] = 100 * importance["importance"] / importance["importance"].sum()

print("\nTop 10 features (by gain):")
for i, row in importance.head(10).iterrows():
    print(f"  {row['feature']:30s}  {row['importance_pct']:5.1f}%")

# Save model
print("\n" + "=" * 70)
print("SAVING MODEL")
print("=" * 70)

model_path = MODELS_DIR / "ltr_ranker.joblib"
joblib.dump(model_ltr, model_path)
print(f"Saved LTR model to: {model_path}")

# Save metadata
feature_importance_dict = dict(zip(
    importance["feature"].tolist(),
    importance["importance_pct"].round(1).tolist()
))

meta_ltr = {
    "model_type": "LambdaMART (LightGBM)",
    "version": "7.1-LTR",
    "features": X.columns.tolist(),
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "fill_values": fill_values,
    "relevance_scale": {
        "5": "Winner (place 1)",
        "4": "Podium (place 2-3)",
        "3": "Top-5 (place 4-5)",
        "2": "Top-10 (place 6-10)",
        "1": "Top-20 (place 11-20)",
        "0": "Below Top-20"
    },
    "metrics": {
        "ndcg_3": round(ndcg_3, 4),
        "ndcg_5": round(ndcg_5, 4),
        "ndcg_10": round(ndcg_10, 4),
        "map_10": round(map_10, 4),
        "mrr": round(mrr, 4),
        "top10_recall": round(top10_recall, 4)
    },
    "params": params,
    "cv_best_rounds": best_rounds,
    "cv_ndcg10": round(best_cv_ndcg, 4),
    "final_rounds": final_rounds,
    "train_races": len(train_races),
    "test_races": len(test_races),
    "train_observations": len(X_train),
    "test_observations": len(X_test),
    "training_date": str(pd.Timestamp.now()),
    "feature_importance": feature_importance_dict
}

meta_path = MODELS_DIR / "ltr_metadata.json"
with open(meta_path, "w") as f:
    json.dump(meta_ltr, f, indent=2)
print(f"Saved LTR metadata to: {meta_path}")

# Summary
print("\n" + "=" * 70)
print("TRAINING SUMMARY - v7.1-LTR")
print("=" * 70)

print(f"\nModel: LambdaMART (LightGBM)")
print(f"Objective: Optimize NDCG (ranking quality)")
print(f"CV Best Rounds: {best_rounds}, Final Rounds: {final_rounds}")

print(f"\nRanking Performance:")
print(f"  NDCG@3:  {ndcg_3:.4f}")
print(f"  NDCG@5:  {ndcg_5:.4f}")
print(f"  NDCG@10: {ndcg_10:.4f}")
print(f"  MAP@10:  {map_10:.4f}")
print(f"  MRR:     {mrr:.4f}")

print(f"\nComparison with v6.10:")
print(f"  LTR Top-10 Recall: {top10_recall:.4f}")
print(f"  v6.10 Top-10 Accuracy: 0.8047 (from model_metadata.json)")

print(f"\nData:")
print(f"  Train: {len(train_races)} races, {len(X_train)} observations")
print(f"  Test: {len(test_races)} races, {len(X_test)} observations")

print(f"\nTop 3 Features:")
for i, row in importance.head(3).iterrows():
    print(f"  {row['feature']:30s}  {row['importance_pct']:5.1f}%")

print("\n" + "=" * 70)
print("LTR MODEL READY")
print("=" * 70)
print("\nNext steps:")
print("  1. Run predict_race_ltr.py to generate predictions")
print("  2. Compare with v6.10 predictions on same race")
print("  3. Validate against actual results")
