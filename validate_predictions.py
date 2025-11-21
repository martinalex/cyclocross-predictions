"""
Validate predictions after race
Usage: python validate_predictions.py --predictions data/clean/predictions_tabor_men_elite.csv --results data/results/NEW_RACE.csv
"""
import pandas as pd
import argparse
from pathlib import Path

def validate_predictions(predictions_path, results_path, category="Men Elite"):
    """Compare predictions against actual results"""

    print("=" * 70)
    print(f"VALIDATING PREDICTIONS: {category}")
    print("=" * 70)

    # Load predictions and results
    predictions = pd.read_csv(predictions_path)
    results = pd.read_csv(results_path)

    # Filter results to category
    results_category = results[results["Category Name"].str.contains(category.split()[0], case=False, na=False)]

    # Get actual Top-10
    actual_top10 = set(results_category[results_category["Place"] <= 10]["rider_name"].str.lower().str.strip())

    # Get predicted Top-10
    predicted_top10 = set(
        predictions[predictions["Predicted Finish"] == "Top-10"]["Rider"].str.lower().str.strip()
    )

    # Calculate accuracy
    correct_predictions = actual_top10 & predicted_top10
    false_positives = predicted_top10 - actual_top10
    false_negatives = actual_top10 - predicted_top10

    accuracy = len(correct_predictions) / len(actual_top10) if len(actual_top10) > 0 else 0
    precision = len(correct_predictions) / len(predicted_top10) if len(predicted_top10) > 0 else 0

    # Display results
    print(f"\n✅ CORRECT PREDICTIONS ({len(correct_predictions)}):")
    for rider in sorted(correct_predictions):
        print(f"  ✓ {rider.title()}")

    print(f"\n❌ MISSED ({len(false_negatives)}):")
    for rider in sorted(false_negatives):
        actual_place = results_category[results_category["rider_name"].str.lower() == rider]["Place"].values[0]
        print(f"  ✗ {rider.title()} (finished {actual_place})")

    print(f"\n⚠️  FALSE POSITIVES ({len(false_positives)}):")
    for rider in sorted(false_positives):
        if rider in results_category["rider_name"].str.lower().values:
            actual_place = results_category[results_category["rider_name"].str.lower() == rider]["Place"].values[0]
            print(f"  • {rider.title()} (predicted Top-10, finished {actual_place})")
        else:
            print(f"  • {rider.title()} (predicted Top-10, did not finish)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Top-10 Accuracy: {accuracy*100:.1f}% ({len(correct_predictions)}/{len(actual_top10)})")
    print(f"Precision: {precision*100:.1f}% ({len(correct_predictions)}/{len(predicted_top10)})")

    # Podium check
    actual_podium = set(results_category[results_category["Place"] <= 3]["rider_name"].str.lower().str.strip())
    predicted_podium_riders = predictions.nlargest(3, "Top-3 Probability")["Rider"].str.lower().str.strip().tolist()

    podium_hits = sum(1 for r in predicted_podium_riders if r in actual_podium)

    print(f"Podium Accuracy: {podium_hits}/3")
    print(f"\nActual Podium:")
    for idx, rider in enumerate(sorted(actual_podium), 1):
        print(f"  {idx}. {rider.title()}")

    print(f"\nPredicted Podium:")
    for idx, rider in enumerate(predicted_podium_riders, 1):
        status = "✓" if rider in actual_podium else "✗"
        print(f"  {status} {idx}. {rider.title()}")

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
