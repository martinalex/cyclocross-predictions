#!/usr/bin/env python3
"""
VeloPredict Automated Pipeline

Single entry point for all race prediction workflows:
- predict: Generate predictions from a startlist
- add-results: Add new race results to training data
- retrain: Rebuild features and retrain model
- validate: Compare predictions to actual results
- full: Run complete post-race workflow (add-results → retrain → validate)

Usage:
    python pipeline.py predict data/startlists/namur_men_elite_2025-12-14.csv
    python pipeline.py add-results data/results/Results__UCI-World-Cup__Namur__Men-Elite__2025-12-14.csv
    python pipeline.py retrain
    python pipeline.py validate --race namur --date 2025-12-14
    python pipeline.py full data/results/Results__UCI-World-Cup__Namur__Men-Elite__2025-12-14.csv
"""
import argparse
import sys
import re
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

import config
from src.features.names import standardize_name, normalize_name


# ============================================================
# RACE REGISTRY MANAGEMENT
# ============================================================

REGISTRY_PATH = config.CLEAN_DIR / "race_registry.json"


def load_registry() -> dict:
    """Load race registry from JSON file."""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    return {"races": [], "model_versions": [], "current_version": "v1"}


def save_registry(registry: dict):
    """Save race registry to JSON file."""
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)


def register_race(
    race_id: str,
    name: str,
    date: str,
    series: str,
    category: str,
    predictions_path: str,
    results_path: str = None,
    version: str = None,
    threshold: float = None
):
    """
    Register a new race in the registry.

    Called automatically by predict() and add_results().
    """
    registry = load_registry()

    if threshold is None:
        threshold = config.CONFIDENCE_THRESHOLD
    if version is None:
        version = registry.get("current_version", "v1")

    # Find or create race entry
    existing = next((r for r in registry["races"] if r["id"] == race_id), None)

    if existing:
        # Update existing race
        if predictions_path:
            existing["predictions"][category] = predictions_path
        if results_path:
            existing["results"][category] = results_path
    else:
        # Create new race entry
        new_race = {
            "id": race_id,
            "name": name,
            "date": date,
            "series": series,
            "version": version,
            "threshold": threshold,
            "predictions": {category: predictions_path} if predictions_path else {},
            "results": {category: results_path} if results_path else {}
        }
        registry["races"].append(new_race)

    save_registry(registry)
    print(f"  Registered race: {race_id} ({category})")


def update_model_version(version: str, accuracy: float, auc: float, observations: int, innovation: str):
    """Register a new model version after training."""
    registry = load_registry()

    # Check if version exists
    existing = next((v for v in registry["model_versions"] if v["version"] == version), None)

    if existing:
        existing["accuracy"] = accuracy
        existing["auc"] = auc
        existing["observations"] = observations
    else:
        registry["model_versions"].append({
            "version": version,
            "accuracy": accuracy,
            "auc": auc,
            "observations": observations,
            "innovation": innovation
        })

    registry["current_version"] = version
    save_registry(registry)


# ============================================================
# REPORT GENERATION
# ============================================================

def _generate_category_section(predictions_df: pd.DataFrame, category: str, threshold: float) -> list:
    """Generate markdown lines for a single category's predictions."""
    lines = []

    # Filter predictions
    top10_preds = predictions_df[
        (predictions_df["Top-10 Probability"] >= threshold) &
        (predictions_df["DNS Risk"] == False)
    ].sort_values("Top-10 Probability", ascending=False)

    high_conf = predictions_df[predictions_df["Top-10 Probability"] >= 0.70]

    # Calculate max rider name length for alignment (including ** markers)
    max_name_len = max(len(row['Rider']) + (4 if row['Top-10 Probability'] >= 0.70 else 0)
                       for _, row in top10_preds.iterrows()) if len(top10_preds) > 0 else 20

    lines.extend([
        f"## {category}",
        f"",
        f"**{len(predictions_df)} riders** | {len(top10_preds)} predicted Top-10 | {len(high_conf)} high confidence",
        f"",
        f"### Predicted Top-10",
        f"",
        f"| #  | {'Rider':<{max_name_len}} | Top-10 % | Podium % | H2H  | Form |",
        f"|----|-{'-'*max_name_len}-|----------|----------|------|------|",
    ])

    for i, (_, row) in enumerate(top10_preds.iterrows(), 1):
        h2h = f"{row['H2H Field Score']*100:3.0f}%" if row['H2H Confidence'] > 0.3 else "N/A "
        form = f"{row['Recent Form']:4.1f}" if pd.notna(row['Recent Form']) else "N/A "
        top10_pct = f"{row['Top-10 Probability']*100:5.1f}%"
        top3_pct = f"{row['Top-3 Probability']*100:5.1f}%"

        if row['Top-10 Probability'] >= 0.70:
            rider_name = f"**{row['Rider']}**"
        else:
            rider_name = row['Rider']

        lines.append(
            f"| {i:2d} | {rider_name:<{max_name_len}} | {top10_pct:>8} | {top3_pct:>8} | {h2h:>4} | {form:>4} |"
        )

    lines.extend([
        f"",
        f"### Podium Prediction",
        f"",
    ])

    podium_top3 = predictions_df[predictions_df["DNS Risk"] == False].nlargest(3, "Top-3 Probability")
    medals = ["1.", "2.", "3."]
    for medal, (_, row) in zip(medals, podium_top3.iterrows()):
        lines.append(f"{medal} **{row['Rider']}** ({row['Top-3 Probability']*100:.1f}%)")

    # DNS risks
    dns_risks = predictions_df[predictions_df["DNS Risk"] == True]
    if len(dns_risks) > 0:
        lines.extend([
            f"",
            f"### DNS Risks",
            f"",
        ])
        for _, row in dns_risks.iterrows():
            lines.append(f"- {row['Rider']}")

    lines.append("")
    return lines


def generate_predictions_report(
    predictions_df: pd.DataFrame,
    race_name: str,
    race_date: str,
    category: str,
    series: str = "UCI World Cup"
) -> str:
    """
    Generate or update a combined markdown predictions report for a race.

    Appends category section if report exists, creates new if not.
    Returns path to the generated report.
    """
    threshold = config.CONFIDENCE_THRESHOLD
    report_filename = f"{race_name.upper()}_PREDICTIONS.md"
    report_path = config.PROJECT_ROOT / report_filename

    # Check if report already exists (adding second category)
    if report_path.exists():
        with open(report_path, 'r') as f:
            existing_content = f.read()

        # Check if this category already exists
        if f"## {category}" in existing_content:
            # Category already in report, skip
            return str(report_path)

        # Add new category section before footer
        footer_marker = "---\n\n*Generated by"
        if footer_marker in existing_content:
            parts = existing_content.rsplit(footer_marker, 1)
            new_section = _generate_category_section(predictions_df, category, threshold)
            updated_content = parts[0] + "---\n\n" + '\n'.join(new_section) + footer_marker + parts[1]
        else:
            # No footer found, just append
            new_section = _generate_category_section(predictions_df, category, threshold)
            updated_content = existing_content + "\n---\n\n" + '\n'.join(new_section)

        with open(report_path, 'w') as f:
            f.write(updated_content)

        return str(report_path)

    # Create new report
    lines = [
        f"# {race_name} Predictions",
        f"",
        f"**{series}** | {race_date}",
        f"",
        f"*VeloPredict v6 | Confidence threshold: {threshold:.0%}*",
        f"",
        f"---",
        f"",
    ]

    # Add category section
    lines.extend(_generate_category_section(predictions_df, category, threshold))

    lines.extend([
        f"---",
        f"",
        f"*Generated by VeloPredict pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    return str(report_path)


def _generate_validation_category_section(
    validation_results: dict,
    matched_df: pd.DataFrame,
    category: str,
    threshold: float
) -> list:
    """Generate markdown lines for a single category's validation results."""
    lines = []

    # Get correct/missed/false positives from matched data
    correct = matched_df[(matched_df['predicted_top10']) & (matched_df['actual_top10'])].sort_values('actual_place')
    missed = matched_df[(~matched_df['predicted_top10']) & (matched_df['actual_top10'])].sort_values('actual_place')
    false_pos = matched_df[(matched_df['predicted_top10']) & (~matched_df['actual_top10'])].sort_values('actual_place')

    lines.extend([
        f"## {category}",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| **Recall** | {validation_results['recall']:.1%} ({len(correct)}/{validation_results['actual_top10']}) |",
        f"| **Precision** | {validation_results['precision']:.1%} ({len(correct)}/{validation_results['predicted_top10']}) |",
        f"| High Confidence Accuracy | {validation_results.get('high_conf_accuracy', 0):.1%} |",
        f"",
        f"### Correct Predictions",
        f"",
    ])

    if len(correct) > 0:
        for _, row in correct.iterrows():
            lines.append(f"- P{int(row['actual_place'])} **{row['rider']}** ({row['prob']*100:.0f}%)")
    else:
        lines.append("*None*")

    lines.extend([
        f"",
        f"### Missed Top-10",
        f"",
    ])

    if len(missed) > 0:
        for _, row in missed.iterrows():
            lines.append(f"- P{int(row['actual_place'])} {row['rider']} ({row['prob']*100:.0f}% < {threshold:.0%})")
    else:
        lines.append("*None*")

    lines.extend([
        f"",
        f"### False Positives",
        f"",
    ])

    if len(false_pos) > 0:
        for _, row in false_pos.head(5).iterrows():
            lines.append(f"- P{int(row['actual_place'])} {row['rider']} ({row['prob']*100:.0f}%)")
    else:
        lines.append("*None*")

    lines.append("")
    return lines


def generate_validation_report(
    validation_results: dict,
    matched_df: pd.DataFrame,
    race_name: str,
    race_date: str,
    category: str,
    series: str = "UCI World Cup"
) -> str:
    """
    Generate or update a combined markdown validation report for a race.

    Appends category section if report exists, creates new if not.
    Returns path to the generated report.
    """
    threshold = config.CONFIDENCE_THRESHOLD
    report_filename = f"{race_name.upper()}_VALIDATION_RESULTS.md"
    report_path = config.PROJECT_ROOT / report_filename

    # Check if report already exists (adding second category)
    if report_path.exists():
        with open(report_path, 'r') as f:
            existing_content = f.read()

        # Check if this category already exists
        if f"## {category}" in existing_content:
            return str(report_path)

        # Add new category section before footer
        footer_marker = "---\n\n*Generated by"
        if footer_marker in existing_content:
            parts = existing_content.rsplit(footer_marker, 1)
            new_section = _generate_validation_category_section(validation_results, matched_df, category, threshold)
            updated_content = parts[0] + "---\n\n" + '\n'.join(new_section) + footer_marker + parts[1]
        else:
            new_section = _generate_validation_category_section(validation_results, matched_df, category, threshold)
            updated_content = existing_content + "\n---\n\n" + '\n'.join(new_section)

        with open(report_path, 'w') as f:
            f.write(updated_content)

        return str(report_path)

    # Create new report
    lines = [
        f"# {race_name} Validation Results",
        f"",
        f"**{series}** | {race_date}",
        f"",
        f"*VeloPredict v6 Performance Analysis*",
        f"",
        f"---",
        f"",
    ]

    # Add category section
    lines.extend(_generate_validation_category_section(validation_results, matched_df, category, threshold))

    lines.extend([
        f"---",
        f"",
        f"*Generated by VeloPredict pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    return str(report_path)


# ============================================================
# PREDICTION PIPELINE
# ============================================================

def parse_startlist_filename(filepath: Path) -> dict:
    """
    Parse race metadata from startlist filename.

    Expected format: racename_category_date.csv
    Example: namur_men_elite_2025-12-14.csv
    """
    stem = filepath.stem.lower()

    # Extract date
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", stem)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # Extract category
    if "women" in stem:
        category = "Women Elite"
    elif "men" in stem:
        category = "Men Elite"
    else:
        category = "Men Elite"

    # Extract race name (first part before category)
    parts = stem.replace(date, "").strip("_").split("_")
    race_name = parts[0].title() if parts else "Unknown"

    return {
        "race_name": race_name,
        "category": category,
        "date": date,
        "series": "UCI World Cup"  # Default, can be overridden
    }


def predict(startlist_path: str, category: str = None, output: str = None):
    """
    Generate predictions from a startlist file.

    Auto-detects category and race name from filename.
    Automatically registers the race in the registry.
    """
    startlist_path = Path(startlist_path)

    if not startlist_path.exists():
        print(f"Error: Startlist not found: {startlist_path}")
        return None

    # Parse metadata from filename
    meta = parse_startlist_filename(startlist_path)

    if category is None:
        category = meta["category"]

    print(f"=" * 70)
    print(f"VELOPREDICT PIPELINE: PREDICT")
    print(f"=" * 70)
    print(f"Race: {meta['race_name']} ({category})")
    print(f"Date: {meta['date']}")
    print(f"Startlist: {startlist_path}")

    # Generate output path if not specified
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        race_slug = meta['race_name'].lower().replace(" ", "_")
        cat_slug = category.lower().replace(" ", "_")
        output_filename = f"predictions_{race_slug}_{cat_slug}_{timestamp}.csv"
        output = str(config.CLEAN_DIR / output_filename)
        output_relative = f"data/clean/{output_filename}"
    else:
        output_relative = output

    # Use existing predict_race module
    from predict_race import predict_race

    predictions = predict_race(
        startlist_path=str(startlist_path),
        category=category,
        output_path=output
    )

    # Generate markdown report
    report_path = generate_predictions_report(
        predictions,
        meta['race_name'],
        meta['date'],
        category,
        meta['series']
    )
    print(f"\nPredictions report: {report_path}")

    # Register the race (use relative path for portability)
    race_id = f"{meta['race_name'].lower()}_{meta['date']}"
    register_race(
        race_id=race_id,
        name=meta['race_name'],
        date=meta['date'],
        series=meta['series'],
        category=category,
        predictions_path=output_relative
    )

    return predictions


# ============================================================
# RESULTS PIPELINE
# ============================================================

def parse_result_filename(filepath: Path) -> dict:
    """
    Parse race metadata from result filename.

    Expected format: Results__Series__Race__Category__Date__Location.csv
    Example: Results__UCI-World-Cup__Namur__Men-Elite__2025-12-14__Namur-BEL.csv
    """
    stem = filepath.stem
    parts = stem.split("__")

    if len(parts) >= 5:
        return {
            "series": parts[1].replace("-", " "),
            "race_name": parts[2],
            "category": parts[3].replace("-", " "),
            "date": parts[4],
            "location": parts[5] if len(parts) > 5 else parts[2]
        }

    # Fallback: try to extract from filename patterns
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", stem)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    category = "Men Elite" if "men" in stem.lower() else "Women Elite" if "women" in stem.lower() else "Men Elite"

    return {
        "series": "Unknown",
        "race_name": stem.split("_")[0] if "_" in stem else stem,
        "category": category,
        "date": date,
        "location": "Unknown"
    }


def add_results(results_path: str, skip_retrain: bool = False):
    """
    Add new race results to training data.

    1. Parse results file
    2. Standardize format
    3. Append to results_with_features.csv
    4. Recompute features
    5. Optionally retrain model
    """
    results_path = Path(results_path)

    if not results_path.exists():
        print(f"Error: Results file not found: {results_path}")
        return False

    print(f"=" * 70)
    print(f"VELOPREDICT PIPELINE: ADD RESULTS")
    print(f"=" * 70)
    print(f"Results file: {results_path}")

    # Parse metadata from filename
    meta = parse_result_filename(results_path)
    print(f"Race: {meta['race_name']} ({meta['category']})")
    print(f"Date: {meta['date']}")
    print(f"Series: {meta['series']}")

    # Load and parse results
    new_results = pd.read_csv(results_path)
    print(f"Loaded {len(new_results)} riders")

    # Standardize column names
    col_map = {
        'Position': 'Place',
        'Pos': 'Place',
        'Rank': 'Place',
        'Nationality': 'NAT',
        'Country': 'NAT',
    }
    new_results = new_results.rename(columns=col_map)

    # Handle name formats
    if 'Name' in new_results.columns:
        # Fix newline-separated names (e.g., "First\nLAST")
        new_results['rider_name'] = new_results['Name'].apply(lambda x:
            str(x).replace('\n', ' ').title() if pd.notna(x) else x
        )
    elif 'rider_name' not in new_results.columns:
        print("Error: No 'Name' or 'rider_name' column found")
        return False

    # Parse Place to numeric
    new_results['Place'] = pd.to_numeric(new_results['Place'], errors='coerce')
    new_results = new_results.dropna(subset=['Place'])

    # Add race metadata
    race_date = pd.Timestamp(meta['date'])
    race_id = f"{race_date.strftime('%Y%m%d')}_{meta['series'].lower().replace(' ', '-')}_{meta['race_name'].lower()}_{meta['location'].lower()}"

    new_results['race_date'] = race_date
    new_results['race_id'] = race_id
    new_results['series_name'] = meta['series']
    new_results['race_name'] = meta['race_name']
    new_results['race_location'] = meta['location']
    new_results['Category Name'] = meta['category']

    print(f"Race ID: {race_id}")
    print(f"Valid results: {len(new_results)}")

    # Load existing data
    existing_path = config.CLEAN_DIR / "results_with_features.csv"
    if existing_path.exists():
        existing = pd.read_csv(existing_path, parse_dates=['race_date'])
        print(f"Existing data: {len(existing)} rows")

        # Check for duplicates
        if race_id in existing['race_id'].values:
            print(f"Warning: Race {race_id} already exists in data!")
            overwrite = input("Overwrite? (y/n): ").lower().strip()
            if overwrite != 'y':
                print("Skipping...")
                return False
            # Remove existing race data
            existing = existing[existing['race_id'] != race_id]
    else:
        existing = pd.DataFrame()

    # Add missing columns with defaults
    for col in existing.columns:
        if col not in new_results.columns:
            new_results[col] = np.nan

    # Combine
    combined = pd.concat([existing, new_results], ignore_index=True)
    print(f"Combined data: {len(combined)} rows")

    # Recompute all features
    print("\nRecomputing features...")
    combined = compute_all_features(combined)

    # Save
    combined.to_csv(existing_path, index=False)
    print(f"Saved to: {existing_path}")

    # Rebuild H2H matrix cache
    print("\nRebuilding H2H matrix...")
    import head_to_head
    head_to_head._h2h_matrix = None  # Clear cache
    head_to_head.get_h2h_matrix()  # Rebuild

    # Register the race results in registry
    registry_race_id = f"{meta['race_name'].lower()}_{meta['date']}"
    register_race(
        race_id=registry_race_id,
        name=meta['race_name'],
        date=meta['date'],
        series=meta['series'],
        category=meta['category'],
        predictions_path=None,  # Will be updated if predictions exist
        results_path=str(results_path)
    )

    if not skip_retrain:
        print("\n" + "=" * 70)
        retrain()

    return True


def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all features for training data.

    This is the core feature engineering pipeline.
    """
    print("  1/7 Normalizing names...")
    df['rider_name_norm'] = df['rider_name'].apply(standardize_name)

    # Sort for time-based features
    df = df.sort_values(['rider_name_norm', 'race_date'])

    print("  2/7 UCI points features...")
    df['Carried Points'] = pd.to_numeric(df['Carried Points'], errors='coerce')
    df['Scored Points'] = pd.to_numeric(df['Scored Points'], errors='coerce')

    max_points = df['Carried Points'].max()
    if pd.isna(max_points) or max_points == 0:
        max_points = 700
    df['uci_points_normalized'] = df['Carried Points'].fillna(0) / max_points

    df['points_tier'] = pd.cut(
        df['Carried Points'].fillna(0),
        bins=[0, 50, 150, 1000],
        labels=['low', 'mid', 'high']
    ).fillna('low')

    print("  3/7 Team tier features...")
    def categorize_team(team_name):
        if pd.isna(team_name):
            return 'no_team'
        team_upper = str(team_name).upper()
        if any(top in team_upper for top in config.TOP_TEAMS):
            return 'top_team'
        return 'other_team'

    df['team_tier'] = df['Team Name'].apply(categorize_team)

    print("  4/7 Category features...")
    df['is_elite'] = df['Category Name'].str.contains('Elite', case=False, na=False).astype(int)
    df['is_women'] = df['Category Name'].str.contains('Women', case=False, na=False).astype(int)

    print("  5/7 Form features...")
    df['races_so_far'] = df.groupby('rider_name_norm').cumcount()

    place_shifted = df.groupby('rider_name_norm')['Place'].shift(1)

    df['avg_place_last3'] = (
        place_shifted.groupby(df['rider_name_norm'])
        .rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
    )

    df['best_place_last5'] = (
        place_shifted.groupby(df['rider_name_norm'])
        .rolling(5, min_periods=1).min().reset_index(level=0, drop=True)
    )

    df['last_place'] = place_shifted
    df['days_since_last_race'] = df.groupby('rider_name_norm')['race_date'].diff().dt.days
    df['last_carried_points'] = df.groupby('rider_name_norm')['Carried Points'].shift(1)
    df['last_scored_points'] = df.groupby('rider_name_norm')['Scored Points'].shift(1)

    print("  6/7 Win rate features...")
    df['top3_finish'] = (df['Place'] <= 3).astype(int)
    top3_shifted = df.groupby('rider_name_norm')['top3_finish'].shift(1)
    df['top3_rate_career'] = (
        top3_shifted.groupby(df['rider_name_norm'])
        .expanding().mean().reset_index(level=0, drop=True)
    )

    df['top10_finish'] = (df['Place'] <= 10).astype(int)
    top10_shifted = df.groupby('rider_name_norm')['top10_finish'].shift(1)
    df['top10_rate_career'] = (
        top10_shifted.groupby(df['rider_name_norm'])
        .expanding().mean().reset_index(level=0, drop=True)
    )

    print("  7/7 Series & new rider features...")
    df['series_appearances'] = df.groupby(['rider_name_norm', 'series_name']).cumcount()
    df['is_new_rider'] = (df['races_so_far'] == 0).astype(int)

    # H2H features - computed per race (slow but accurate)
    print("  Computing H2H features (this may take a while)...")
    df = compute_h2h_features(df)

    return df


def compute_h2h_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute head-to-head features for all races."""
    from collections import defaultdict

    h2h_records = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    df = df.sort_values('race_date')

    h2h_scores = []
    h2h_known = []

    races = df.groupby('race_id')
    total_races = len(races)

    for race_idx, (race_id, race_df) in enumerate(races):
        if race_idx % 20 == 0:
            print(f"    Processing race {race_idx+1}/{total_races}...")

        race_riders = race_df[race_df['Place'].notna()][['rider_name_norm', 'Place', 'Category Name']].values

        # Calculate H2H scores using HISTORICAL data only
        race_h2h_scores = {}
        race_h2h_known = {}

        for rider_name, place, category in race_riders:
            if pd.isna(rider_name):
                race_h2h_scores[rider_name] = 0.5
                race_h2h_known[rider_name] = 0
                continue

            opponents = [(r, p, c) for r, p, c in race_riders
                        if r != rider_name and c == category and not pd.isna(r)]

            if not opponents:
                race_h2h_scores[rider_name] = 0.5
                race_h2h_known[rider_name] = 0
                continue

            win_rates = []
            for opp_name, _, _ in opponents:
                if opp_name in h2h_records[rider_name] and h2h_records[rider_name][opp_name][1] > 0:
                    wins, total = h2h_records[rider_name][opp_name]
                    win_rates.append(wins / total)

            if win_rates:
                race_h2h_scores[rider_name] = np.mean(win_rates)
                race_h2h_known[rider_name] = len(win_rates)
            else:
                race_h2h_scores[rider_name] = 0.5
                race_h2h_known[rider_name] = 0

        # Store scores
        for idx in race_df.index:
            rider = race_df.loc[idx, 'rider_name_norm']
            h2h_scores.append(race_h2h_scores.get(rider, 0.5))
            h2h_known.append(race_h2h_known.get(rider, 0))

        # Update H2H records for future races
        for i in range(len(race_riders)):
            for j in range(i + 1, len(race_riders)):
                r1_name, r1_place, r1_cat = race_riders[i]
                r2_name, r2_place, r2_cat = race_riders[j]

                if pd.isna(r1_name) or pd.isna(r2_name) or r1_cat != r2_cat:
                    continue

                h2h_records[r1_name][r2_name][1] += 1
                h2h_records[r2_name][r1_name][1] += 1

                if r1_place < r2_place:
                    h2h_records[r1_name][r2_name][0] += 1
                elif r2_place < r1_place:
                    h2h_records[r2_name][r1_name][0] += 1

    df['h2h_field_score'] = h2h_scores
    df['h2h_known_opponents'] = h2h_known

    return df


# ============================================================
# RETRAIN PIPELINE
# ============================================================

def retrain():
    """
    Retrain the model with updated data.

    Uses train_model_v2.py logic but runs from here.
    """
    print(f"=" * 70)
    print(f"VELOPREDICT PIPELINE: RETRAIN")
    print(f"=" * 70)

    import subprocess
    result = subprocess.run(
        [sys.executable, "train_model_v2.py"],
        capture_output=False
    )

    return result.returncode == 0


# ============================================================
# VALIDATION PIPELINE
# ============================================================

def validate(predictions_path: str, results_path: str, threshold: float = None):
    """
    Validate predictions against actual results.

    Computes:
    - Recall: % of actual Top-10 that we predicted
    - Precision: % of predictions that were correct
    - Podium accuracy
    """
    if threshold is None:
        threshold = config.CONFIDENCE_THRESHOLD

    print(f"=" * 70)
    print(f"VELOPREDICT PIPELINE: VALIDATE")
    print(f"=" * 70)

    predictions_path = Path(predictions_path)
    results_path = Path(results_path)

    if not predictions_path.exists():
        print(f"Error: Predictions file not found: {predictions_path}")
        return None
    if not results_path.exists():
        print(f"Error: Results file not found: {results_path}")
        return None

    # Load data
    pred_df = pd.read_csv(predictions_path)
    results_df = pd.read_csv(results_path)

    print(f"Predictions: {len(pred_df)} riders")
    print(f"Results: {len(results_df)} riders")
    print(f"Threshold: {threshold:.0%}")

    # Standardize column names
    if 'Position' in results_df.columns:
        results_df = results_df.rename(columns={'Position': 'Place'})

    # Standardize names for matching
    pred_df['rider_std'] = pred_df['Rider'].apply(standardize_name)

    # Handle different name formats in results
    if 'Name' in results_df.columns:
        results_df['rider_std'] = results_df['Name'].apply(
            lambda x: standardize_name(str(x).replace('\n', ' ').title()) if pd.notna(x) else None
        )
    else:
        results_df['rider_std'] = results_df['rider_name'].apply(standardize_name)

    results_df['Place'] = pd.to_numeric(results_df['Place'], errors='coerce')

    # Match predictions to results
    matched = []
    for _, pred_row in pred_df.iterrows():
        rider_std = pred_row['rider_std']
        prob = pred_row['Top-10 Probability']
        top3_prob = pred_row.get('Top-3 Probability', 0)

        match = results_df[results_df['rider_std'] == rider_std]
        if not match.empty:
            place = match.iloc[0]['Place']
            if pd.notna(place):
                matched.append({
                    'rider': pred_row['Rider'],
                    'prob': prob,
                    'top3_prob': top3_prob,
                    'predicted_top10': prob >= threshold,
                    'actual_place': int(place),
                    'actual_top10': place <= 10,
                    'actual_top3': place <= 3
                })

    if not matched:
        print("Error: No matches found between predictions and results")
        return None

    df = pd.DataFrame(matched)

    # Calculate metrics
    predicted_top10 = df[df['predicted_top10']]
    actual_top10 = df[df['actual_top10']]

    true_positives = len(predicted_top10[predicted_top10['actual_top10']])
    false_positives = len(predicted_top10[~predicted_top10['actual_top10']])
    false_negatives = len(actual_top10[~actual_top10['predicted_top10']])

    precision = true_positives / len(predicted_top10) if len(predicted_top10) > 0 else 0
    recall = true_positives / len(actual_top10) if len(actual_top10) > 0 else 0

    # Podium metrics (using 30% threshold)
    podium_preds = df[df['top3_prob'] >= 0.30]
    podium_correct = len(podium_preds[podium_preds['actual_top3']]) if len(podium_preds) > 0 else 0
    podium_accuracy = podium_correct / len(podium_preds) if len(podium_preds) > 0 else 0

    # High confidence metrics
    high_conf = df[df['prob'] >= 0.70]
    high_conf_correct = len(high_conf[high_conf['actual_top10']]) if len(high_conf) > 0 else 0
    high_conf_accuracy = high_conf_correct / len(high_conf) if len(high_conf) > 0 else 0

    print(f"\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"\nMatched riders: {len(df)}")
    print(f"Predicted Top-10: {len(predicted_top10)}")
    print(f"Actual Top-10: {len(actual_top10)}")

    print(f"\n📊 METRICS:")
    print(f"  Recall (coverage):     {recall:.1%} ({true_positives}/{len(actual_top10)} actual Top-10 predicted)")
    print(f"  Precision:             {precision:.1%} ({true_positives}/{len(predicted_top10)} predictions correct)")
    print(f"  False positives:       {false_positives}")
    print(f"  False negatives:       {false_negatives}")

    print(f"\n🎯 HIGH CONFIDENCE (>70%):")
    print(f"  Predictions: {len(high_conf)}")
    print(f"  Correct: {high_conf_correct} ({high_conf_accuracy:.1%})")

    print(f"\n🏆 PODIUM (>30% Top-3 prob):")
    print(f"  Predictions: {len(podium_preds)}")
    print(f"  Correct: {podium_correct} ({podium_accuracy:.1%})")

    # Show details
    print(f"\n✅ CORRECT TOP-10 PREDICTIONS:")
    correct = predicted_top10[predicted_top10['actual_top10']].sort_values('actual_place')
    for _, row in correct.iterrows():
        print(f"  P{row['actual_place']:2d} - {row['rider']:30s} ({row['prob']:.1%})")

    print(f"\n❌ MISSED TOP-10 (false negatives):")
    missed = actual_top10[~actual_top10['predicted_top10']].sort_values('actual_place')
    for _, row in missed.iterrows():
        print(f"  P{row['actual_place']:2d} - {row['rider']:30s} ({row['prob']:.1%} < {threshold:.0%})")

    print(f"\n⚠️ FALSE POSITIVES (predicted but outside Top-10):")
    false_pos = predicted_top10[~predicted_top10['actual_top10']].sort_values('actual_place')
    for _, row in false_pos.head(10).iterrows():
        print(f"  P{row['actual_place']:2d} - {row['rider']:30s} ({row['prob']:.1%})")

    return {
        'recall': recall,
        'precision': precision,
        'high_conf_accuracy': high_conf_accuracy,
        'podium_accuracy': podium_accuracy,
        'matched': len(df),
        'predicted_top10': len(predicted_top10),
        'actual_top10': len(actual_top10)
    }


# ============================================================
# FULL POST-RACE PIPELINE
# ============================================================

def full_pipeline(results_path: str, predictions_path: str = None):
    """
    Run complete post-race workflow:
    1. Add results to training data
    2. Retrain model
    3. Validate predictions (if provided)
    """
    print(f"=" * 70)
    print(f"VELOPREDICT PIPELINE: FULL POST-RACE WORKFLOW")
    print(f"=" * 70)

    results_path = Path(results_path)

    # Step 1: Add results
    print("\n[STEP 1/3] Adding results to training data...")
    success = add_results(str(results_path), skip_retrain=True)
    if not success:
        print("Failed to add results. Aborting.")
        return False

    # Step 2: Retrain
    print("\n[STEP 2/3] Retraining model...")
    retrain()

    # Step 3: Validate (if predictions provided)
    if predictions_path:
        print("\n[STEP 3/3] Validating predictions...")
        validate(predictions_path, str(results_path))
    else:
        print("\n[STEP 3/3] Skipping validation (no predictions file provided)")
        print("  To validate, run: python pipeline.py validate --predictions <file> --results <file>")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    return True


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="VeloPredict Automated Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate predictions from startlist
  python pipeline.py predict data/startlists/namur_men_elite_2025-12-14.csv

  # Add race results and retrain
  python pipeline.py add-results data/results/Results__UCI-World-Cup__Namur__Men-Elite__2025-12-14.csv

  # Just retrain the model
  python pipeline.py retrain

  # Validate predictions against results
  python pipeline.py validate --predictions data/clean/predictions_namur.csv --results data/results/namur.csv

  # Full post-race workflow
  python pipeline.py full data/results/namur.csv --predictions data/clean/predictions_namur.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Pipeline command')

    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Generate predictions from startlist')
    predict_parser.add_argument('startlist', help='Path to startlist CSV')
    predict_parser.add_argument('--category', help='Race category (auto-detected if not specified)')
    predict_parser.add_argument('--output', help='Output path for predictions')

    # Add results command
    results_parser = subparsers.add_parser('add-results', help='Add race results to training data')
    results_parser.add_argument('results', help='Path to results CSV')
    results_parser.add_argument('--skip-retrain', action='store_true', help='Skip retraining after adding')

    # Retrain command
    retrain_parser = subparsers.add_parser('retrain', help='Retrain model with current data')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate predictions against results')
    validate_parser.add_argument('--predictions', required=True, help='Path to predictions CSV')
    validate_parser.add_argument('--results', required=True, help='Path to results CSV')
    validate_parser.add_argument('--threshold', type=float, help='Confidence threshold')

    # Full pipeline command
    full_parser = subparsers.add_parser('full', help='Run full post-race workflow')
    full_parser.add_argument('results', help='Path to results CSV')
    full_parser.add_argument('--predictions', help='Path to predictions CSV (for validation)')

    args = parser.parse_args()

    if args.command == 'predict':
        predict(args.startlist, args.category, args.output)
    elif args.command == 'add-results':
        add_results(args.results, args.skip_retrain)
    elif args.command == 'retrain':
        retrain()
    elif args.command == 'validate':
        validate(args.predictions, args.results, args.threshold)
    elif args.command == 'full':
        full_pipeline(args.results, args.predictions)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
