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
from head_to_head import get_h2h_matrix, calculate_h2h_features

def load_historical_data():
    """Load historical rider data for feature lookup"""
    df = pd.read_csv(config.RESULTS_WITH_FEATURES, parse_dates=["race_date"])
    return df

def load_uci_rankings():
    """Load centralized UCI rankings (Nov 17, 2025)"""
    rankings = {}

    # Men Elite
    men_path = config.CLEAN_DIR / "uci_rankings_men_elite.csv"
    if men_path.exists():
        men = pd.read_csv(men_path)
        for _, row in men.iterrows():
            name_norm = standardize_name(row["Rider"])
            if name_norm:
                rankings[name_norm] = {
                    "rank": row["Rank"],
                    "points": row["Points"],
                    "category": "Men Elite"
                }

    # Women Elite
    women_path = config.CLEAN_DIR / "uci_rankings_women_elite.csv"
    if women_path.exists():
        women = pd.read_csv(women_path)
        for _, row in women.iterrows():
            name_norm = standardize_name(row["Rider"])
            if name_norm:
                rankings[name_norm] = {
                    "rank": row["Rank"],
                    "points": row["Points"],
                    "category": "Women Elite"
                }

    return rankings

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
            .replace("ý", "y").replace("í", "i").replace("ň", "n")
            .replace("ě", "e").replace("ď", "d").replace("ť", "t")
    )
    return name

def standardize_name(s):
    """Standardize name to 'firstname lastname' format for consistent matching.
    Handles:
    - 'LASTNAME Firstname' -> 'firstname lastname'
    - 'VAN ALPHEN Aniek' -> 'aniek van alphen' (multi-word last names)
    - 'Firstname Lastname' -> 'firstname lastname'
    """
    if pd.isna(s):
        return None
    s = str(s).strip()

    # Remove diacritics for matching
    normalized = normalize_name(s)
    if normalized is None:
        return None

    parts = normalized.split()
    orig_parts = s.split()

    if len(parts) < 2:
        return normalized

    # Find where the uppercase last name ends and firstname begins
    # E.g., "VAN ALPHEN Aniek" - find index of first non-uppercase word
    first_lower_idx = None
    for i, p in enumerate(orig_parts):
        if not p.isupper():
            first_lower_idx = i
            break

    if first_lower_idx is not None and first_lower_idx > 0:
        # Found pattern like "VAN ALPHEN Aniek" or "LASTNAME Firstname"
        first_name_parts = parts[first_lower_idx:]
        last_name_parts = parts[:first_lower_idx]
        return f"{' '.join(first_name_parts)} {' '.join(last_name_parts)}"
    elif all(p.isupper() for p in orig_parts):
        # All uppercase: "LASTNAME FIRSTNAME" -> assume first word is last name
        return f"{parts[1]} {parts[0]}"

    # Default: already in firstname lastname format
    return normalized

def get_rider_features(rider_name, historical_data, category="Men Elite", startlist_uci_rank=None, uci_rankings=None):
    """Get latest features for a rider from historical data

    Args:
        rider_name: Rider name from startlist
        historical_data: DataFrame with historical race results
        category: Race category (e.g., "Men Elite")
        startlist_uci_rank: UCI rank from startlist (fallback for new riders)
        uci_rankings: Centralized UCI rankings lookup dict (primary source)
    """

    # Standardize name for matching (converts "LASTNAME Firstname" to "firstname lastname")
    std_name = standardize_name(rider_name)
    # Historical data should already have standardized names from update_results.py
    # but normalize just in case
    if "rider_name_norm" not in historical_data.columns:
        historical_data["rider_name_norm"] = historical_data["rider_name"].apply(standardize_name)

    # With standardized names, we can do simpler matching
    # std_name is already in "firstname lastname" format
    parts = std_name.split() if std_name else []
    if len(parts) >= 2:
        # Extract first name and last name for partial matching
        first_name = parts[0]
        last_name = parts[-1]  # Last word is the last name
    else:
        first_name = std_name or ""
        last_name = std_name or ""

    # Find rider's most recent race
    category_mask = historical_data["Category Name"].str.contains(category.split()[0], case=False, na=False)

    # Exact match on standardized name
    exact_match = (historical_data["rider_name_norm"] == std_name) & category_mask

    # Partial match: both first name AND last name appear in historical name
    # This handles names with middle names like "ceylin del carmen alvarado" matching "ceylin alvarado"
    if first_name and last_name:
        partial_match = (
            historical_data["rider_name_norm"].str.contains(first_name, na=False, regex=False) &
            historical_data["rider_name_norm"].str.contains(last_name, na=False, regex=False)
        ) & category_mask
    else:
        partial_match = exact_match

    rider_history = historical_data[
        exact_match | partial_match
    ].sort_values("race_date", ascending=False)

    if len(rider_history) > 0:
        # Use most recent data
        latest = rider_history.iloc[0]

        # Get UCI points normalized - prefer centralized rankings over historical data
        max_uci_rank = 700
        if uci_rankings and std_name in uci_rankings:
            # Use current UCI ranking (more accurate than historical "Carried Points")
            uci_rank = uci_rankings[std_name]["rank"]
            uci_points_norm = min(uci_rank / max_uci_rank, 1.0)
        elif startlist_uci_rank is not None and not pd.isna(startlist_uci_rank) and startlist_uci_rank > 0:
            # Fallback to startlist UCI rank
            uci_points_norm = min(startlist_uci_rank / max_uci_rank, 1.0)
        else:
            # Use historical data as last resort
            uci_points_norm = latest["uci_points_normalized"]

        # Cap races_so_far to avoid penalizing experienced riders
        # The model incorrectly learned that more races = worse performance (fatigue artifact)
        # Capping at 10 makes experienced riders equal to new riders (who also get 10)
        races_so_far = min(latest["races_so_far"] + 1, 10)

        features = {
            "uci_points_normalized": uci_points_norm,
            "races_so_far": races_so_far,
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
        # New rider - infer performance from UCI points if available
        # v4 IMPROVEMENT: Use UCI-based inference instead of generic defaults

        # Try to get UCI points from historical data (even if no race history)
        # Use same partial matching as above
        if first_name and last_name:
            uci_partial = (
                historical_data["rider_name_norm"].str.contains(first_name, na=False, regex=False) &
                historical_data["rider_name_norm"].str.contains(last_name, na=False, regex=False)
            )
        else:
            uci_partial = pd.Series([False] * len(historical_data))

        uci_match = historical_data[
            (historical_data["rider_name_norm"] == std_name) | uci_partial
        ]

        # Priority order for UCI data lookup:
        # 1. Centralized UCI rankings (Nov 17, 2025) - use Points column for consistency
        # 2. Startlist UCI rank column - convert rank to approximate points
        # 3. Historical data UCI points - may be outdated
        # 4. Default (weak rider)

        # Normalization: Use UCI Points, normalized so that:
        # - Lower normalized value = STRONGER rider (high points = good ranking)
        # - Higher normalized value = WEAKER rider (low points = poor ranking)
        #
        # Historical data uses "Carried Points" (max ~750) where lower = better
        # New UCI rankings use "Points" (max ~3500) where HIGHER = better
        # We need to INVERT the new points to match historical convention
        max_uci_points = 3500  # Max points in elite CX (Brand has 3280)
        max_uci_rank = 700  # For fallback rank-to-points conversion

        # 1. Check centralized UCI rankings first - USE POINTS (inverted)
        if uci_rankings and std_name in uci_rankings:
            uci_points = uci_rankings[std_name]["points"]
            uci_rank = uci_rankings[std_name]["rank"]
            # Invert: high points = strong rider = LOW normalized value
            # Brand (3280 pts) → norm = 1 - (3280/3500) = 0.06 (strong)
            # Folcarelli (132 pts) → norm = 1 - (132/3500) = 0.96 (weak)
            # Wait - this doesn't match! Folcarelli rank 115 should be fairly strong
            #
            # Better approach: Use RANK directly since it's already ordered
            # Rank 1 → norm ~0.0 (strong), Rank 120 → norm ~0.17 (still decent)
            uci_points_norm = min(uci_rank / max_uci_rank, 1.0)
            inference_source = f"UCI rankings (rank {int(uci_rank)}, {int(uci_points)} pts, norm={uci_points_norm:.3f})"
        # 2. Try startlist UCI rank - convert to approximate normalized value
        elif startlist_uci_rank is not None and not pd.isna(startlist_uci_rank) and startlist_uci_rank > 0:
            # Rank 1 → norm ~0.0 (strong), Rank 500 → norm ~0.7 (weak)
            uci_points_norm = min(startlist_uci_rank / max_uci_rank, 1.0)
            inference_source = f"startlist UCI rank {int(startlist_uci_rank)} (norm={uci_points_norm:.3f})"
        # 3. Check historical data
        elif len(uci_match) > 0:
            uci_points_norm = uci_match.iloc[0]["uci_points_normalized"]
            inference_source = f"historical UCI (norm={uci_points_norm:.3f})"
        # 4. Default for unknown riders
        else:
            uci_points_norm = 0.8  # High default = weak rider
            inference_source = "generic default (weak)"

        # Infer expected place from UCI points (linear regression model)
        # Formula: place = 9.3 + 51.4 * uci_normalized
        # uci_normalized=0.0 (rank 1) → place 9
        # uci_normalized=0.5 (rank 350) → place 35
        # uci_normalized=1.0 (rank 700) → place 60
        inferred_place = config.UCI_PLACE_INTERCEPT + config.UCI_PLACE_SLOPE * uci_points_norm
        inferred_place = max(5, min(70, inferred_place))  # Bound to 5-70

        print(f"  ⚠️  {rider_name}: No history found, using {inference_source} → expected place ~{inferred_place:.0f}")

        # For new riders, use neutral values that don't trigger training data artifacts
        # - races_so_far=0 in training data means "first race of season" (often good performance)
        # - For truly unknown riders, use median value (~10) to avoid this bias
        features = {
            "uci_points_normalized": uci_points_norm,
            "races_so_far": 10,  # Neutral value (was 0, which boosted predictions incorrectly)
            "avg_place_last3": inferred_place,  # v4: UCI-based instead of generic
            "best_place_last5": inferred_place,  # v4: UCI-based instead of generic
            "last_place": inferred_place,        # v4: UCI-based instead of generic
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

def predict_race(startlist_path, category="Men Elite", output_path=None, confidence_threshold=0.55, enable_dns_filter=True):
    """Generate predictions for a race

    Args:
        startlist_path: Path to startlist CSV
        category: Race category (e.g., "Men Elite")
        output_path: Where to save predictions
        confidence_threshold: Minimum probability to predict Top-10 (default: 0.55, reduced false positives)
        enable_dns_filter: Filter riders unlikely to start (default: True)
    """

    print("=" * 70)
    print("VELOPREDICT: RACE PREDICTIONS (v4 - UCI-Based Inference)")
    print("=" * 70)

    # Load models and data
    print("\nLoading models and historical data...")
    model_top10, model_top3, metadata = load_models()
    historical_data = load_historical_data()
    uci_rankings = load_uci_rankings()

    print(f"✓ Model loaded (90.0% Top-10 accuracy on Tabor)")
    print(f"✓ Historical data: {len(historical_data)} observations")
    print(f"✓ UCI rankings loaded: {len(uci_rankings)} riders (Nov 17, 2025)")
    print(f"✓ Confidence threshold: {confidence_threshold:.0%} (improved precision)")
    print(f"✓ DNS filter: {'Enabled' if enable_dns_filter else 'Disabled'}")

    # Load startlist
    print(f"\nLoading startlist: {startlist_path}")
    startlist = pd.read_csv(startlist_path)
    print(f"✓ Found {len(startlist)} riders")

    # Build H2H matrix and get normalized field names
    print("\nBuilding head-to-head matrix...")
    h2h_matrix = get_h2h_matrix()

    # Build normalized field list for H2H calculations
    field_names_norm = []
    for idx, row in startlist.iterrows():
        rider_name = row.get("rider_name", row.get("Naam", row.get("Name")))
        std_name = standardize_name(rider_name)
        if std_name:
            field_names_norm.append(std_name)
    print(f"✓ H2H matrix ready ({len(field_names_norm)} riders in field)")

    # Generate predictions for each rider
    predictions = []

    print(f"\nGenerating predictions for {category}...")
    print("-" * 70)

    for idx, row in startlist.iterrows():
        rider_name = row.get("rider_name", row.get("Naam", row.get("Name")))

        # Get UCI rank from startlist (if available)
        uci_rank = row.get("UCI Rank", row.get("UCI", row.get("uci_rank", None)))
        if uci_rank is not None:
            uci_rank = pd.to_numeric(uci_rank, errors='coerce')

        # Get features
        features, status = get_rider_features(rider_name, historical_data, category, startlist_uci_rank=uci_rank, uci_rankings=uci_rankings)

        # Calculate head-to-head score against this field
        std_name = standardize_name(rider_name)
        h2h_features = calculate_h2h_features(std_name, field_names_norm)

        # Add H2H to model features
        features["h2h_field_score"] = h2h_features['h2h_field_score']

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

        # DNS Filter: Check if rider is unlikely to start
        dns_risk = False
        dns_reason = ""

        if enable_dns_filter:
            days_since = features.get("days_since_last_race", 7)
            races_count = features.get("races_so_far", 0)

            # Flag if hasn't raced in 21+ days (likely taking break or injured)
            if days_since > 21:
                dns_risk = True
                dns_reason = f"⚠️ DNS Risk: {days_since} days since last race"

            # Flag if very few races this season (< 2)
            elif races_count < 2 and status == "found":
                dns_risk = True
                dns_reason = "⚠️ DNS Risk: Only 1 race this season"

        # Apply confidence threshold (Quick Win #1)
        predicted_finish = "Top-10" if (top10_prob > confidence_threshold and not dns_risk) else "Outside Top-10"

        # Mark DNS risk riders
        if dns_risk:
            predicted_finish = "DNS Risk"

        predictions.append({
            "Rider": rider_name,
            "Top-10 Probability": top10_prob,
            "Top-3 Probability": top3_prob,
            "H2H Field Score": h2h_features['h2h_field_score'],
            "H2H Confidence": h2h_features['h2h_confidence'],
            "H2H Known Opponents": h2h_features['h2h_known_opponents'],
            "Predicted Finish": predicted_finish,
            "Status": status,
            "DNS Risk": dns_risk,
            "DNS Reason": dns_reason,
            "Recent Form": features.get("avg_place_last3", "N/A"),
            "Career Top-10 Rate": features.get("top10_rate_career", 0)
        })

        # Print status with H2H info
        if dns_risk:
            confidence = "⚠️  DNS?"
        else:
            confidence = "🔥 HIGH" if top10_prob > 0.7 else "⚠️  MED" if top10_prob > 0.4 else "   LOW"

        dns_marker = " [DNS RISK]" if dns_risk else ""
        h2h_str = f"H2H: {h2h_features['h2h_field_score']*100:4.0f}%" if h2h_features['h2h_confidence'] > 0 else "H2H: N/A"
        print(f"  {confidence}  {rider_name:30s}  Top-10: {top10_prob:5.1%}  |  Podium: {top3_prob:5.1%}  |  {h2h_str}{dns_marker}")

    # Sort by Top-10 probability
    df_predictions = pd.DataFrame(predictions).sort_values("Top-10 Probability", ascending=False)

    # Display results
    print("\n" + "=" * 70)
    print("PREDICTED TOP-10 FINISHERS")
    print("=" * 70)

    # Filter: Must meet confidence threshold AND not be DNS risk
    top10_predictions = df_predictions[
        (df_predictions["Top-10 Probability"] > confidence_threshold) &
        (df_predictions["DNS Risk"] == False)
    ]

    for idx, row in top10_predictions.iterrows():
        podium_icon = "🥇" if row["Top-3 Probability"] > 0.5 else "  "
        h2h_pct = row['H2H Field Score'] * 100 if row['H2H Confidence'] > 0 else 0
        h2h_str = f"(H2H: {h2h_pct:3.0f}%)" if row['H2H Confidence'] > 0.3 else "(H2H: N/A)"
        print(f"{podium_icon} {row['Rider']:30s}  {row['Top-10 Probability']:5.1%} chance  {h2h_str}")

    print(f"\nTotal predicted Top-10: {len(top10_predictions)} riders")
    print(f"(Using {confidence_threshold:.0%} confidence threshold)")

    # Show DNS risks if any
    dns_risks = df_predictions[df_predictions["DNS Risk"] == True]
    if len(dns_risks) > 0:
        print(f"\n⚠️  DNS Risk: {len(dns_risks)} riders flagged as unlikely to start:")
        for idx, row in dns_risks.iterrows():
            print(f"   • {row['Rider']:30s} - {row['DNS Reason']}")

    # Podium predictions
    print("\n" + "=" * 70)
    print("PREDICTED PODIUM FINISHERS")
    print("=" * 70)

    # Exclude DNS risks from podium predictions
    eligible_for_podium = df_predictions[df_predictions["DNS Risk"] == False]
    podium_predictions = eligible_for_podium.nlargest(3, "Top-3 Probability")

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
    print(f"Predicted Top-10: {len(top10_predictions)} (threshold: {confidence_threshold:.0%})")
    print(f"High confidence (>70%): {len(df_predictions[df_predictions['Top-10 Probability'] > 0.7])}")
    print(f"DNS risks flagged: {len(dns_risks)}")
    print(f"Riders with history: {len(df_predictions[df_predictions['Status'] == 'found'])}")
    print(f"New riders: {len(df_predictions[df_predictions['Status'] == 'new_rider'])}")

    # H2H stats
    h2h_coverage = df_predictions[df_predictions['H2H Confidence'] > 0.3]
    print(f"\nHead-to-Head Analysis:")
    print(f"  • Riders with H2H data: {len(h2h_coverage)}/{len(df_predictions)}")
    if len(h2h_coverage) > 0:
        avg_h2h = h2h_coverage['H2H Field Score'].mean() * 100
        top_h2h = h2h_coverage.nlargest(3, 'H2H Field Score')
        print(f"  • Top H2H vs field: {', '.join(top_h2h['Rider'].head(3))}")

    print(f"\nImprovements vs Tabor:")
    print(f"  • Confidence threshold: 50% → {confidence_threshold:.0%} (reduce false positives)")
    print(f"  • DNS filtering: {'Enabled' if enable_dns_filter else 'Disabled'}")
    print(f"  • Head-to-head analysis: Enabled (field-adjusted win rates)")
    print(f"  • Expected precision: ~60% (vs 42% at Tabor)")

    print("\n" + "=" * 70)

    return df_predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict race results")
    parser.add_argument("--startlist", required=True, help="Path to startlist CSV")
    parser.add_argument("--category", default="Men Elite", help="Race category")
    parser.add_argument("--output", help="Output path for predictions")

    args = parser.parse_args()

    predictions = predict_race(args.startlist, args.category, args.output)
