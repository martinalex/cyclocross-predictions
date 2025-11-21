"""
Predict Top-10 finishers for upcoming race
Usage: python predict_race.py --startlist data/startlists/tabor_men_elite_2025-11-23.csv
"""
import pandas as pd
import numpy as np
import joblib
import json
import argparse
from pathlib import Path
import config

def load_historical_data():
    """Load historical rider data for feature lookup"""
    df = pd.read_csv(config.RESULTS_WITH_FEATURES, parse_dates=["race_date"])
    return df

def load_models():
    """Load trained models"""
    model_top10 = joblib.load(config.TOP10_MODEL)
    model_top3 = joblib.load(config.TOP3_MODEL)

    with open(config.MODEL_METADATA, 'r') as f:
        metadata = json.load(f)

    return model_top10, model_top3, metadata

def normalize_name(name):
    """Normalize rider name for matching"""
    if pd.isna(name):
        return None
    name = str(name).strip().lower()
    name = (
        name.replace("é", "e").replace("è", "e").replace("ë", "e")
            .replace("ó", "o").replace("ò", "o").replace("ö", "o")
            .replace("á", "a").replace("à", "a").replace("ä", "a")
            .replace("ü", "u").replace("ï", "i").replace("ř", "r")
            .replace("ž", "z").replace("š", "s").replace("č", "c")
    )
    return name

def get_rider_features(rider_name, historical_data, category="Men Elite"):
    """Get latest features for a rider from historical data"""

    # Normalize name for matching
    norm_name = normalize_name(rider_name)
    historical_data["rider_name_norm"] = historical_data["rider_name"].apply(normalize_name)

    # Try different name formats for matching
    # "LASTNAME Firstname" -> "firstname lastname"
    parts = norm_name.split()
    if len(parts) >= 2:
        # Try reversed: "firstname lastname"
        reversed_name = f"{parts[-1]} {' '.join(parts[:-1])}"
    else:
        reversed_name = norm_name

    # Find rider's most recent race (try both name orders)
    rider_history = historical_data[
        (
            (historical_data["rider_name_norm"] == norm_name) |
            (historical_data["rider_name_norm"] == reversed_name)
        ) &
        (historical_data["Category Name"].str.contains(category.split()[0], case=False, na=False))
    ].sort_values("race_date", ascending=False)

    if len(rider_history) > 0:
        # Use most recent data
        latest = rider_history.iloc[0]

        features = {
            "uci_points_normalized": latest["uci_points_normalized"],
            "races_so_far": latest["races_so_far"] + 1,  # +1 for this race
            "avg_place_last3": latest["avg_place_last3"],
            "best_place_last5": latest["best_place_last5"],
            "last_place": latest["Place"],
            "days_since_last_race": 7,  # Assume weekly racing
            "last_carried_points": latest["Carried Points"],
            "last_scored_points": latest["Scored Points"],
            "top3_rate_career": latest["top3_rate_career"],
            "top10_rate_career": latest["top10_rate_career"],
            "series_appearances": 0,  # Reset for new series
            "is_elite": 1 if "Elite" in category else 0,
            "is_women": 1 if "Women" in category else 0,
            "points_tier": latest["points_tier"],
            "team_tier": latest["team_tier"]
        }

        return features, "found"
    else:
        # New rider - use defaults
        print(f"  ⚠️  {rider_name}: No history found, using defaults")

        features = {
            "uci_points_normalized": 0.1,  # Low but not zero
            "races_so_far": 0,
            "avg_place_last3": config.MEDIAN_PLACE_DEFAULT,
            "best_place_last5": config.MEDIAN_PLACE_DEFAULT,
            "last_place": config.MEDIAN_PLACE_DEFAULT,
            "days_since_last_race": 14,
            "last_carried_points": 0,
            "last_scored_points": 0,
            "top3_rate_career": 0,
            "top10_rate_career": 0,
            "series_appearances": 0,
            "is_elite": 1 if "Elite" in category else 0,
            "is_women": 1 if "Women" in category else 0,
            "points_tier": "low",
            "team_tier": "no_team"
        }

        return features, "new_rider"

def predict_race(startlist_path, category="Men Elite", output_path=None):
    """Generate predictions for a race"""

    print("=" * 70)
    print("VELOPREDICT: RACE PREDICTIONS")
    print("=" * 70)

    # Load models and data
    print("\nLoading models and historical data...")
    model_top10, model_top3, metadata = load_models()
    historical_data = load_historical_data()

    print(f"✓ Model loaded (80.2% Top-10 accuracy)")
    print(f"✓ Historical data: {len(historical_data)} observations")

    # Load startlist
    print(f"\nLoading startlist: {startlist_path}")
    startlist = pd.read_csv(startlist_path)
    print(f"✓ Found {len(startlist)} riders")

    # Generate predictions for each rider
    predictions = []

    print(f"\nGenerating predictions for {category}...")
    print("-" * 70)

    for idx, row in startlist.iterrows():
        rider_name = row.get("rider_name", row.get("Naam", row.get("Name")))

        # Get features
        features, status = get_rider_features(rider_name, historical_data, category)

        # Prepare feature vector
        X = pd.DataFrame([features])
        X = pd.get_dummies(X, columns=["points_tier", "team_tier"], drop_first=True)

        # Align with training features
        for feat in metadata['features']:
            if feat not in X.columns:
                X[feat] = 0
        X = X[metadata['features']]

        # Fill any remaining NaN
        X = X.fillna(config.FILL_VALUES)

        # Predict
        top10_prob = model_top10.predict_proba(X)[0][1]
        top3_prob = model_top3.predict_proba(X)[0][1]

        predictions.append({
            "Rider": rider_name,
            "Top-10 Probability": top10_prob,
            "Top-3 Probability": top3_prob,
            "Predicted Finish": "Top-10" if top10_prob > 0.5 else "Outside Top-10",
            "Status": status,
            "Recent Form": features.get("avg_place_last3", "N/A"),
            "Career Top-10 Rate": features.get("top10_rate_career", 0)
        })

        # Print status
        confidence = "🔥 HIGH" if top10_prob > 0.7 else "⚠️  MED" if top10_prob > 0.4 else "   LOW"
        print(f"  {confidence}  {rider_name:30s}  Top-10: {top10_prob:5.1%}  |  Podium: {top3_prob:5.1%}")

    # Sort by Top-10 probability
    df_predictions = pd.DataFrame(predictions).sort_values("Top-10 Probability", ascending=False)

    # Display results
    print("\n" + "=" * 70)
    print("PREDICTED TOP-10 FINISHERS")
    print("=" * 70)

    top10_predictions = df_predictions[df_predictions["Top-10 Probability"] > 0.5]

    for idx, row in top10_predictions.iterrows():
        podium_icon = "🥇" if row["Top-3 Probability"] > 0.5 else "  "
        print(f"{podium_icon} {row['Rider']:30s}  {row['Top-10 Probability']:5.1%} chance")

    print(f"\nTotal predicted Top-10: {len(top10_predictions)} riders")

    # Podium predictions
    print("\n" + "=" * 70)
    print("PREDICTED PODIUM FINISHERS")
    print("=" * 70)

    podium_predictions = df_predictions.nlargest(3, "Top-3 Probability")

    for rank, (idx, row) in enumerate(podium_predictions.iterrows(), 1):
        medal = ["🥇", "🥈", "🥉"][rank-1]
        print(f"{medal} {rank}. {row['Rider']:30s}  {row['Top-3 Probability']:5.1%} chance")

    # Save predictions
    if output_path is None:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
        output_path = config.CLEAN_DIR / f"predictions_{timestamp}.csv"

    df_predictions.to_csv(output_path, index=False)
    print(f"\n✓ Predictions saved to: {output_path}")

    # Summary stats
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Riders analyzed: {len(df_predictions)}")
    print(f"Predicted Top-10: {len(top10_predictions)}")
    print(f"High confidence (>70%): {len(df_predictions[df_predictions['Top-10 Probability'] > 0.7])}")
    print(f"Riders with history: {len(df_predictions[df_predictions['Status'] == 'found'])}")
    print(f"New riders: {len(df_predictions[df_predictions['Status'] == 'new_rider'])}")

    print("\n" + "=" * 70)

    return df_predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict race results")
    parser.add_argument("--startlist", required=True, help="Path to startlist CSV")
    parser.add_argument("--category", default="Men Elite", help="Race category")
    parser.add_argument("--output", help="Output path for predictions")

    args = parser.parse_args()

    predictions = predict_race(args.startlist, args.category, args.output)
