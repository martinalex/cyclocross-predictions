"""
Predict race results using LTR (Learning-to-Rank) model
Version: 7.1-LTR

This generates predictions using the LambdaMART ranker instead of binary classification.
Output is a ranking score per rider - higher score = better predicted finish.
"""
import pandas as pd
import numpy as np
import joblib
import json
import argparse
from pathlib import Path

import config
from src.features.builder import FeatureBuilder


def load_ltr_model():
    """Load trained LTR model"""
    model_path = config.MODELS_DIR / "ltr_ranker.joblib"
    meta_path = config.MODELS_DIR / "ltr_metadata.json"

    model = joblib.load(model_path)

    with open(meta_path, 'r') as f:
        metadata = json.load(f)

    return model, metadata


def predict_race_ltr(
    startlist_path,
    category="Men Elite",
    output_path=None
):
    """Generate LTR predictions for a race

    Args:
        startlist_path: Path to startlist CSV
        category: Race category (e.g., "Men Elite")
        output_path: Where to save predictions

    Returns:
        DataFrame with predictions sorted by ranking score
    """
    print("=" * 70)
    print("VELOPREDICT: LTR PREDICTIONS (v7.1-LTR)")
    print("=" * 70)

    # Load model and initialize FeatureBuilder
    print("\nLoading LTR model and data...")
    model, metadata = load_ltr_model()
    builder = FeatureBuilder(load_h2h=True)

    print(f"Model: {metadata['model_type']}")
    print(f"Version: {metadata['version']}")
    print(f"NDCG@10: {metadata['metrics']['ndcg_10']:.4f}")
    print(f"Historical data: {len(builder.historical_data)} observations")
    print(f"UCI rankings loaded: {len(builder.uci_rankings)} riders")

    # Load startlist
    print(f"\nLoading startlist: {startlist_path}")
    startlist = pd.read_csv(startlist_path)
    print(f"Found {len(startlist)} riders")

    # Build field list for H2H
    field_names = []
    for idx, row in startlist.iterrows():
        rider_name = row.get("rider_name", row.get("Naam", row.get("Name")))
        field_names.append(rider_name)

    print(f"\nBuilding head-to-head matrix...")
    print(f"H2H matrix ready ({len(field_names)} riders in field)")

    # Generate predictions
    predictions = []
    feature_rows = []

    print(f"\nGenerating predictions for {category}...")
    print("-" * 70)

    for idx, row in startlist.iterrows():
        rider_name = row.get("rider_name", row.get("Naam", row.get("Name")))

        # Get UCI rank from startlist (if available)
        uci_rank = row.get("UCI Rank", row.get("UCI", row.get("uci_rank", None)))
        if uci_rank is not None:
            uci_rank = pd.to_numeric(uci_rank, errors='coerce')

        # Get features using unified FeatureBuilder
        rider_features = builder.get_rider_features(rider_name, category, startlist_uci_rank=uci_rank)

        # Add H2H features
        builder.add_h2h_features(rider_features, rider_name, field_names)

        # Prepare model input
        X = builder.prepare_model_input(rider_features)
        feature_rows.append(X.iloc[0])

        # Store rider info for output
        predictions.append({
            "Rider": rider_name,
            "Status": rider_features.status,
            "H2H Field Score": rider_features.features.get("h2h_field_score", 0.5),
            "H2H Confidence": getattr(rider_features, 'h2h_confidence', 0.0),
            "H2H Known Opponents": getattr(rider_features, 'h2h_known_opponents', 0),
            "Recent Form": rider_features.features.get("avg_place_last3", "N/A"),
            "Career Top-10 Rate": rider_features.features.get("top10_rate_career", 0),
            "Is New Rider": rider_features.is_new_rider
        })

    # Stack all feature rows and predict
    X_all = pd.DataFrame(feature_rows)

    # Predict ranking scores
    ranking_scores = model.predict(X_all)

    # Add scores to predictions
    for i, score in enumerate(ranking_scores):
        predictions[i]["LTR Score"] = score

    # Sort by ranking score (descending - higher is better)
    df_predictions = pd.DataFrame(predictions).sort_values("LTR Score", ascending=False)
    df_predictions["Predicted Rank"] = range(1, len(df_predictions) + 1)

    # Display results
    print("\n" + "=" * 70)
    print("LTR PREDICTED TOP-10 FINISHERS")
    print("=" * 70)

    top10 = df_predictions.head(10)
    for idx, row in top10.iterrows():
        rank = row['Predicted Rank']
        h2h_pct = row['H2H Field Score'] * 100 if row['H2H Confidence'] > 0 else 0
        h2h_str = f"(H2H: {h2h_pct:3.0f}%)" if row['H2H Confidence'] > 0.3 else "(H2H: N/A)"
        new_flag = " [NEW]" if row['Is New Rider'] else ""
        print(f"   {rank:2d}. {row['Rider']:30s}  Score: {row['LTR Score']:6.3f}  {h2h_str}{new_flag}")

    # Show predicted podium
    print("\n" + "=" * 70)
    print("LTR PREDICTED PODIUM")
    print("=" * 70)

    podium = df_predictions.head(3)
    medals = ["1.", "2.", "3."]
    for idx, (_, row) in enumerate(podium.iterrows()):
        new_flag = " (new rider)" if row['Is New Rider'] else ""
        print(f"{medals[idx]} {row['Rider']:30s}  Score: {row['LTR Score']:.3f}{new_flag}")

    # Save predictions
    if output_path is None:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
        output_path = config.CLEAN_DIR / f"predictions_ltr_{timestamp}.csv"

    df_predictions.to_csv(output_path, index=False)
    print(f"\nPredictions saved to: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Riders analyzed: {len(df_predictions)}")
    print(f"Riders with history: {len(df_predictions[df_predictions['Status'] == 'found'])}")
    print(f"New riders: {len(df_predictions[df_predictions['Is New Rider'] == True])}")

    # Score distribution
    scores = df_predictions['LTR Score']
    print(f"\nScore Distribution:")
    print(f"  Max: {scores.max():.3f}")
    print(f"  Mean: {scores.mean():.3f}")
    print(f"  Min: {scores.min():.3f}")
    print(f"  Std: {scores.std():.3f}")

    # H2H coverage
    h2h_coverage = df_predictions[df_predictions['H2H Confidence'] > 0.3]
    print(f"\nHead-to-Head Analysis:")
    print(f"  - Riders with H2H data: {len(h2h_coverage)}/{len(df_predictions)}")

    print("\n" + "=" * 70)

    return df_predictions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict race results using LTR model")
    parser.add_argument("--startlist", required=True, help="Path to startlist CSV")
    parser.add_argument("--category", default="Men Elite", help="Race category")
    parser.add_argument("--output", help="Output path for predictions")

    args = parser.parse_args()

    predictions = predict_race_ltr(
        args.startlist,
        args.category,
        args.output
    )
