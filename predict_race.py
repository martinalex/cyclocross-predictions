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
from src.features.builder import FeatureBuilder


def load_models():
    """Load trained models"""
    model_top10 = joblib.load(config.TOP10_MODEL)
    model_top3 = joblib.load(config.TOP3_MODEL)

    with open(config.MODEL_METADATA, 'r') as f:
        metadata = json.load(f)

    return model_top10, model_top3, metadata


def predict_race(
    startlist_path,
    category="Men Elite",
    output_path=None,
    confidence_threshold=None,
    enable_dns_filter=False
):
    """Generate predictions for a race

    Args:
        startlist_path: Path to startlist CSV
        category: Race category (e.g., "Men Elite")
        output_path: Where to save predictions
        confidence_threshold: Minimum probability to predict Top-10 (default from config)
        enable_dns_filter: DEPRECATED - DNS filter disabled by default (was causing false flags on elite riders)
    """
    # Use config default if not specified
    if confidence_threshold is None:
        confidence_threshold = config.CONFIDENCE_THRESHOLD

    print("=" * 70)
    print("VELOPREDICT: RACE PREDICTIONS (v6 - Unified FeatureBuilder)")
    print("=" * 70)

    # Load models and initialize FeatureBuilder
    print("\nLoading models and data...")
    model_top10, model_top3, metadata = load_models()
    builder = FeatureBuilder(load_h2h=True)

    print(f"Model loaded ({metadata['top10_accuracy']*100:.1f}% Top-10 accuracy)")
    print(f"Historical data: {len(builder.historical_data)} observations")
    print(f"UCI rankings loaded: {len(builder.uci_rankings)} riders")
    print(f"Confidence threshold: {confidence_threshold:.0%}")
    print(f"DNS filter: {'Enabled' if enable_dns_filter else 'Disabled'}")

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

        # Print new rider info
        if rider_features.is_new_rider and rider_features.inference_source:
            print(f"  New rider: {rider_name} - {rider_features.inference_source}")

        # Prepare model input
        X = builder.prepare_model_input(rider_features)

        # Predict
        top10_prob = model_top10.predict_proba(X)[0][1]
        top3_prob = model_top3.predict_proba(X)[0][1]

        # Apply new rider discount
        if rider_features.is_new_rider:
            top10_prob *= config.NEW_RIDER_DISCOUNT
            top3_prob *= config.NEW_RIDER_DISCOUNT

        # Check DNS risk
        dns_risk = False
        dns_reason = ""
        if enable_dns_filter:
            dns_risk, dns_reason = builder.check_dns_risk(rider_features)

        # Determine prediction
        if dns_risk:
            predicted_finish = "DNS Risk"
        elif top10_prob > confidence_threshold:
            predicted_finish = "Top-10"
        else:
            predicted_finish = "Outside Top-10"

        # Get H2H info
        h2h_score = rider_features.features.get("h2h_field_score", 0.5)
        h2h_confidence = getattr(rider_features, 'h2h_confidence', 0.0)
        h2h_known = getattr(rider_features, 'h2h_known_opponents', 0)

        predictions.append({
            "Rider": rider_name,
            "Top-10 Probability": top10_prob,
            "Top-3 Probability": top3_prob,
            "H2H Field Score": h2h_score,
            "H2H Confidence": h2h_confidence,
            "H2H Known Opponents": h2h_known,
            "Predicted Finish": predicted_finish,
            "Status": rider_features.status,
            "DNS Risk": dns_risk,
            "DNS Reason": dns_reason,
            "Recent Form": rider_features.features.get("avg_place_last3", "N/A"),
            "Career Top-10 Rate": rider_features.features.get("top10_rate_career", 0)
        })

        # Print status
        if dns_risk:
            confidence = "  DNS?"
        else:
            confidence = " HIGH" if top10_prob > 0.7 else "  MED" if top10_prob > 0.4 else "  LOW"

        dns_marker = " [DNS RISK]" if dns_risk else ""
        h2h_str = f"H2H: {h2h_score*100:4.0f}%" if h2h_confidence > 0 else "H2H: N/A"
        print(f"  {confidence}  {rider_name:30s}  Top-10: {top10_prob:5.1%}  |  Podium: {top3_prob:5.1%}  |  {h2h_str}{dns_marker}")

    # Sort by Top-10 probability and add Predicted Rank
    df_predictions = pd.DataFrame(predictions).sort_values("Top-10 Probability", ascending=False)
    df_predictions['Predicted Rank'] = range(1, len(df_predictions) + 1)

    # Display results - ALWAYS predict exactly 10 riders (v6.4+ methodology)
    print("\n" + "=" * 70)
    print("PREDICTED TOP-10 FINISHERS")
    print("=" * 70)

    # Always take top 10 by probability, regardless of threshold
    eligible = df_predictions[df_predictions["DNS Risk"] == False]
    top10_predictions = eligible.nlargest(10, "Top-10 Probability")

    for rank, (idx, row) in enumerate(top10_predictions.iterrows(), 1):
        h2h_pct = row['H2H Field Score'] * 100 if row['H2H Confidence'] > 0 else 0
        h2h_str = f"(H2H: {h2h_pct:3.0f}%)" if row['H2H Confidence'] > 0.3 else "(H2H: N/A)"
        print(f"   {rank:2d}. {row['Rider']:30s}  {row['Top-10 Probability']:5.1%} chance  {h2h_str}")

    print(f"\nPredicted Top-10: 10 riders (fixed N=10, v6.4+ methodology)")

    # Show DNS risks
    dns_risks = df_predictions[df_predictions["DNS Risk"] == True]
    if len(dns_risks) > 0:
        print(f"\n  DNS Risk: {len(dns_risks)} riders flagged as unlikely to start:")
        for idx, row in dns_risks.iterrows():
            print(f"   - {row['Rider']:30s} - {row['DNS Reason']}")

    # Podium predictions
    print("\n" + "=" * 70)
    print("PREDICTED PODIUM FINISHERS")
    print("=" * 70)

    eligible_for_podium = df_predictions[
        (df_predictions["DNS Risk"] == False) &
        (df_predictions["Top-3 Probability"] >= config.PODIUM_THRESHOLD)
    ]

    podium_predictions = eligible_for_podium.nlargest(3, "Top-3 Probability")

    if len(podium_predictions) == 0:
        print(f"No riders meet podium prediction threshold ({config.PODIUM_THRESHOLD:.0%})")
        print("Top 3 by probability shown for reference:")
        reference = df_predictions[df_predictions["DNS Risk"] == False].nlargest(3, "Top-3 Probability")
        for rank, (idx, row) in enumerate(reference.iterrows(), 1):
            print(f"   {rank}. {row['Rider']:30s}  {row['Top-3 Probability']:5.1%} (below threshold)")
    else:
        medals = ["1.", "2.", "3."]
        for rank, (idx, row) in enumerate(podium_predictions.iterrows(), 1):
            new_rider_flag = " (new rider)" if row["Status"] == "new_rider" else ""
            print(f"{medals[rank-1]} {row['Rider']:30s}  {row['Top-3 Probability']:5.1%} chance{new_rider_flag}")

        if len(podium_predictions) < 3:
            print(f"\n   Only {len(podium_predictions)} rider(s) meet the {config.PODIUM_THRESHOLD:.0%} podium threshold")

    # Save predictions
    if output_path is None:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
        output_path = config.CLEAN_DIR / f"predictions_{timestamp}.csv"

    df_predictions.to_csv(output_path, index=False)
    print(f"\nPredictions saved to: {output_path}")

    # Probability Distribution Analysis (v6.4+ methodology)
    print("\n" + "=" * 70)
    print("PROBABILITY DISTRIBUTION ANALYSIS")
    print("=" * 70)

    probs = df_predictions['Top-10 Probability']
    field_size = len(df_predictions)

    low_count = len(probs[probs < 0.30])
    mid_count = len(probs[(probs >= 0.30) & (probs < 0.60)])
    high_count = len(probs[probs >= 0.60])

    low_pct = low_count / field_size * 100
    mid_pct = mid_count / field_size * 100
    high_pct = high_count / field_size * 100

    mean_prob = probs.mean()
    std_prob = probs.std()

    new_riders = len(df_predictions[df_predictions['Status'] == 'new_rider'])

    # Determine pattern
    if mid_pct < 10:
        pattern = "BIMODAL"
        pattern_desc = "Model is decisive - clear separation between contenders and non-contenders"
    elif mid_pct > 20:
        pattern = "BALANCED"
        pattern_desc = "Model is uncertain - many riders in competitive range"
    else:
        pattern = "MODERATE"
        pattern_desc = "Typical distribution with some uncertainty"

    print(f"| Metric           | Value  | Interpretation        |")
    print(f"|------------------|-------:|----------------------|")
    print(f"| Low (<30%)       | {low_pct:5.1f}% | Non-contenders        |")
    print(f"| Mid (30-60%)     | {mid_pct:5.1f}% | Uncertain zone        |")
    print(f"| High (>60%)      | {high_pct:5.1f}% | Likely contenders     |")
    print(f"| Mean Probability | {mean_prob*100:5.1f}% | Average across field  |")
    print(f"| Std Deviation    | {std_prob:.3f} | Probability spread    |")
    print(f"| New Riders       | {new_riders:5d} | No prior race history |")
    print(f"| Field Size       | {field_size:5d} | Total riders          |")
    print(f"\nPattern: {pattern}")
    print(f"  {pattern_desc}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Riders analyzed: {len(df_predictions)}")
    print(f"Predicted Top-10: 10 (fixed N=10)")
    print(f"High confidence (>70%): {len(df_predictions[df_predictions['Top-10 Probability'] > 0.7])}")
    print(f"DNS risks flagged: {len(dns_risks)}")
    print(f"Riders with history: {len(df_predictions[df_predictions['Status'] == 'found'])}")
    print(f"New riders: {new_riders}")

    # H2H stats
    h2h_coverage = df_predictions[df_predictions['H2H Confidence'] > 0.3]
    print(f"\nHead-to-Head Analysis:")
    print(f"  - Riders with H2H data: {len(h2h_coverage)}/{len(df_predictions)}")
    if len(h2h_coverage) > 0:
        top_h2h = h2h_coverage.nlargest(3, 'H2H Field Score')
        print(f"  - Top H2H vs field: {', '.join(top_h2h['Rider'].head(3))}")

    print("\n" + "=" * 70)

    return df_predictions, {
        'low_pct': low_pct,
        'mid_pct': mid_pct,
        'high_pct': high_pct,
        'mean_prob': mean_prob,
        'std_prob': std_prob,
        'new_rider_count': new_riders,
        'field_size': field_size,
        'pattern': pattern
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict race results")
    parser.add_argument("--startlist", required=True, help="Path to startlist CSV")
    parser.add_argument("--category", default="Men Elite", help="Race category")
    parser.add_argument("--output", help="Output path for predictions")
    parser.add_argument("--threshold", type=float, help="Confidence threshold (default from config)")
    parser.add_argument("--narrative", action="store_true", help="Generate LLM narrative (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--race-name", default="Race", help="Race name for narrative")

    args = parser.parse_args()

    predictions, distribution = predict_race(
        args.startlist,
        args.category,
        args.output,
        confidence_threshold=args.threshold
    )

    # Generate LLM narrative if requested
    if args.narrative:
        print("\n" + "=" * 70)
        print("AI RACE ANALYSIS (powered by Claude)")
        print("=" * 70)

        try:
            from src.llm.narratives import explain_predictions

            narratives = explain_predictions(predictions, args.race_name)

            print("\n### RACE PREVIEW ###")
            print(narratives["race_preview"])

            print("\n### PODIUM PREDICTION ###")
            print(narratives["podium_prediction"])

            print("\n### TOP RIDER INSIGHTS ###")
            for item in narratives["top_insights"]:
                print(f"\n{item['rider']}:")
                print(f"  {item['insight']}")

        except ValueError as e:
            print(f"\nError: {e}")
            print("Set ANTHROPIC_API_KEY to enable narrative generation.")
        except Exception as e:
            print(f"\nError generating narrative: {e}")
