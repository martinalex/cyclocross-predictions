"""
Validate predictions after race
Usage: python validate_predictions.py --predictions data/clean/predictions_tabor_men_elite.csv --results data/results/NEW_RACE.csv
"""
import pandas as pd
import argparse
from pathlib import Path
import unicodedata
import re

def normalize_name(name):
    """Normalize rider name for matching"""
    if pd.isna(name):
        return ""
    # Remove accents
    name = unicodedata.normalize('NFD', str(name))
    name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
    # Lowercase and clean
    name = name.lower().strip()
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)
    return name

def match_names(name1, name2):
    """Check if two names match, considering reversed order"""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)

    if norm1 == norm2:
        return True

    # Try reversed
    parts1 = norm1.split()
    parts2 = norm2.split()

    if len(parts1) >= 2 and len(parts2) >= 2:
        reversed1 = f"{parts1[-1]} {' '.join(parts1[:-1])}"
        reversed2 = f"{parts2[-1]} {' '.join(parts2[:-1])}"

        if reversed1 == norm2 or norm1 == reversed2:
            return True

    return False

def validate_predictions(predictions_path, results_path, category="Men Elite"):
    """Compare predictions against actual results"""

    print("=" * 70)
    print(f"VALIDATING PREDICTIONS: {category}")
    print("=" * 70)

    # Load predictions and results
    predictions = pd.read_csv(predictions_path)
    results = pd.read_csv(results_path)

    # Clean up Name column - remove newlines and extra spaces
    if "Name" in results.columns:
        results["rider_name"] = results["Name"].str.replace("\n", " ").str.strip()
    elif "rider_name" in results.columns:
        results["rider_name"] = results["rider_name"].str.strip()

    # Results file is already category-specific, no filtering needed
    results_category = results.copy()

    # Get actual Top-10 riders
    actual_top10_df = results_category[results_category["Place"] <= 10].copy()
    actual_top10_names = actual_top10_df["rider_name"].tolist()

    # Get predicted Top-10 riders
    predicted_top10_df = predictions[predictions["Predicted Finish"] == "Top-10"].copy()
    predicted_top10_names = predicted_top10_df["Rider"].tolist()

    # Match names using fuzzy matching
    correct_predictions = []
    false_positives = []
    false_negatives = list(actual_top10_names)

    for pred_name in predicted_top10_names:
        matched = False
        for actual_name in actual_top10_names:
            if match_names(pred_name, actual_name):
                correct_predictions.append(actual_name)
                if actual_name in false_negatives:
                    false_negatives.remove(actual_name)
                matched = True
                break
        if not matched:
            false_positives.append(pred_name)

    accuracy = len(correct_predictions) / len(actual_top10_names) if len(actual_top10_names) > 0 else 0
    precision = len(correct_predictions) / len(predicted_top10_names) if len(predicted_top10_names) > 0 else 0

    # Display results
    print(f"\n✅ CORRECT PREDICTIONS ({len(correct_predictions)}):")
    for rider in sorted(correct_predictions):
        actual_place = results_category[results_category["rider_name"] == rider]["Place"].values[0]
        print(f"  ✓ {rider} (P{actual_place})")

    print(f"\n❌ MISSED ({len(false_negatives)}):")
    for rider in sorted(false_negatives):
        actual_place = results_category[results_category["rider_name"] == rider]["Place"].values[0]
        print(f"  ✗ {rider} (finished P{actual_place})")

    print(f"\n⚠️  FALSE POSITIVES ({len(false_positives)}):")
    for pred_rider in sorted(false_positives):
        # Try to find in results with name matching
        found = False
        for actual_rider in results_category["rider_name"].tolist():
            if match_names(pred_rider, actual_rider):
                actual_place = results_category[results_category["rider_name"] == actual_rider]["Place"].values[0]
                print(f"  • {pred_rider} (predicted Top-10, finished P{actual_place})")
                found = True
                break
        if not found:
            print(f"  • {pred_rider} (predicted Top-10, did not start)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Top-10 Accuracy: {accuracy*100:.1f}% ({len(correct_predictions)}/{len(actual_top10_names)})")
    print(f"Precision: {precision*100:.1f}% ({len(correct_predictions)}/{len(predicted_top10_names)})")

    # Podium check
    actual_podium_df = results_category[results_category["Place"] <= 3].sort_values("Place")
    actual_podium_names = actual_podium_df["rider_name"].tolist()

    predicted_podium_df = predictions.nlargest(3, "Top-3 Probability")
    predicted_podium_names = predicted_podium_df["Rider"].tolist()

    podium_hits = 0
    for pred_name in predicted_podium_names:
        for actual_name in actual_podium_names:
            if match_names(pred_name, actual_name):
                podium_hits += 1
                break

    print(f"Podium Accuracy: {podium_hits}/3")
    print(f"\nActual Podium:")
    for idx, rider in enumerate(actual_podium_names, 1):
        print(f"  {idx}. {rider}")

    print(f"\nPredicted Podium:")
    for idx, pred_rider in enumerate(predicted_podium_names, 1):
        matched = False
        for actual_rider in actual_podium_names:
            if match_names(pred_rider, actual_rider):
                matched = True
                break
        status = "✓" if matched else "✗"
        print(f"  {status} {idx}. {pred_rider}")

    print("\n" + "=" * 70)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "podium_hits": podium_hits,
        "correct": len(correct_predictions),
        "missed": len(false_negatives),
        "false_positives": len(false_positives)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate race predictions")
    parser.add_argument("--predictions", required=True, help="Path to predictions CSV")
    parser.add_argument("--results", required=True, help="Path to actual results CSV")
    parser.add_argument("--category", default="Men Elite", help="Race category")

    args = parser.parse_args()

    metrics = validate_predictions(args.predictions, args.results, args.category)

    print(f"\n✅ Validation complete!")
    print(f"   Save these metrics for your LinkedIn post!")
