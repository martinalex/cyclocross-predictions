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
from scipy import stats

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
# MARKDOWN TABLE UTILITIES
# ============================================================

def format_markdown_table(headers: list, rows: list, alignments: list = None) -> list:
    """
    Generate a properly aligned markdown table.

    Args:
        headers: List of column header strings
        rows: List of row data (each row is a list of values)
        alignments: List of alignments ('left', 'right', 'center') per column
                   Defaults to 'left' for text, 'right' for numbers

    Returns:
        List of markdown lines forming the aligned table

    Example:
        headers = ['#', 'Rider', 'Top-10 %']
        rows = [[1, 'VAN DER POEL', '99.0%'], [2, 'NYS', '96.2%']]
        lines = format_markdown_table(headers, rows)
    """
    if not rows:
        return [f"| {' | '.join(headers)} |", f"|{'|'.join(['---'] * len(headers))}|"]

    # Convert all values to strings
    str_rows = [[str(v) for v in row] for row in rows]
    str_headers = [str(h) for h in headers]

    # Calculate column widths (max of header and all row values)
    col_widths = []
    for i in range(len(str_headers)):
        max_width = len(str_headers[i])
        for row in str_rows:
            if i < len(row):
                max_width = max(max_width, len(row[i]))
        col_widths.append(max_width)

    # Default alignments: detect numbers for right-align
    if alignments is None:
        alignments = []
        for i, h in enumerate(str_headers):
            # Check if column contains mostly numbers/percentages
            sample_values = [row[i] for row in str_rows[:3] if i < len(row)]
            is_numeric = all(
                any(c.isdigit() for c in v) and not any(c.isalpha() for c in v.replace('%', ''))
                for v in sample_values if v.strip()
            ) if sample_values else False
            alignments.append('right' if is_numeric else 'left')

    # Build header row
    header_cells = []
    for i, h in enumerate(str_headers):
        if alignments[i] == 'right':
            header_cells.append(h.rjust(col_widths[i]))
        elif alignments[i] == 'center':
            header_cells.append(h.center(col_widths[i]))
        else:
            header_cells.append(h.ljust(col_widths[i]))
    header_line = '| ' + ' | '.join(header_cells) + ' |'

    # Build separator row with alignment markers
    sep_cells = []
    for i, width in enumerate(col_widths):
        if alignments[i] == 'right':
            sep_cells.append('-' * width + ':')
        elif alignments[i] == 'center':
            sep_cells.append(':' + '-' * width + ':')
        else:
            sep_cells.append('-' * (width + 1))
    sep_line = '|' + '|'.join(sep_cells) + '|'

    # Build data rows
    lines = [header_line, sep_line]
    for row in str_rows:
        cells = []
        for i in range(len(str_headers)):
            val = row[i] if i < len(row) else ''
            if alignments[i] == 'right':
                cells.append(val.rjust(col_widths[i]))
            elif alignments[i] == 'center':
                cells.append(val.center(col_widths[i]))
            else:
                cells.append(val.ljust(col_widths[i]))
        lines.append('| ' + ' | '.join(cells) + ' |')

    return lines


# ============================================================
# REPORT GENERATION
# ============================================================

def _generate_rider_note(row: pd.Series) -> str:
    """Generate a brief note about a rider based on their stats."""
    notes = []

    # Form-based notes
    form = row.get('Recent Form', None)
    if pd.notna(form):
        if form <= 1.5:
            notes.append("winning form")
        elif form <= 3.0:
            notes.append("strong form")
        elif form >= 15.0:
            notes.append("poor recent form")

    # H2H-based notes
    h2h = row.get('H2H Field Score', None)
    h2h_conf = row.get('H2H Confidence', 0)
    if pd.notna(h2h) and h2h_conf > 0.3:
        if h2h >= 0.95:
            notes.append("dominates field")
        elif h2h >= 0.85:
            notes.append("strong H2H")
        elif h2h <= 0.3:
            notes.append("struggles vs field")
    elif h2h_conf <= 0.3:
        notes.append("limited H2H data")

    # Career rate notes
    career_rate = row.get('Career Top-10 Rate', None)
    if pd.notna(career_rate):
        if career_rate >= 0.90:
            notes.append("elite consistency")
        elif career_rate <= 0.30 and career_rate > 0:
            notes.append("rarely scores")

    # Status-based notes
    status = row.get('Status', 'found')
    if status == 'new_rider':
        notes.append("season debut")

    # DNS reason if present
    dns_reason = row.get('DNS Reason', None)
    if pd.notna(dns_reason) and dns_reason:
        notes.append(str(dns_reason).replace('DNS Risk: ', ''))

    # Podium contender
    top3_prob = row.get('Top-3 Probability', 0)
    if top3_prob >= 0.30:
        notes.append("podium contender")
    elif top3_prob >= 0.15:
        notes.append("podium threat")

    return "; ".join(notes[:3]) if notes else "-"


def _generate_category_section_v65(predictions_df: pd.DataFrame, category: str) -> list:
    """
    Generate markdown lines for a single category's predictions using v6.5+ format.

    Key changes from old format:
    - Fixed N=10 predictions (not threshold-based)
    - Fixed N=3 podium picks
    - Simpler table: Pred Rank, Rider, Top-10 %, Podium %, H2H vs Field
    - Borderline = positions 11-15 (not threshold-based)
    - No "Rest of Field" section (too verbose)
    - No "Notes" or "Form" columns (cleaner)
    """
    lines = []

    # Sort all riders by Top-10 probability
    all_riders = predictions_df.sort_values("Top-10 Probability", ascending=False).copy()

    # Fixed N=10 predictions (v6.4+ methodology)
    top10_preds = all_riders.head(10)

    # Borderline = positions 11-15
    borderline_preds = all_riders.iloc[10:15] if len(all_riders) > 10 else pd.DataFrame()

    high_conf = predictions_df[predictions_df["Top-10 Probability"] >= 0.70]
    field_size = len(predictions_df)

    lines.extend([
        f"## {category}",
        f"",
        f"**Field Size:** {field_size} riders",
        f"**High Confidence (>70%):** {len(high_conf)} riders",
        f"",
        f"### Predicted Top-10",
        f"",
    ])

    # Build Top-10 table rows (fixed N=10)
    table_rows = []
    for i, (_, row) in enumerate(top10_preds.iterrows(), 1):
        h2h = f"{row['H2H Field Score']*100:.0f}%" if row.get('H2H Confidence', 0) > 0.3 else "N/A"
        top10_pct = f"{row['Top-10 Probability']*100:.1f}%"
        top3_pct = f"{row['Top-3 Probability']*100:.1f}%"
        rider_name = row['Rider']
        table_rows.append([i, rider_name, top10_pct, top3_pct, h2h])

    headers = ['Pred Rank', 'Rider', 'Top-10 %', 'Podium %', 'H2H vs Field']
    alignments = ['right', 'left', 'right', 'right', 'right']
    lines.extend(format_markdown_table(headers, table_rows, alignments))

    # Predicted Podium (fixed N=3, by podium probability)
    lines.extend([
        f"",
        f"### Predicted Podium",
        f"",
    ])

    podium_top3 = all_riders.nlargest(3, "Top-3 Probability")
    podium_rows = []
    for i, (_, row) in enumerate(podium_top3.iterrows(), 1):
        podium_rows.append([i, row['Rider'], f"{row['Top-3 Probability']*100:.1f}%"])

    podium_headers = ['Position', 'Rider', 'Probability']
    podium_alignments = ['right', 'left', 'right']
    lines.extend(format_markdown_table(podium_headers, podium_rows, podium_alignments))

    # Borderline section (positions 11-15)
    if len(borderline_preds) > 0:
        lines.extend([
            f"",
            f"### Borderline Riders (11-15)",
            f"",
        ])

        borderline_rows = []
        for i, (_, row) in enumerate(borderline_preds.iterrows(), 11):
            h2h = f"{row['H2H Field Score']*100:.0f}%" if row.get('H2H Confidence', 0) > 0.3 else "N/A"
            top10_pct = f"{row['Top-10 Probability']*100:.1f}%"
            borderline_rows.append([i, row['Rider'], top10_pct, h2h])

        borderline_headers = ['Pred Rank', 'Rider', 'Top-10 %', 'H2H vs Field']
        borderline_alignments = ['right', 'left', 'right', 'right']
        lines.extend(format_markdown_table(borderline_headers, borderline_rows, borderline_alignments))

    lines.append("")
    return lines


def _generate_category_section(predictions_df: pd.DataFrame, category: str, threshold: float) -> list:
    """
    DEPRECATED: Old threshold-based format. Now redirects to v6.5+ format.
    Kept for backward compatibility but should not be used directly.
    """
    # Redirect to new v6.5+ format
    return _generate_category_section_v65(predictions_df, category)


def _generate_metrics_explanation() -> list:
    """Generate the Understanding the Metrics section for reports."""
    lines = [
        "## Understanding the Metrics",
        "",
        "### Top-10 Probability",
        "",
        "**What it measures:** The likelihood a rider finishes in positions 1-10 (scoring positions in UCI World Cup).",
        "",
        "**How it's calculated:**",
        "- A Random Forest classifier trained on 8,357+ historical race results",
        "- Uses Platt scaling calibration so probabilities reflect actual historical outcomes",
        "- When model says 70%, historically ~70% of riders at that probability finish Top-10",
        "",
        "**Key inputs:**",
        "- Head-to-head win rate vs this specific field (22.5% importance)",
        "- Recent form: avg finish last 3 races, best finish last 5 races",
        "- Career Top-10 rate across all races",
        "- Last race finish position",
        "- UCI points tier and team quality",
        "",
        "**Interpreting the values:**",
        "- **>90%** = Virtual lock for Top-10 (elite favorites)",
        "- **70-90%** = High confidence prediction",
        "- **55-70%** = Likely Top-10 but with uncertainty",
        "- **<55%** = Outside our prediction threshold",
        "",
        "---",
        "",
        "### Podium Probability (Top-3)",
        "",
        "**What it measures:** The likelihood a rider finishes on the podium (positions 1-3).",
        "",
        "**How it's calculated:**",
        "- Separate Random Forest model trained specifically for podium prediction",
        "- Much harder to predict than Top-10 (only 3 spots vs 10)",
        "- Also uses Platt scaling for calibrated probabilities",
        "",
        "**Key inputs:**",
        "- Same features as Top-10 model, but weighted differently",
        "- Career podium rate (top3_rate_career) becomes more important",
        "- H2H dominance matters more - need to beat almost everyone",
        "",
        "**Interpreting the values:**",
        "- **>50%** = Clear podium favorite (rare - usually only 1-2 riders per race)",
        "- **20-50%** = Realistic podium contender",
        "- **5-20%** = Outside chance if favorites falter",
        "- **<5%** = Would require multiple surprises",
        "",
        "**Why podium is harder to predict:**",
        "- Only 3 spots vs 10 for Top-10",
        "- More dependent on race-day tactics and luck",
        "- One crash or mechanical can reshuffle entire podium",
        "",
        "---",
        "",
        "### Form Score",
        "",
        "**What it measures:** A rider's recent racing performance, indicating current fitness and momentum.",
        "",
        "**How it's calculated:**",
        "- `avg_place_last3`: Average finishing position in last 3 races",
        "- Lower is better (Form 1.0 = averaging 1st place)",
        "- Only counts races where rider finished (DNF/DNS excluded from average)",
        "",
        "**Example calculation:**",
        "- Rider finished P1, P2, P1 in last 3 races -> Form = (1+2+1)/3 = **1.3**",
        "- Rider finished P5, P8, P10 -> Form = (5+8+10)/3 = **7.7**",
        "",
        "**Interpreting the values:**",
        "",
    ]

    # Form score interpretation table
    form_headers = ['Form Score', 'Interpretation']
    form_rows = [
        ['1.0 - 2.0', 'Elite form, winning/podiuming'],
        ['2.0 - 5.0', 'Strong form, consistent Top-5'],
        ['5.0 - 10.0', 'Solid form, regular Top-10'],
        ['10.0 - 20.0', 'Mixed results, inconsistent'],
        ['>20.0', 'Poor recent form or limited data'],
    ]
    lines.extend(format_markdown_table(form_headers, form_rows, ['left', 'left']))

    lines.extend([
        "",
        "**Why it matters:**",
        "- Captures current fitness that UCI points (updated monthly) miss",
        "- A rider on a hot streak is more dangerous than rankings suggest",
        "- Recent form is 13.6% of model importance (3rd most important feature)",
        "",
        "---",
        "",
        "### Career Top-10 Rate",
        "",
        "**What it measures:** Historical consistency - what percentage of a rider's career races resulted in Top-10 finishes.",
        "",
        "**How it's calculated:**",
        "- `top10_rate_career = (# of Top-10 finishes) / (# of races completed)`",
        "- Only uses data BEFORE the current race (no data leakage)",
        "- Builds up over a rider's career in our dataset",
        "",
        "**Example:**",
        "- Rider has 20 races, finished Top-10 in 18 -> Rate = 18/20 = **90%**",
        "- Rider has 50 races, finished Top-10 in 25 -> Rate = 25/50 = **50%**",
        "",
        "**Interpreting the values:**",
        "",
    ])

    # Career rate interpretation table
    career_headers = ['Career Rate', 'Rider Profile']
    career_rows = [
        ['>90%', 'Elite - almost always scores (MVDP, Brand)'],
        ['70-90%', 'Top-tier professional'],
        ['50-70%', 'Strong but inconsistent'],
        ['30-50%', 'Mid-pack regular'],
        ['<30%', 'Back of field or new rider'],
    ]
    lines.extend(format_markdown_table(career_headers, career_rows, ['left', 'left']))

    lines.extend([
        "",
        "**Why it matters:**",
        "- Provides baseline expectation independent of current form",
        "- Helps identify riders who consistently perform vs one-hit wonders",
        "- 11.2% of model importance (4th most important feature)",
        "",
        "---",
        "",
        "### Head-to-Head (H2H)",
        "",
        "**What it measures:** A rider's historical win rate against the specific opponents in this startlist.",
        "",
        "**How it's calculated:**",
        "- For each pair of riders who have raced together, track who finished ahead",
        "- H2H score = (wins against field) / (total matchups with field)",
        "- Only uses races BEFORE the current race (no data leakage)",
        "",
        "**Interpreting the values:**",
        "- **H2H 90%+** = Historically beats almost everyone in the field",
        "- **H2H 70-90%** = Strong record against this field",
        "- **H2H 50-70%** = Competitive, mixed results",
        "- **H2H <50%** = Usually loses to this field",
        "- **H2H N/A** = New rider or insufficient head-to-head data",
        "",
        "**Why it matters:**",
        "- #1 most important feature (22.5% of model importance)",
        "- Captures matchup-specific dynamics that other features miss",
        "- A rider who always beats this field is more likely to do so again",
        "",
    ])

    return lines


def _get_model_version() -> str:
    """Get current model version from registry."""
    registry = load_registry()
    return registry.get("current_version", "v6.5")


def _get_model_stats() -> tuple:
    """Get model observation count and H2H pair count from metadata."""
    metadata_path = config.MODELS_DIR / "model_metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        observations = metadata.get("total_observations", 0)
        # H2H pairs is approximately observations * (observations - 1) / 2 for unique pairs
        # But we use the actual h2h matrix size from predict_race if available
        return observations, 0  # H2H count calculated dynamically
    return 0, 0


def _generate_methodology_section() -> list:
    """Generate the v6.4+ methodology section for prediction reports."""
    return [
        "## Methodology (v6.4+)",
        "",
        "### Fixed Top-10 Predictions",
        "",
        "1. **Always predict exactly 10 riders** - No confidence threshold filtering",
        "2. **Always predict exactly 3 podium picks** - Top 3 by podium probability",
        "",
        "### Metrics We Track",
        "",
        "| Metric | Description |",
        "|--------|-------------|",
        "| **Hits@10** | How many of our 10 predictions finished in actual top-10? (X/10) |",
        "| **Hits@3** | How many of our 3 podium picks made the actual podium? (X/3) |",
        "| **Spearman Rank Correlation** | Did we get the ordering right? (-1 to +1) |",
        "| **MAE on Rank** | Average positions off for predicted riders |",
        "",
        "*Note: With fixed N=10 predictions, precision@10 = recall@10 = Hits@10/10*",
        "",
    ]


def _generate_distribution_section_v65(category: str, distribution: dict) -> list:
    """Generate distribution section for a specific category (v6.5+ format)."""
    if not distribution:
        return []

    lines = [
        f"### {category}",
        "",
    ]

    dist_headers = ['Metric', 'Value', 'Interpretation']
    dist_rows = [
        ['Low (<30%)', f"{distribution['low_pct']:.1f}%", 'Non-contenders'],
        ['Mid (30-60%)', f"{distribution['mid_pct']:.1f}%", 'Uncertain zone'],
        ['High (>60%)', f"{distribution['high_pct']:.1f}%", 'Likely contenders'],
        ['Mean Probability', f"{distribution['mean_prob']*100:.1f}%", 'Average across field'],
        ['Std Deviation', f"{distribution['std_prob']:.3f}", 'Probability spread'],
        ['New Riders', f"{distribution['new_rider_count']}", 'No prior race history'],
        ['Field Size', f"{distribution['field_size']}", 'Total riders'],
    ]
    lines.extend(format_markdown_table(dist_headers, dist_rows, ['left', 'right', 'left']))

    # Determine pattern
    if distribution['mid_pct'] < 10:
        pattern = "BIMODAL - Model is decisive"
    elif distribution['mid_pct'] > 20:
        pattern = "BALANCED - Model is uncertain"
    else:
        pattern = "MODERATE - Typical distribution"

    lines.extend([
        "",
        f"**Pattern:** {pattern}",
        "",
    ])

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

    Uses v6.5+ format:
    - Filename includes date: RACENAME_PREDICTIONS_YYYY-MM-DD.md
    - Fixed N=10 predictions (not threshold-based)
    - Proper header with model version, series, location
    - Methodology section explaining v6.4+ approach
    - Per-category distribution analysis

    Returns path to the generated report.
    """
    model_version = _get_model_version()
    observations, _ = _get_model_stats()

    # Filename includes date (v6.5+ format)
    report_filename = f"{race_name.upper()}_PREDICTIONS_{race_date}.md"
    report_path = config.PROJECT_ROOT / report_filename

    # Calculate distribution for this category
    distribution = calculate_distribution_metrics(predictions_df)

    # Check if report already exists (adding second category)
    if report_path.exists():
        with open(report_path, 'r') as f:
            existing_content = f.read()

        # Check if this category already exists
        if f"## {category}" in existing_content:
            # Category already in report, skip
            return str(report_path)

        # Find insertion point: before "## Combined Summary" or before "## Probability Distribution"
        combined_marker = "\n---\n\n## Combined Summary"
        distribution_marker = "\n---\n\n## Probability Distribution Analysis"
        footer_marker = "\n---\n\n*Generated by"

        new_section = _generate_category_section_v65(predictions_df, category)
        new_section_text = "\n---\n\n" + '\n'.join(new_section)

        # Also need to add distribution for this category
        if distribution:
            # Find the distribution section and add to it
            if "## Probability Distribution Analysis" in existing_content:
                # Add category distribution before the footer
                dist_lines = _generate_distribution_section_v65(category, distribution)
                dist_text = '\n'.join(dist_lines)

                # Insert category section before Combined Summary or Distribution
                if combined_marker in existing_content:
                    parts = existing_content.split(combined_marker, 1)
                    updated_content = parts[0] + new_section_text + combined_marker + parts[1]
                elif distribution_marker in existing_content:
                    parts = existing_content.split(distribution_marker, 1)
                    updated_content = parts[0] + new_section_text + distribution_marker + parts[1]
                else:
                    parts = existing_content.rsplit(footer_marker, 1)
                    updated_content = parts[0] + new_section_text + footer_marker + parts[1]

                # Now add the distribution for this category
                if footer_marker in updated_content:
                    parts = updated_content.rsplit(footer_marker, 1)
                    updated_content = parts[0] + "\n" + dist_text + footer_marker + parts[1]
            else:
                # No distribution section yet, just add category
                if footer_marker in existing_content:
                    parts = existing_content.rsplit(footer_marker, 1)
                    updated_content = parts[0] + new_section_text + footer_marker + parts[1]
                else:
                    updated_content = existing_content + new_section_text
        else:
            if combined_marker in existing_content:
                parts = existing_content.split(combined_marker, 1)
                updated_content = parts[0] + new_section_text + combined_marker + parts[1]
            elif footer_marker in existing_content:
                parts = existing_content.rsplit(footer_marker, 1)
                updated_content = parts[0] + new_section_text + footer_marker + parts[1]
            else:
                updated_content = existing_content + new_section_text

        with open(report_path, 'w') as f:
            f.write(updated_content)

        return str(report_path)

    # Create new report (v6.5+ format)
    # Format date nicely
    try:
        date_obj = datetime.strptime(race_date, "%Y-%m-%d")
        date_display = date_obj.strftime("%B %d, %Y")
    except ValueError:
        date_display = race_date

    lines = [
        f"# VeloPredict: {series} {race_name} Predictions",
        f"",
        f"**Race Date:** {date_display}",
        f"**Location:** {race_name}, Belgium",
        f"**Series:** {series}",
        f"**Model Version:** {model_version}",
        f"**Prediction Date:** {datetime.now().strftime('%B %d, %Y')}",
        f"",
        f"---",
        f"",
    ]

    # Add methodology section
    lines.extend(_generate_methodology_section())

    lines.append("---")
    lines.append("")

    # Add category section
    lines.extend(_generate_category_section_v65(predictions_df, category))

    # Add distribution analysis section
    if distribution:
        lines.append("---")
        lines.append("")
        lines.append("## Probability Distribution Analysis")
        lines.append("")
        lines.extend(_generate_distribution_section_v65(category, distribution))

    # Footer with model stats
    lines.extend([
        f"---",
        f"",
        f"*Generated by VeloPredict {model_version} | {observations:,} observations*",
    ])

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    return str(report_path)


def _generate_distribution_section(distribution: dict) -> list:
    """Generate markdown lines for the distribution analysis section."""
    if not distribution:
        return []

    lines = [
        "## Probability Distribution Analysis",
        "",
    ]

    # Distribution table
    dist_headers = ['Metric', 'Value', 'Interpretation']
    dist_rows = [
        ['Low (<30%)', f"{distribution['low_pct']:.1f}%", 'Non-contenders'],
        ['Mid (30-60%)', f"{distribution['mid_pct']:.1f}%", 'Uncertain zone'],
        ['High (>60%)', f"{distribution['high_pct']:.1f}%", 'Likely contenders'],
        ['Mean Probability', f"{distribution['mean_prob']*100:.1f}%", 'Average across field'],
        ['Std Deviation', f"{distribution['std_prob']:.3f}", 'Probability spread'],
        ['New Riders', f"{distribution['new_rider_count']}", 'No prior race history'],
        ['Field Size', f"{distribution['field_size']}", 'Total riders'],
    ]
    lines.extend(format_markdown_table(dist_headers, dist_rows, ['left', 'right', 'left']))

    # Determine pattern
    if distribution['mid_pct'] < 10:
        pattern = "BIMODAL"
        pattern_desc = "Model is decisive - clear separation between contenders and non-contenders"
    elif distribution['mid_pct'] > 20:
        pattern = "BALANCED"
        pattern_desc = "Model is uncertain - many riders in the 'maybe' zone"
    else:
        pattern = "MODERATE"
        pattern_desc = "Typical distribution with clear favorites and some uncertainty"

    lines.extend([
        "",
        f"**Pattern:** {pattern}",
        f"- {pattern_desc}",
        "",
        "**What this means:**",
        f"- {distribution['low_pct']:.0f}% of riders had <30% probability (clear non-contenders)",
        f"- {distribution['mid_pct']:.0f}% in the uncertain 30-60% range",
        f"- {distribution['high_pct']:.0f}% were predicted >60% (likely Top-10)",
        "",
    ])

    return lines


def _generate_validation_category_section(
    validation_results: dict,
    matched_df: pd.DataFrame,
    category: str,
    threshold: float
) -> list:
    """Generate markdown lines for a single category's validation results.

    Uses new template format with Hits@10, Hits@3, Spearman, MAE metrics.
    Includes metrics explanation, podium breakdown, and next-10 analysis.
    """
    lines = []

    # Extract metrics
    hits_10 = validation_results.get('hits_10', 0)
    hits_3 = validation_results.get('hits_3', 0)
    spearman = validation_results.get('spearman')
    mae_rank = validation_results.get('mae_rank')
    pred_top10_detail = validation_results.get('pred_top10_detail', [])
    pred_top3_detail = validation_results.get('pred_top3_detail', [])
    pred_next10_detail = validation_results.get('pred_next10_detail', [])

    # Legacy metrics values
    recall = validation_results.get('recall', 0)
    precision = validation_results.get('precision', 0)
    high_conf_accuracy = validation_results.get('high_conf_accuracy', 0)
    true_positives = validation_results.get('true_positives', 0)
    predicted_top10_count = validation_results.get('predicted_top10', 0)
    actual_top10_count = validation_results.get('actual_top10', 0)
    high_conf_count = validation_results.get('high_conf_count', 0)
    high_conf_correct_count = validation_results.get('high_conf_correct_count', 0)

    lines.extend([
        f"### {category} Results",
        f"",
    ])

    # ========== METRICS TABLE ==========
    metrics_headers = ['Metric', 'Value', 'Target']
    spearman_str = f"{spearman:.2f}" if spearman is not None else "N/A"
    mae_str = f"{mae_rank:.1f}" if mae_rank is not None else "N/A"

    metrics_rows = [
        ['**Hits@10**', f"{hits_10}/10", "7+"],
        ['**Hits@3**', f"{hits_3}/3", "2+"],
        ['**Spearman ρ**', spearman_str, ">0.5"],
        ['**MAE Rank**', mae_str, "<3"],
    ]
    lines.extend(format_markdown_table(metrics_headers, metrics_rows, ['left', 'center', 'center']))

    # ========== METRICS EXPLANATION + INTERPRETATION ==========
    lines.extend([
        f"",
        f"#### Metrics Interpretation",
        f"",
    ])

    # Hits@10 interpretation
    hits10_status = "✅ Met target" if hits_10 >= 7 else "❌ Below target"
    lines.append(f"- **Hits@10** ({hits_10}/10): How many of our top-10 predictions finished in actual top-10? {hits10_status}")

    # Hits@3 interpretation
    hits3_status = "✅ Met target" if hits_3 >= 2 else "❌ Below target"
    lines.append(f"- **Hits@3** ({hits_3}/3): How many of our podium picks made actual podium? {hits3_status}")

    # Spearman interpretation
    if spearman is not None:
        spearman_status = "✅ Met target" if spearman > 0.5 else "❌ Below target"
        if spearman > 0.7:
            spearman_interp = "Strong rank correlation"
        elif spearman > 0.5:
            spearman_interp = "Moderate rank correlation"
        elif spearman > 0.3:
            spearman_interp = "Weak rank correlation"
        else:
            spearman_interp = "Poor rank correlation"
        lines.append(f"- **Spearman ρ** ({spearman:.2f}): Rank correlation between predicted and actual order. {spearman_interp}. {spearman_status}")
    else:
        lines.append(f"- **Spearman ρ** (N/A): Insufficient matched riders to calculate correlation.")

    # MAE interpretation
    if mae_rank is not None:
        mae_status = "✅ Met target" if mae_rank < 3 else "❌ Below target"
        lines.append(f"- **MAE Rank** ({mae_rank:.1f}): On average, our predictions were {mae_rank:.1f} positions off from actual finish. {mae_status}")
    else:
        lines.append(f"- **MAE Rank** (N/A): No matched riders to calculate error.")

    # ========== TOP-10 BREAKDOWN ==========
    lines.extend([
        f"",
        f"#### Predicted Top-10 Breakdown",
        f"",
    ])

    breakdown_headers = ['Pred Rank', 'Rider', 'Probability', 'Actual', 'Result']
    breakdown_rows = []
    for detail in pred_top10_detail:
        pred_rank = detail['pred_rank']
        rider = detail['rider']
        prob = f"{detail['prob']:.1%}"
        actual = detail['actual_place']
        if isinstance(actual, int):
            actual_str = f"P{actual}"
            result = "✅" if detail['hit'] else "❌"
        else:
            actual_str = str(actual)
            result = "❌"
        breakdown_rows.append([str(pred_rank), rider, prob, actual_str, result])

    lines.extend(format_markdown_table(breakdown_headers, breakdown_rows, ['center', 'left', 'right', 'center', 'center']))

    # ========== PODIUM BREAKDOWN ==========
    lines.extend([
        f"",
        f"#### Predicted Podium Breakdown",
        f"",
        f"*Top 3 riders by Top-3 Probability*",
        f"",
    ])

    podium_headers = ['Pred Rank', 'Rider', 'Podium Prob', 'Actual', 'Result']
    podium_rows = []
    for detail in pred_top3_detail:
        pred_rank = detail['pred_rank']
        rider = detail['rider']
        prob = f"{detail['prob']:.1%}"
        actual = detail['actual_place']
        if isinstance(actual, int):
            actual_str = f"P{actual}"
            result = "✅" if detail['hit'] else "❌"
        else:
            actual_str = str(actual)
            result = "❌"
        podium_rows.append([str(pred_rank), rider, prob, actual_str, result])

    lines.extend(format_markdown_table(podium_headers, podium_rows, ['center', 'left', 'right', 'center', 'center']))

    # ========== NEXT 10 RIDERS (11-20) ==========
    lines.extend([
        f"",
        f"#### Next 10 Riders (Ranks 11-20)",
        f"",
        f"*How did our near-miss predictions perform?*",
        f"",
    ])

    next10_headers = ['Pred Rank', 'Rider', 'Probability', 'Actual', 'Made Top-10?']
    next10_rows = []
    surprises = []  # Track riders who outperformed predictions
    for detail in pred_next10_detail:
        pred_rank = detail['pred_rank']
        rider = detail['rider']
        prob = f"{detail['prob']:.1%}"
        actual = detail['actual_place']
        if isinstance(actual, int):
            actual_str = f"P{actual}"
            result = "✅ Yes!" if detail['hit'] else "No"
            if detail['hit']:
                surprises.append(f"{rider} (predicted #{pred_rank}, finished P{actual})")
        else:
            actual_str = str(actual)
            result = "No"
        next10_rows.append([str(pred_rank), rider, prob, actual_str, result])

    lines.extend(format_markdown_table(next10_headers, next10_rows, ['center', 'left', 'right', 'center', 'center']))

    # Highlight any surprises
    if surprises:
        lines.extend([
            f"",
            f"**Surprises:** {', '.join(surprises)}",
        ])

    # ========== LEGACY METRICS WITH CALCULATIONS ==========
    lines.extend([
        f"",
        f"#### Legacy Metrics (Threshold-based)",
        f"",
        f"*Using {threshold:.0%} confidence threshold*",
        f"",
    ])

    legacy_headers = ['Metric', 'Value', 'Calculation']
    legacy_rows = [
        ['Recall', f"{recall:.1%}", f"{true_positives} correct / {actual_top10_count} actual top-10"],
        ['Precision', f"{precision:.1%}", f"{true_positives} correct / {predicted_top10_count} predictions above threshold"],
        ['High Conf Accuracy', f"{high_conf_accuracy:.1%}", f"{high_conf_correct_count} correct / {high_conf_count} predictions >70%"],
    ]
    lines.extend(format_markdown_table(legacy_headers, legacy_rows, ['left', 'center', 'left']))

    # ========== ACTUAL TOP-20 RESULTS ==========
    actual_top20_detail = validation_results.get('actual_top20_detail', [])
    if actual_top20_detail:
        lines.extend([
            f"",
            f"#### Actual Top-20 Results",
            f"",
            f"*How the race actually unfolded vs our predictions*",
            f"",
        ])

        actual_headers = ['Pos', 'Rider', 'Our Prob', 'Our Rank', 'Rank Error', 'Status']
        actual_rows = []
        for detail in actual_top20_detail:
            pos = f"P{detail['actual_place']}"
            rider = detail['rider']
            prob = f"{detail['prob']:.1%}" if detail['prob'] is not None else "N/A"
            pred_rank = f"#{detail['pred_rank']}" if detail['pred_rank'] is not None else "N/A"

            if detail['rank_error'] is not None:
                error = detail['rank_error']
                if error > 0:
                    error_str = f"+{error}"  # We underestimated them
                elif error < 0:
                    error_str = str(error)  # We overestimated them
                else:
                    error_str = "0"  # Perfect
            else:
                error_str = "N/A"

            status = detail['status']
            actual_rows.append([pos, rider, prob, pred_rank, error_str, status])

        lines.extend(format_markdown_table(actual_headers, actual_rows, ['center', 'left', 'right', 'center', 'center', 'left']))

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

    Supports two formats:
    1. Simple: racename_category_date.csv (e.g., namur_men_elite_2025-12-14.csv)
    2. Structured: Startlist__Series__City__Category__Date.csv
       (e.g., Startlist__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv)
    """
    stem = filepath.stem

    # Extract date
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", stem)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # Extract category
    stem_lower = stem.lower()
    if "women" in stem_lower:
        category = "Women Elite"
    elif "men" in stem_lower:
        category = "Men Elite"
    else:
        category = "Men Elite"

    # Check for structured format: Startlist__Series__City__Category__Date
    if "__" in stem:
        parts = stem.split("__")
        # parts[0] = "Startlist", parts[1] = series, parts[2] = city, parts[3] = category, parts[4] = date
        if len(parts) >= 3:
            series = parts[1].replace("-", " ") if len(parts) > 1 else "UCI World Cup"
            race_name = parts[2] if len(parts) > 2 else "Unknown"
            return {
                "race_name": race_name,
                "category": category,
                "date": date,
                "series": series
            }

    # Fallback: Simple format (first part before category)
    parts = stem_lower.replace(date, "").strip("_").split("_")
    race_name = parts[0].title() if parts else "Unknown"

    return {
        "race_name": race_name,
        "category": category,
        "date": date,
        "series": "UCI World Cup"  # Default for simple format
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

    predictions, distribution = predict_race(
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
    category_slug = meta['category'].lower().replace(' ', '_')
    race_id = f"{race_date.strftime('%Y%m%d')}_{meta['series'].lower().replace(' ', '-')}_{meta['race_name'].lower()}_{category_slug}_{meta['location'].lower()}"

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
    After successful retrain, updates:
    - SEASON_TRACKER.md with new version
    - VERSION_HISTORY.md Evolution Overview table
    - VERSION_HISTORY.md Training Metrics table
    """
    print(f"=" * 70)
    print(f"VELOPREDICT PIPELINE: RETRAIN")
    print(f"=" * 70)

    import subprocess
    result = subprocess.run(
        [sys.executable, "train_model_v2.py"],
        capture_output=False
    )

    if result.returncode == 0:
        # Load updated metadata
        metadata_path = config.MODELS_DIR / "model_metadata.json"
        registry = load_registry()

        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)

            # Get current version from registry and calculate NEW version
            old_version = registry.get("current_version", "v6.4")
            accuracy = metadata.get("top10_accuracy", 0) * 100
            auc = metadata.get("top10_auc", 0)
            observations = metadata.get("total_observations", 0)
            total_races = metadata.get("total_races", 0)
            training_date = metadata.get("training_date", "")

            # Calculate new version by incrementing minor version
            # e.g., v6.8 -> v6.9, v6.9 -> v6.10
            version_match = re.match(r'v(\d+)\.(\d+)', old_version)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                new_version = f"v{major}.{minor + 1}"
            else:
                new_version = "v6.5"  # fallback

            print(f"\n[VERSION BUMP] {old_version} → {new_version}")

            # Determine innovation description from recent changes
            # This is based on what was just added - look for recent race in registry
            innovation = "+Results"
            race_date = datetime.now().strftime("%Y-%m-%d")
            race_name = "Unknown"

            # Try to find the most recent validated race
            if "races" in registry:
                races = registry.get("races", [])
                # races is a list of dicts, not a dict
                validated_races = [r for r in races if r.get("validation")]
                recent_races = sorted(
                    validated_races,
                    key=lambda x: x.get("date", ""),
                    reverse=True
                )
                if recent_races:
                    recent_race = recent_races[0]
                    race_name = recent_race.get("name", "Unknown")
                    race_date = recent_race.get("date", race_date)
                    innovation = f"+{race_name} Results"

            # Update registry with new version
            update_model_version(new_version, accuracy / 100, auc, observations, innovation)
            print(f"  Updated registry to {new_version}")

            # Update SEASON_TRACKER.md with new model version (header + footer)
            update_tracker_model_version(new_version)

            # Update VERSION_HISTORY.md tables
            print(f"\n[AUTO-UPDATE] Updating VERSION_HISTORY.md tables...")

            # Update Evolution Overview
            update_evolution_overview_table(
                model_version=new_version,
                race_date=race_date,
                innovation=innovation,
                accuracy=accuracy,
                validation_notes="Pending"
            )

            # Update Training Metrics
            update_training_metrics_table(
                model_version=new_version,
                accuracy=accuracy,
                auc=auc,
                observations=observations,
                innovation=innovation
            )

            # Update SEASON_TRACKER.md Model Version History table
            print(f"\n[AUTO-UPDATE] Updating SEASON_TRACKER.md Model Version History...")
            update_season_tracker_version_table(
                model_version=new_version,
                innovation=innovation,
                accuracy=accuracy,
                auc=auc,
                observations=observations,
                notes=f"Current - Post {race_name}"
            )

            # Update SEASON_TRACKER.md Retraining History table
            print(f"[AUTO-UPDATE] Updating SEASON_TRACKER.md Retraining History...")
            update_retraining_history_table(new_version, race_date, innovation, observations, race_name)

    return result.returncode == 0


# ============================================================
# NEW METRICS: Hits@10, Hits@3, Spearman, MAE
# ============================================================

def calculate_new_metrics(pred_df: pd.DataFrame, results_df: pd.DataFrame) -> dict:
    """
    Calculate new-style metrics for prediction validation.

    Args:
        pred_df: Predictions DataFrame with 'Rider', 'Top-10 Probability', 'Top-3 Probability'
        results_df: Results DataFrame with 'rider_std', 'Place'

    Returns:
        dict with:
        - hits_10: How many of top-10 predictions finished in actual top-10
        - hits_3: How many of top-3 predictions made actual podium
        - spearman: Rank correlation between predicted and actual order
        - mae_rank: Mean absolute error of rank positions
        - pred_top10_detail: Detailed breakdown of each prediction
    """
    # Standardize prediction names
    pred_df = pred_df.copy()
    pred_df['rider_std'] = pred_df['Rider'].apply(standardize_name)

    # Get top-10 predictions by probability
    pred_top10 = pred_df.nlargest(10, 'Top-10 Probability')
    pred_top10_names = set(pred_top10['rider_std'])

    # Get top-3 predictions by podium probability
    top3_col = 'Top-3 Probability' if 'Top-3 Probability' in pred_df.columns else 'Top-10 Probability'
    pred_top3 = pred_df.nlargest(3, top3_col)
    pred_top3_names = set(pred_top3['rider_std'])

    # Get actual top-10 and top-3
    actual_top10 = results_df[results_df['Place'] <= 10]
    actual_top10_names = set(actual_top10['rider_std'])

    actual_top3 = results_df[results_df['Place'] <= 3]
    actual_top3_names = set(actual_top3['rider_std'])

    # Calculate Hits@10 and Hits@3
    hits_10 = len(pred_top10_names & actual_top10_names)
    hits_3 = len(pred_top3_names & actual_top3_names)

    # For Spearman correlation, match predicted ranks with actual ranks
    pred_ranks = {}
    for idx, (_, row) in enumerate(pred_top10.iterrows(), 1):
        pred_ranks[row['rider_std']] = idx

    actual_ranks = {}
    for _, row in results_df.iterrows():
        if pd.notna(row['Place']):
            actual_ranks[row['rider_std']] = int(row['Place'])

    # Find common riders between predicted top-10 and results
    common = set(pred_ranks.keys()) & set(actual_ranks.keys())

    if len(common) >= 2:
        pred_r = [pred_ranks[n] for n in common]
        actual_r = [actual_ranks[n] for n in common]
        spearman, _ = stats.spearmanr(pred_r, actual_r)
        spearman = round(spearman, 2) if not np.isnan(spearman) else None
    else:
        spearman = None

    # MAE on rank for predicted top-10 that finished
    mae_values = []
    for name_std in pred_top10_names:
        pred_rank = pred_ranks.get(name_std)
        if name_std in actual_ranks:
            actual_rank = actual_ranks[name_std]
            mae_values.append(abs(pred_rank - actual_rank))

    mae_rank = round(np.mean(mae_values), 1) if mae_values else None

    # Detailed breakdown for top-10
    pred_top10_detail = []
    for idx, (_, row) in enumerate(pred_top10.iterrows(), 1):
        name_std = row['rider_std']
        actual_place = actual_ranks.get(name_std, 'DNF/DNS')
        in_top10 = actual_place <= 10 if isinstance(actual_place, (int, float)) else False
        pred_top10_detail.append({
            'pred_rank': idx,
            'rider': row['Rider'],
            'prob': row['Top-10 Probability'],
            'actual_place': actual_place,
            'hit': in_top10
        })

    # Detailed breakdown for podium (top-3 by Top-3 Probability)
    pred_top3_detail = []
    for idx, (_, row) in enumerate(pred_top3.iterrows(), 1):
        name_std = row['rider_std']
        actual_place = actual_ranks.get(name_std, 'DNF/DNS')
        in_top3 = actual_place <= 3 if isinstance(actual_place, (int, float)) else False
        pred_top3_detail.append({
            'pred_rank': idx,
            'rider': row['Rider'],
            'prob': row[top3_col],
            'actual_place': actual_place,
            'hit': in_top3
        })

    # Next 10 riders (ranks 11-20 by Top-10 Probability)
    pred_next10 = pred_df.nlargest(20, 'Top-10 Probability').tail(10)
    pred_next10_detail = []
    for idx, (_, row) in enumerate(pred_next10.iterrows(), 11):
        name_std = row['rider_std']
        actual_place = actual_ranks.get(name_std, 'DNF/DNS')
        in_top10 = actual_place <= 10 if isinstance(actual_place, (int, float)) else False
        pred_next10_detail.append({
            'pred_rank': idx,
            'rider': row['Rider'],
            'prob': row['Top-10 Probability'],
            'actual_place': actual_place,
            'hit': in_top10  # Did they actually make top-10?
        })

    # Actual Top-20 results with our predictions
    # Create a lookup from rider_std to prediction info
    pred_lookup = {}
    for idx, (_, row) in enumerate(pred_df.sort_values('Top-10 Probability', ascending=False).iterrows(), 1):
        pred_lookup[row['rider_std']] = {
            'pred_rank': idx,
            'prob': row['Top-10 Probability']
        }

    actual_top20 = results_df[results_df['Place'] <= 20].sort_values('Place')
    actual_top20_detail = []
    for _, row in actual_top20.iterrows():
        name_std = row['rider_std']
        actual_place = int(row['Place'])
        pred_info = pred_lookup.get(name_std, {'pred_rank': None, 'prob': None})
        pred_rank = pred_info['pred_rank']
        prob = pred_info['prob']

        # Calculate rank error (positive = we underestimated them)
        if pred_rank is not None:
            rank_error = pred_rank - actual_place
        else:
            rank_error = None

        # Determine status
        if pred_rank is not None and pred_rank <= 10 and actual_place <= 10:
            status = "✅ Hit"
        elif pred_rank is not None and pred_rank > 10 and actual_place <= 10:
            status = "📈 Surprise"
        elif pred_rank is not None and pred_rank <= 10 and actual_place > 10:
            status = "📉 Miss"
        elif pred_rank is None:
            status = "❓ Unknown"
        else:
            status = ""

        # Get rider name from results (may need to find original name)
        rider_name = row.get('Name', name_std)
        if pd.isna(rider_name):
            rider_name = name_std

        actual_top20_detail.append({
            'actual_place': actual_place,
            'rider': rider_name,
            'rider_std': name_std,
            'prob': prob,
            'pred_rank': pred_rank,
            'rank_error': rank_error,
            'status': status
        })

    return {
        'hits_10': hits_10,
        'hits_3': hits_3,
        'spearman': spearman,
        'mae_rank': mae_rank,
        'pred_top10_detail': pred_top10_detail,
        'pred_top3_detail': pred_top3_detail,
        'pred_next10_detail': pred_next10_detail,
        'actual_top20_detail': actual_top20_detail,
        'pred_top3_names': list(pred_top3['Rider']),
        'actual_top3_names': [r for r in results_df[results_df['Place'] <= 3]['rider_std'].tolist()]
    }


# ============================================================
# DISTRIBUTION METRICS
# ============================================================

def calculate_distribution_metrics(predictions_df: pd.DataFrame, threshold: float = None) -> dict:
    """
    Calculate probability distribution metrics for a set of predictions.

    These metrics help understand model confidence patterns:
    - Bimodal distribution (most low + some high, empty middle) = decisive model
    - Balanced distribution (spread across all buckets) = uncertain model

    Args:
        predictions_df: DataFrame with 'Top-10 Probability' column
        threshold: Confidence threshold (defaults to config)

    Returns:
        dict with distribution metrics:
        - low_pct: % of riders with <30% probability
        - mid_pct: % of riders with 30-60% probability
        - high_pct: % of riders with >60% probability
        - mean_prob: Average probability across all riders
        - std_prob: Standard deviation of probabilities
        - new_rider_count: Number of new riders (is_new_rider=1 or Status='new_rider')
        - field_size: Total number of riders
    """
    if threshold is None:
        threshold = config.CONFIDENCE_THRESHOLD

    # Get probabilities
    if 'Top-10 Probability' in predictions_df.columns:
        probs = predictions_df['Top-10 Probability'].dropna()
    elif 'prob' in predictions_df.columns:
        probs = predictions_df['prob'].dropna()
    else:
        return None

    if len(probs) == 0:
        return None

    # Count buckets
    low_count = (probs < 0.30).sum()
    mid_count = ((probs >= 0.30) & (probs <= 0.60)).sum()
    high_count = (probs > 0.60).sum()
    total = len(probs)

    # Calculate percentages
    low_pct = round(low_count / total * 100, 1)
    mid_pct = round(mid_count / total * 100, 1)
    high_pct = round(high_count / total * 100, 1)

    # Calculate statistics
    mean_prob = round(probs.mean(), 3)
    std_prob = round(probs.std(), 3)

    # Count new riders
    new_rider_count = 0
    if 'is_new_rider' in predictions_df.columns:
        new_rider_count = int(predictions_df['is_new_rider'].sum())
    elif 'Status' in predictions_df.columns:
        new_rider_count = int((predictions_df['Status'] == 'new_rider').sum())

    return {
        'low_pct': low_pct,
        'mid_pct': mid_pct,
        'high_pct': high_pct,
        'mean_prob': mean_prob,
        'std_prob': std_prob,
        'new_rider_count': new_rider_count,
        'field_size': total
    }


def calculate_distribution_from_files(predictions_path: str, results_path: str = None) -> dict:
    """
    Calculate distribution metrics from prediction and optionally result files.

    If results_path is provided, merges predictions with results to get
    complete picture including actual positions.

    Args:
        predictions_path: Path to predictions CSV
        results_path: Optional path to results CSV

    Returns:
        dict with distribution metrics
    """
    predictions_path = Path(predictions_path)

    if not predictions_path.exists():
        print(f"Warning: Predictions file not found: {predictions_path}")
        return None

    pred_df = pd.read_csv(predictions_path)

    return calculate_distribution_metrics(pred_df)


def update_registry_distribution(race_id: str, distribution: dict):
    """
    Add distribution metrics to a race's validation block in the registry.

    Args:
        race_id: Race ID (e.g., 'namur_2025-12-14')
        distribution: Distribution metrics dict from calculate_distribution_metrics
    """
    registry = load_registry()

    for race in registry["races"]:
        if race["id"] == race_id:
            if "validation" not in race:
                race["validation"] = {}
            race["validation"]["distribution"] = distribution
            save_registry(registry)
            print(f"  Updated distribution for {race_id}")
            return True

    print(f"  Warning: Race {race_id} not found in registry")
    return False


def update_validation_reports_with_distribution():
    """
    Update existing validation markdown reports with distribution sections.

    Reads distribution data from registry and appends to validation reports.
    """
    print("=" * 70)
    print("UPDATING VALIDATION REPORTS WITH DISTRIBUTION")
    print("=" * 70)

    registry = load_registry()
    updated_count = 0

    for race in registry["races"]:
        race_name = race["name"]
        distribution = race.get("validation", {}).get("distribution")

        if not distribution:
            print(f"\n{race_name}: No distribution data in registry, skipping")
            continue

        report_path = config.PROJECT_ROOT / f"{race_name.upper()}_VALIDATION_RESULTS.md"

        if not report_path.exists():
            print(f"\n{race_name}: Validation report not found at {report_path}")
            continue

        # Read existing report
        with open(report_path, 'r') as f:
            content = f.read()

        # Check if distribution section already exists
        if "## Probability Distribution Analysis" in content:
            print(f"\n{race_name}: Distribution section already exists, skipping")
            continue

        # Generate distribution section
        dist_lines = _generate_distribution_section(distribution)
        dist_section = '\n'.join(dist_lines)

        # Find where to insert (before the footer or at the end)
        footer_marker = "---\n\n*Generated by"
        if footer_marker in content:
            parts = content.rsplit(footer_marker, 1)
            updated_content = parts[0] + "---\n\n" + dist_section + footer_marker + parts[1]
        else:
            # No footer, append at end
            updated_content = content + "\n---\n\n" + dist_section

        # Write updated report
        with open(report_path, 'w') as f:
            f.write(updated_content)

        print(f"\n{race_name}: Added distribution section")
        updated_count += 1

    print(f"\n{'=' * 70}")
    print(f"Updated {updated_count} validation reports")
    print(f"{'=' * 70}")

    return updated_count


def update_prediction_reports_with_distribution():
    """
    Update existing prediction markdown reports with distribution sections.

    Reads distribution data from registry (or calculates from prediction CSVs)
    and appends to prediction report files (e.g., NAMUR_PREDICTIONS.md).
    """
    print("=" * 70)
    print("UPDATING PREDICTION REPORTS WITH DISTRIBUTION")
    print("=" * 70)

    registry = load_registry()
    updated_count = 0

    for race in registry["races"]:
        race_name = race["name"]

        # Try to get distribution from registry validation block first
        distribution = race.get("validation", {}).get("distribution")

        # If not in registry, calculate from prediction files
        if not distribution:
            print(f"\n{race_name}: Calculating distribution from prediction files...")
            all_probs = []
            new_rider_total = 0

            for category, pred_path in race.get("predictions", {}).items():
                full_path = config.PROJECT_ROOT / pred_path
                if full_path.exists():
                    pred_df = pd.read_csv(full_path)
                    if 'Top-10 Probability' in pred_df.columns:
                        all_probs.extend(pred_df['Top-10 Probability'].dropna().tolist())
                    if 'Status' in pred_df.columns:
                        new_rider_total += (pred_df['Status'] == 'new_rider').sum()

            if all_probs:
                probs = pd.Series(all_probs)
                low_count = (probs < 0.30).sum()
                mid_count = ((probs >= 0.30) & (probs <= 0.60)).sum()
                high_count = (probs > 0.60).sum()
                total = len(probs)

                distribution = {
                    'low_pct': round(low_count / total * 100, 1),
                    'mid_pct': round(mid_count / total * 100, 1),
                    'high_pct': round(high_count / total * 100, 1),
                    'mean_prob': round(probs.mean(), 3),
                    'std_prob': round(probs.std(), 3),
                    'new_rider_count': int(new_rider_total),
                    'field_size': total
                }

        if not distribution:
            print(f"\n{race_name}: No distribution data available, skipping")
            continue

        # Check multiple possible prediction report filenames
        possible_names = [
            f"{race_name.upper()}_PREDICTIONS.md",
            f"{race_name.upper()}_PREDICTIONS_{race['date']}.md",
            f"{race_name.upper().replace(' ', '-')}_PREDICTIONS.md",
        ]

        report_path = None
        for name in possible_names:
            candidate = config.PROJECT_ROOT / name
            if candidate.exists():
                report_path = candidate
                break

        if not report_path:
            print(f"\n{race_name}: No prediction report found, skipping")
            continue

        # Read existing report
        with open(report_path, 'r') as f:
            content = f.read()

        # Check if distribution section already exists
        if "## Probability Distribution Analysis" in content:
            print(f"\n{race_name}: Distribution section already exists, skipping")
            continue

        # Generate distribution section
        dist_lines = _generate_distribution_section(distribution)
        dist_section = '\n'.join(dist_lines)

        # Find where to insert - prefer before "Understanding the Metrics" or footer
        metrics_marker = "---\n\n## Understanding the Metrics"
        footer_marker = "---\n\n*Generated by"
        alt_footer = "---\n\n*Predictions generated"

        if metrics_marker in content:
            parts = content.split(metrics_marker, 1)
            updated_content = parts[0] + "---\n\n" + dist_section + metrics_marker + parts[1]
        elif footer_marker in content:
            parts = content.rsplit(footer_marker, 1)
            updated_content = parts[0] + "---\n\n" + dist_section + footer_marker + parts[1]
        elif alt_footer in content:
            parts = content.rsplit(alt_footer, 1)
            updated_content = parts[0] + "---\n\n" + dist_section + alt_footer + parts[1]
        else:
            # No known marker, append at end with separator
            updated_content = content.rstrip() + "\n\n---\n\n" + dist_section

        # Write updated report
        with open(report_path, 'w') as f:
            f.write(updated_content)

        print(f"\n{race_name}: Added distribution section to {report_path.name}")
        updated_count += 1

    print(f"\n{'=' * 70}")
    print(f"Updated {updated_count} prediction reports")
    print(f"{'=' * 70}")

    return updated_count


def backfill_distribution_metrics():
    """
    Calculate and store distribution metrics for all races in registry.

    This is a one-time operation to populate existing races with
    the new distribution metrics.
    """
    print("=" * 70)
    print("BACKFILLING DISTRIBUTION METRICS")
    print("=" * 70)

    registry = load_registry()
    updated_count = 0

    for race in registry["races"]:
        race_id = race["id"]
        race_name = race["name"]

        print(f"\n{race_name} ({race_id}):")

        # Collect all prediction files for this race
        all_probs = []
        new_rider_total = 0

        for category, pred_path in race.get("predictions", {}).items():
            full_path = config.PROJECT_ROOT / pred_path

            if not full_path.exists():
                print(f"  {category}: File not found: {pred_path}")
                continue

            pred_df = pd.read_csv(full_path)
            print(f"  {category}: {len(pred_df)} riders")

            # Collect probabilities
            if 'Top-10 Probability' in pred_df.columns:
                all_probs.extend(pred_df['Top-10 Probability'].dropna().tolist())

            # Count new riders
            if 'Status' in pred_df.columns:
                new_rider_total += (pred_df['Status'] == 'new_rider').sum()

        if not all_probs:
            print(f"  No prediction data found")
            continue

        # Calculate combined distribution
        probs = pd.Series(all_probs)

        low_count = (probs < 0.30).sum()
        mid_count = ((probs >= 0.30) & (probs <= 0.60)).sum()
        high_count = (probs > 0.60).sum()
        total = len(probs)

        distribution = {
            'low_pct': round(low_count / total * 100, 1),
            'mid_pct': round(mid_count / total * 100, 1),
            'high_pct': round(high_count / total * 100, 1),
            'mean_prob': round(probs.mean(), 3),
            'std_prob': round(probs.std(), 3),
            'new_rider_count': int(new_rider_total),
            'field_size': total
        }

        print(f"  Distribution: Low {distribution['low_pct']}% | Mid {distribution['mid_pct']}% | High {distribution['high_pct']}%")
        print(f"  Mean prob: {distribution['mean_prob']:.1%} | Std: {distribution['std_prob']:.3f}")
        print(f"  New riders: {distribution['new_rider_count']} | Field size: {distribution['field_size']}")

        # Update registry
        if "validation" not in race:
            race["validation"] = {}
        race["validation"]["distribution"] = distribution
        updated_count += 1

    # Save updated registry
    save_registry(registry)
    print(f"\n{'=' * 70}")
    print(f"Updated {updated_count} races with distribution metrics")
    print(f"{'=' * 70}")

    return updated_count


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
        def clean_result_name(x):
            if pd.isna(x):
                return None
            name = str(x).strip()
            # Only apply title() for newline-separated names (e.g., "FIRSTNAME\nLASTNAME")
            if '\n' in name:
                parts = name.split('\n')
                # Reconstruct as "LASTNAME Firstname"
                if len(parts) == 2:
                    firstname = parts[0].strip().title()
                    lastname = parts[1].strip().upper()
                    name = f"{lastname} {firstname}"
                else:
                    name = name.replace('\n', ' ')
            return standardize_name(name)

        results_df['rider_std'] = results_df['Name'].apply(clean_result_name)
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

    # Calculate distribution metrics from matched predictions
    distribution = calculate_distribution_metrics(df)

    if distribution:
        print(f"\n📊 DISTRIBUTION ANALYSIS:")
        print(f"  Low (<30%):   {distribution['low_pct']:.1f}% of field")
        print(f"  Mid (30-60%): {distribution['mid_pct']:.1f}% of field")
        print(f"  High (>60%):  {distribution['high_pct']:.1f}% of field")
        print(f"  Mean prob:    {distribution['mean_prob']:.1%}")
        print(f"  Field size:   {distribution['field_size']}")

        # Interpret distribution pattern
        if distribution['mid_pct'] < 10:
            print(f"  Pattern: BIMODAL (decisive - model is confident)")
        elif distribution['mid_pct'] > 20:
            print(f"  Pattern: BALANCED (uncertain - more mid-tier riders)")
        else:
            print(f"  Pattern: MODERATE (typical distribution)")

    # Calculate new metrics (Hits@10, Hits@3, Spearman, MAE)
    # Need results_df with rider_std column
    results_df_with_std = results_df.copy()
    if 'rider_std' not in results_df_with_std.columns:
        if 'Name' in results_df_with_std.columns:
            results_df_with_std['rider_std'] = results_df_with_std['Name'].apply(
                lambda x: standardize_name(str(x).replace('\n', ' ').title()) if pd.notna(x) else None
            )
        else:
            results_df_with_std['rider_std'] = results_df_with_std['rider_name'].apply(standardize_name)

    new_metrics = calculate_new_metrics(pred_df, results_df_with_std)

    print(f"\n🎯 NEW METRICS (Hits-based):")
    print(f"  Hits@10:    {new_metrics['hits_10']}/10")
    print(f"  Hits@3:     {new_metrics['hits_3']}/3")
    if new_metrics['spearman'] is not None:
        print(f"  Spearman ρ: {new_metrics['spearman']:.2f}")
    else:
        print(f"  Spearman ρ: N/A (insufficient data)")
    if new_metrics['mae_rank'] is not None:
        print(f"  MAE Rank:   {new_metrics['mae_rank']:.1f}")
    else:
        print(f"  MAE Rank:   N/A")

    print(f"\n📋 TOP-10 PREDICTION BREAKDOWN:")
    for detail in new_metrics['pred_top10_detail']:
        status = "✅" if detail['hit'] else "❌"
        place_str = f"P{detail['actual_place']}" if isinstance(detail['actual_place'], int) else detail['actual_place']
        print(f"  {status} #{detail['pred_rank']:2d} {detail['rider']:25s} ({detail['prob']:.1%}) → {place_str}")

    # Count high-conf predictions for legacy metrics explanation
    high_conf_count = len(high_conf)
    high_conf_correct_count = high_conf_correct

    return {
        'recall': recall,
        'precision': precision,
        'high_conf_accuracy': high_conf_accuracy,
        'podium_accuracy': podium_accuracy,
        'matched': len(df),
        'predicted_top10': len(predicted_top10),
        'actual_top10': len(actual_top10),
        'true_positives': true_positives,
        'high_conf_count': high_conf_count,
        'high_conf_correct_count': high_conf_correct_count,
        'distribution': distribution,
        'hits_10': new_metrics['hits_10'],
        'hits_3': new_metrics['hits_3'],
        'spearman': new_metrics['spearman'],
        'mae_rank': new_metrics['mae_rank'],
        'pred_top10_detail': new_metrics['pred_top10_detail'],
        'pred_top3_detail': new_metrics['pred_top3_detail'],
        'pred_next10_detail': new_metrics['pred_next10_detail'],
        'actual_top20_detail': new_metrics['actual_top20_detail']
    }


def update_registry_validation(race_id: str, category: str, validation_results: dict):
    """
    Update the race registry with validation results including new metrics.

    Args:
        race_id: Race ID (e.g., 'antwerpen_2025-12-20')
        category: Category name (e.g., 'Men Elite')
        validation_results: Dict from validate() with all metrics
    """
    registry = load_registry()

    for race in registry["races"]:
        if race["id"] == race_id:
            if "validation" not in race:
                race["validation"] = {}

            # Store per-category validation
            cat_key = category.lower().replace(" ", "_")
            race["validation"][cat_key] = {
                "precision": round(validation_results['precision'] * 100, 1),
                "recall": round(validation_results['recall'] * 100, 1),
                "high_conf_accuracy": round(validation_results['high_conf_accuracy'] * 100, 1) if validation_results['high_conf_accuracy'] else None,
                "hits_10": validation_results['hits_10'],
                "hits_3": validation_results['hits_3'],
                "spearman": validation_results['spearman'],
                "mae_rank": validation_results['mae_rank']
            }

            # Store distribution if available
            if validation_results.get('distribution'):
                race["validation"]["distribution"] = validation_results['distribution']

            save_registry(registry)
            print(f"  Updated registry validation for {race_id} ({category})")
            return True

    print(f"  Warning: Race {race_id} not found in registry")
    return False


def validate_ltr_predictions(ltr_predictions_path: str, results_path: str) -> dict:
    """
    Validate LTR predictions against results.
    Returns dict with hits_10, hits_3, spearman, mae_rank.
    """
    ltr_pred_df = pd.read_csv(ltr_predictions_path)
    results_df = pd.read_csv(results_path)

    # Standardize column names
    if 'Position' in results_df.columns:
        results_df = results_df.rename(columns={'Position': 'Place'})

    # Get rider column from LTR predictions
    rider_col = 'Rider' if 'Rider' in ltr_pred_df.columns else 'rider'
    score_col = 'LTR Score' if 'LTR Score' in ltr_pred_df.columns else 'ltr_score'

    # Standardize names
    ltr_pred_df['rider_std'] = ltr_pred_df[rider_col].apply(standardize_name)

    if 'Name' in results_df.columns:
        results_df['rider_std'] = results_df['Name'].apply(lambda x: standardize_name(str(x)) if pd.notna(x) else None)
    else:
        results_df['rider_std'] = results_df.iloc[:, 1].apply(lambda x: standardize_name(str(x)) if pd.notna(x) else None)

    # Sort LTR predictions by score (descending) and take top 10
    ltr_pred_df = ltr_pred_df.sort_values(score_col, ascending=False)
    top10_ltr = ltr_pred_df.head(10)
    top3_ltr = ltr_pred_df.head(3)

    # Get actual top 10 and top 3
    results_df['Place'] = pd.to_numeric(results_df['Place'], errors='coerce')
    actual_top10 = set(results_df[results_df['Place'] <= 10]['rider_std'].dropna().tolist())
    actual_top3 = set(results_df[results_df['Place'] <= 3]['rider_std'].dropna().tolist())

    # Calculate hits
    predicted_top10 = set(top10_ltr['rider_std'].tolist())
    predicted_top3 = set(top3_ltr['rider_std'].tolist())

    hits_10 = len(predicted_top10 & actual_top10)
    hits_3 = len(predicted_top3 & actual_top3)

    # Calculate Spearman and MAE for predicted riders
    pred_ranks = []
    actual_ranks = []
    rank_diffs = []

    for i, row in top10_ltr.iterrows():
        rider_std = row['rider_std']
        pred_rank = list(top10_ltr['rider_std']).index(rider_std) + 1

        # Find actual rank
        actual_row = results_df[results_df['rider_std'] == rider_std]
        if len(actual_row) > 0 and pd.notna(actual_row['Place'].iloc[0]):
            actual_rank = int(actual_row['Place'].iloc[0])
            pred_ranks.append(pred_rank)
            actual_ranks.append(actual_rank)
            rank_diffs.append(abs(pred_rank - actual_rank))

    # Spearman correlation
    if len(pred_ranks) >= 3:
        from scipy import stats
        spearman, _ = stats.spearmanr(pred_ranks, actual_ranks)
    else:
        spearman = 0.0

    # MAE
    mae_rank = sum(rank_diffs) / len(rank_diffs) if rank_diffs else 10.0

    return {
        'hits_10': hits_10,
        'hits_3': hits_3,
        'spearman': round(spearman, 2) if not pd.isna(spearman) else 0.0,
        'mae_rank': round(mae_rank, 1)
    }


def update_ltr_experiment(race_name: str, race_date: str, series: str, category: str,
                          v6_results: dict, ltr_results: dict, v6_model: str = "v6.10"):
    """
    Update LTR_EXPERIMENT.md and ltr_validation_results.json with new validation.
    """
    from update_ltr_experiment import add_validation

    add_validation(
        race=race_name,
        date=race_date,
        series=series,
        category=category,
        v6_model=v6_model,
        v6_hits10=v6_results['hits_10'],
        v6_hits3=v6_results['hits_3'],
        v6_spearman=v6_results['spearman'],
        v6_mae=v6_results['mae_rank'],
        ltr_hits10=ltr_results['hits_10'],
        ltr_hits3=ltr_results['hits_3'],
        ltr_spearman=ltr_results['spearman'],
        ltr_mae=ltr_results['mae_rank']
    )


def generate_ltr_validation_report(race_name: str, race_date: str, category: str,
                                    v6_results: dict, ltr_results: dict,
                                    ltr_pred_df: pd.DataFrame, results_df: pd.DataFrame) -> str:
    """
    Generate or update LTR validation report markdown.
    """
    report_filename = f"{race_name.upper()}_LTR_PREDICTIONS_{race_date}.md"
    report_path = config.PROJECT_ROOT / report_filename

    # Determine winner for each metric
    def winner(ltr_val, v6_val, lower_is_better=False):
        if lower_is_better:
            if ltr_val < v6_val:
                return "LTR", f"**{ltr_val}**", str(v6_val)
            elif v6_val < ltr_val:
                return "v6.x", str(ltr_val), f"**{v6_val}**"
        else:
            if ltr_val > v6_val:
                return "LTR", f"**{ltr_val}**", str(v6_val)
            elif v6_val > ltr_val:
                return "v6.x", str(ltr_val), f"**{v6_val}**"
        return "TIE", str(ltr_val), str(v6_val)

    h10_winner, ltr_h10, v6_h10 = winner(ltr_results['hits_10'], v6_results['hits_10'])
    h3_winner, ltr_h3, v6_h3 = winner(ltr_results['hits_3'], v6_results['hits_3'])
    sp_winner, ltr_sp, v6_sp = winner(ltr_results['spearman'], v6_results['spearman'])
    mae_winner, ltr_mae, v6_mae = winner(ltr_results['mae_rank'], v6_results['mae_rank'], lower_is_better=True)

    # Count wins
    ltr_wins = sum(1 for w in [h10_winner, h3_winner, sp_winner, mae_winner] if w == "LTR")
    v6_wins = sum(1 for w in [h10_winner, h3_winner, sp_winner, mae_winner] if w == "v6.x")
    ties = sum(1 for w in [h10_winner, h3_winner, sp_winner, mae_winner] if w == "TIE")

    overall_winner = "LTR" if ltr_wins > v6_wins else ("v6.x" if v6_wins > ltr_wins else "TIE")

    cat_abbrev = "Men" if "men" in category.lower() else "Women"

    validation_section = f"""
---

## {category} Validation Results

|    Metric     | v6.x  | v7.1-LTR |  Winner   |
|:-------------:|:-----:|:--------:|:---------:|
| **Hits@10**   | {v6_h10}/10 | {ltr_h10}/10 | **{h10_winner}** |
| **Hits@3**    | {v6_h3}/3  | {ltr_h3}/3  | **{h3_winner}** |
| **Spearman ρ**| {v6_sp}  | {ltr_sp}  | **{sp_winner}** |
| **MAE Rank**  | {v6_mae}  | {ltr_mae}  | **{mae_winner}** |

**{cat_abbrev} Elite Winner: {overall_winner}** (LTR: {ltr_wins}, v6.x: {v6_wins}, Ties: {ties})

"""

    if report_path.exists():
        with open(report_path, 'r') as f:
            content = f.read()

        # Check if this category validation already exists
        if f"## {category} Validation Results" in content:
            return str(report_path)

        # Append before the final line or at the end
        if content.rstrip().endswith("*"):
            # Find last line starting with *
            lines = content.rstrip().split('\n')
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].startswith('*'):
                    content = '\n'.join(lines[:i]) + validation_section + '\n'.join(lines[i:])
                    break
        else:
            content = content.rstrip() + validation_section

        with open(report_path, 'w') as f:
            f.write(content)
    else:
        # Create new file with just validation section
        content = f"""# {race_name} LTR Validation Results

**Date:** {race_date}
**A/B Test:** v6.x vs v7.1-LTR

{validation_section}

*Generated by VeloPredict pipeline*
"""
        with open(report_path, 'w') as f:
            f.write(content)

    return str(report_path)


def update_season_tracker(race_name: str, race_date: str, series: str, category: str, validation_results: dict):
    """
    Auto-update SEASON_TRACKER.md with validation results.

    Updates the "Live Predictions (v6.4+)" table with actual results.
    Handles three cases:
    1. Pending row exists -> update it
    2. Row with data exists -> skip (already processed)
    3. No row exists -> add new row

    Args:
        race_name: Race name (e.g., 'Antwerpen')
        race_date: Date string (e.g., '2025-12-20')
        series: Series name (e.g., 'UCI World Cup')
        category: Category (e.g., 'Men Elite')
        validation_results: Dict from validate() with all metrics
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        print(f"  Warning: SEASON_TRACKER.md not found")
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    # Determine category abbreviation
    cat_abbrev = "WE" if "women" in category.lower() else "ME"
    series_abbrev = "UCI WC" if "world cup" in series.lower() else series[:6]

    # Format the new values
    hits_10 = f"{validation_results['hits_10']}/10"
    hits_3 = f"{validation_results['hits_3']}/3"
    spearman = f"{validation_results['spearman']:.2f}" if validation_results['spearman'] is not None else "-"
    mae = f"{validation_results['mae_rank']:.1f}" if validation_results['mae_rank'] is not None else "-"

    # Check if row already exists with actual data (not pending)
    # Pattern: | 2025-12-20 | Antwerpen | UCI WC | ME  | 6/10 | ... (has actual values)
    existing_pattern = rf"\| {race_date} \| {race_name}\s*\| {series_abbrev}\s*\| {cat_abbrev}\s*\| \d+/10"
    if re.search(existing_pattern, content):
        print(f"  SEASON_TRACKER.md already has data for {race_name} {cat_abbrev} - skipping")
        return True

    # Find and update the pending row for this race/category
    # Look for pattern: | 2025-12-20 | Antwerpen | UCI WC | ME  | -       | -      | -          | -        | *Pending* |
    pending_pattern = rf"\| {race_date} \| {race_name}\s+\| {series_abbrev}\s+\| {cat_abbrev}\s+\| -\s+\| -\s+\| -\s+\| -\s+\| \*Pending\* \|"

    # Build replacement row (with proper spacing for alignment)
    new_row = f"| {race_date} | {race_name:<9} | {series_abbrev:<6} | {cat_abbrev:<3} | {hits_10:<7} | {hits_3:<6} | {spearman:<10} | {mae:<8} |           |"

    # Check if pending row exists
    if re.search(pending_pattern, content):
        content = re.sub(pending_pattern, new_row, content)
        print(f"  Updated SEASON_TRACKER.md: {race_name} {cat_abbrev}")
    else:
        # Row doesn't exist - need to add it after the table separator line
        table_marker = "### Live Predictions (v6.4+)"
        if table_marker not in content:
            print(f"  Warning: Live Predictions section not found in SEASON_TRACKER.md")
            return False

        # Find the separator line (|---|...) and insert after it
        lines = content.split('\n')
        new_lines = []
        separator_found = False
        row_added = False
        in_live_section = False

        for i, line in enumerate(lines):
            new_lines.append(line)

            # Track when we enter the Live Predictions section
            if "### Live Predictions (v6.4+)" in line:
                in_live_section = True
                continue

            # Find the separator line in the Live Predictions table
            if in_live_section and line.startswith('|---') and not separator_found:
                separator_found = True
                # Insert the new row right after the separator
                new_lines.append(new_row)
                row_added = True
                continue

            # Stop looking after we leave the section (next ---)
            if in_live_section and line.strip() == '---':
                in_live_section = False

        content = '\n'.join(new_lines)
        if row_added:
            print(f"  Added row to SEASON_TRACKER.md: {race_name} {cat_abbrev}")
        else:
            print(f"  Warning: Could not find table separator in SEASON_TRACKER.md")

    # Update the "Last Updated" date
    today = datetime.now().strftime("%B %d, %Y")
    content = re.sub(r"\*\*Last Updated:\*\* .+", f"**Last Updated:** {today}", content)

    with open(tracker_path, 'w') as f:
        f.write(content)

    return True


def add_race_details_to_tracker(race_name: str, race_date: str, category: str, validation_results: dict):
    """
    Add detailed race summary section to SEASON_TRACKER.md.

    Adds a subsection with surprises, misses, and key takeaways.

    Args:
        race_name: Race name (e.g., 'Antwerpen')
        race_date: Date string (e.g., '2025-12-20')
        category: Category (e.g., 'Men Elite')
        validation_results: Dict from validate() with all metrics
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    cat_abbrev = "WE" if "women" in category.lower() else "ME"

    # Check if THIS CATEGORY's details already exist (not just the race header)
    cat_detail_pattern = f"**{cat_abbrev}:**"
    details_header = f"#### {race_name} {race_date} Details"

    # If header exists and this category is already there, skip
    if details_header in content and cat_detail_pattern in content:
        # Check if cat_detail_pattern appears after the details_header
        header_pos = content.find(details_header)
        next_section = content.find("---", header_pos + 1)
        section_content = content[header_pos:next_section] if next_section > header_pos else content[header_pos:]
        if cat_detail_pattern in section_content:
            print(f"  Race details for {cat_abbrev} already exist in SEASON_TRACKER.md - skipping")
            return True

    # Build the details section
    hits_10 = validation_results['hits_10']
    hits_3 = validation_results['hits_3']
    spearman = validation_results['spearman']
    mae_rank = validation_results['mae_rank']

    # Extract surprises and misses from next-10 and top-10 detail
    pred_next10_detail = validation_results.get('pred_next10_detail', [])
    pred_top10_detail = validation_results.get('pred_top10_detail', [])

    surprises = []
    for detail in pred_next10_detail:
        if detail.get('hit'):
            actual = detail['actual_place']
            surprises.append(f"{detail['rider'].split()[-1]} (#{detail['pred_rank']}→P{actual})")

    misses = []
    for detail in pred_top10_detail:
        if not detail.get('hit'):
            actual = detail['actual_place']
            if isinstance(actual, int) and actual > 10:
                misses.append(f"{detail['rider'].split()[-1]} (P{actual})")
            elif actual == 'DNF/DNS':
                misses.append(f"{detail['rider'].split()[-1]} (DNS)")

    # Determine overall status
    targets_met = sum([
        1 if hits_10 >= 7 else 0,
        1 if hits_3 >= 2 else 0,
        1 if spearman is not None and spearman > 0.5 else 0,
        1 if mae_rank is not None and mae_rank < 3 else 0
    ])

    if targets_met == 4:
        status_emoji = "🟢"
        status_text = "All targets met"
    elif targets_met >= 2:
        status_emoji = "🟡"
        status_text = f"{targets_met}/4 targets met"
    else:
        status_emoji = "🔴"
        status_text = f"{targets_met}/4 targets met"

    # Build the section
    details_lines = [
        f"",
        f"**{cat_abbrev}:** {status_emoji} {status_text}",
    ]

    if surprises:
        details_lines.append(f"- Surprises: {', '.join(surprises[:3])}")
    if misses:
        details_lines.append(f"- Misses: {', '.join(misses[:3])}")

    # Podium accuracy
    spearman_str = f"{spearman:.2f}" if spearman is not None else "N/A"
    details_lines.append(f"- Podium: {hits_3}/3 | Spearman: {spearman_str}")

    details_text = '\n'.join(details_lines)

    # Find where to insert details
    lines = content.split('\n')
    new_lines = []
    details_added = False
    race_details_header = f"#### {race_name} {race_date} Details"

    # Check if the race details section already exists
    if race_details_header in content:
        # Insert this category's details after the existing header (before the ---)
        for i, line in enumerate(lines):
            new_lines.append(line)

            # Found the existing details section - look for last detail line before ---
            if race_details_header in line and not details_added:
                # Copy lines until we hit ---
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('---'):
                    j += 1
                # Insert before the --- (after the last content line)
                # We've already added the header, now look for --- and insert before it
                continue

            # If we're at the --- right after the details section, insert before it
            if line.strip().startswith('---') and not details_added:
                # Check if previous non-empty line was part of our details section
                for prev_i in range(len(new_lines) - 2, -1, -1):
                    if new_lines[prev_i].strip():
                        # Check if we're in the right details section
                        header_found = False
                        for check_i in range(prev_i, -1, -1):
                            if race_details_header in new_lines[check_i]:
                                header_found = True
                                break
                            if new_lines[check_i].strip().startswith('####'):
                                break
                        if header_found:
                            # Insert before the ---
                            new_lines.pop()  # Remove the --- we just added
                            new_lines.append(details_text)
                            new_lines.append(line)  # Put --- back
                            details_added = True
                        break
    else:
        # Create new details section - find where to insert (after table, before ---)
        table_ended = False
        in_live_section = False

        for i, line in enumerate(lines):
            # Track when we enter the Live Predictions section
            if "### Live Predictions (v6.4+)" in line:
                in_live_section = True

            # Find the end of table (first non-table line after table starts)
            if in_live_section and not table_ended:
                if line.strip() == '' and i > 0 and new_lines and new_lines[-1].startswith('|'):
                    table_ended = True

            # Find where to insert details (after the --- that follows the table)
            if in_live_section and table_ended and line.strip() == '---' and not details_added:
                new_lines.append(f"")
                new_lines.append(race_details_header)
                new_lines.append(details_text)
                details_added = True
                in_live_section = False

            new_lines.append(line)

    content = '\n'.join(new_lines)

    with open(tracker_path, 'w') as f:
        f.write(content)

    if details_added:
        print(f"  Added race details to SEASON_TRACKER.md: {race_name} {cat_abbrev}")

    return True


def update_season_summary_table(race_name: str, race_date: str, series: str, category: str,
                                 model_version: str, validation_results: dict):
    """
    Update the Season Summary table in SEASON_TRACKER.md with validation results.

    This table shows all races with their original prediction metrics.

    Args:
        race_name: Race name (e.g., 'Antwerpen')
        race_date: Date string (e.g., '2025-12-20')
        series: Series name (e.g., 'UCI World Cup')
        category: Category (e.g., 'Men Elite')
        model_version: Model version used (e.g., 'v6.4')
        validation_results: Dict with hits_10, hits_3, spearman, mae_rank
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        print(f"  Warning: SEASON_TRACKER.md not found")
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    # Format values
    cat_abbrev = "WE" if "women" in category.lower() else "ME"
    series_abbrev = "UCI WC" if "world cup" in series.lower() else series[:6]
    hits_10 = f"{validation_results['hits_10']}/10"
    hits_3 = f"{validation_results['hits_3']}/3"
    spearman = f"{validation_results['spearman']:.2f}" if validation_results.get('spearman') is not None else "n/a"
    mae = f"{validation_results['mae_rank']:.1f}" if validation_results.get('mae_rank') is not None else "n/a"

    # Find the Season Summary table section first
    # Look for the table header pattern
    season_summary_pattern = r"(## Season Summary.*?\n\n\| Date.*?\n\|[-\|]+\n)"

    match = re.search(season_summary_pattern, content, re.DOTALL)
    if not match:
        print(f"  Warning: Season Summary table not found in SEASON_TRACKER.md")
        return False

    # Extract only the Season Summary section (from header to next section or Season Averages)
    section_start = match.start()
    next_section = re.search(r"\n### Season Averages", content[section_start:])
    if next_section:
        section_end = section_start + next_section.start()
    else:
        section_end = len(content)
    season_summary_section = content[section_start:section_end]

    # Check if row already exists in the Season Summary table specifically
    existing_pattern = rf"\| {race_date} \| {race_name}\s*\| .+\| {cat_abbrev}"
    if re.search(existing_pattern, season_summary_section):
        print(f"  Season Summary already has {race_name} {cat_abbrev} - skipping")
        return True

    # Find where the table data ends (look for blank line or new section)
    table_start = match.end()

    # Find all existing rows and insert in date order
    lines = content.split('\n')
    new_lines = []
    in_season_summary = False
    in_table = False
    row_added = False
    last_table_row_idx = -1

    for i, line in enumerate(lines):
        if "## Season Summary" in line:
            in_season_summary = True

        # Track when we're in the actual table rows
        if in_season_summary and line.startswith("| ") and not line.startswith("|--"):
            if "Date" not in line:  # Skip header row
                in_table = True
                last_table_row_idx = len(new_lines)

        # If we hit a blank line or next section while in table, insert before it
        if in_table and (line.strip() == "" or line.startswith("###")):
            if not row_added:
                # Add the new row at the end of the table
                new_row = f"| {race_date} | {race_name:<11} | {series_abbrev:<9} | {cat_abbrev} | {model_version:<5} | {hits_10:<7} | {hits_3:<6} | {spearman:<10} | {mae:<8} |"
                new_lines.append(new_row)
                row_added = True
            in_table = False
            in_season_summary = False

        new_lines.append(line)

    if row_added:
        content = '\n'.join(new_lines)
        with open(tracker_path, 'w') as f:
            f.write(content)
        print(f"  Added to Season Summary: {race_name} {cat_abbrev}")

        # Also update season averages
        update_season_averages()

    return True


def update_season_averages():
    """
    Recalculate and update the Season Averages section based on Season Summary table.
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    # Parse the Season Summary table
    # Find lines that look like: | 2025-12-20 | Antwerpen | UCI WC | ME | v6.4 | 6/10 | 1/3 | 0.08 | 6.0 |
    row_pattern = r"\| (\d{4}-\d{2}-\d{2}) \| .+?\| .+?\| (ME|WE) \| .+?\| (\d+)/10\s*\| (\d+)/3"

    matches = re.findall(row_pattern, content)

    if not matches:
        return False

    # Calculate averages
    me_hits10 = []
    me_hits3 = []
    we_hits10 = []
    we_hits3 = []

    for date, cat, h10, h3 in matches:
        if cat == "ME":
            me_hits10.append(int(h10))
            me_hits3.append(int(h3))
        else:
            we_hits10.append(int(h10))
            we_hits3.append(int(h3))

    me_count = len(me_hits10)
    we_count = len(we_hits10)
    total_count = me_count + we_count

    me_avg_h10 = sum(me_hits10) / me_count if me_count > 0 else 0
    me_avg_h3 = sum(me_hits3) / me_count if me_count > 0 else 0
    we_avg_h10 = sum(we_hits10) / we_count if we_count > 0 else 0
    we_avg_h3 = sum(we_hits3) / we_count if we_count > 0 else 0

    overall_avg_h10 = (sum(me_hits10) + sum(we_hits10)) / total_count if total_count > 0 else 0
    overall_avg_h3 = (sum(me_hits3) + sum(we_hits3)) / total_count if total_count > 0 else 0

    # Build new averages table
    new_averages = f"""### Season Averages

| Category    | Races | Avg Hits@10 | Avg Hits@3 |
|-------------|-------|-------------|------------|
| Men Elite   | {me_count}     | {me_avg_h10:.1f}/10      | {me_avg_h3:.1f}/3      |
| Women Elite | {we_count}     | {we_avg_h10:.1f}/10      | {we_avg_h3:.1f}/3      |
| **Overall** | {total_count}    | **{overall_avg_h10:.1f}/10**  | **{overall_avg_h3:.1f}/3**  |

### Targets

| Metric | Target | Season Avg | Status |
|--------|--------|------------|--------|
| Hits@10 | 7+/10 | {overall_avg_h10:.1f}/10 | {"✅ Met" if overall_avg_h10 >= 7 else "❌ Below"} |
| Hits@3 | 2+/3 | {overall_avg_h3:.1f}/3 | {"✅ Met" if overall_avg_h3 >= 2 else "❌ Below"} |"""

    # Replace the existing Season Averages and Targets sections
    old_averages_pattern = r"### Season Averages.*?(?=\n---)"
    content = re.sub(old_averages_pattern, new_averages, content, flags=re.DOTALL)

    with open(tracker_path, 'w') as f:
        f.write(content)

    print(f"  Updated Season Averages: ME {me_count} races, WE {we_count} races")
    return True


def update_tracker_model_version(new_version: str):
    """
    Update the Current Model Version in SEASON_TRACKER.md header.

    Args:
        new_version: New version string (e.g., 'v6.5')
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    # Update the version line
    old_pattern = r"\*\*Current Model Version:\*\* v\d+\.\d+"
    new_line = f"**Current Model Version:** {new_version}"

    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_line, content)

        # Also update the footer
        footer_pattern = r"\*Generated by VeloPredict v\d+\.\d+"
        footer_new = f"*Generated by VeloPredict {new_version}"
        content = re.sub(footer_pattern, footer_new, content)

        with open(tracker_path, 'w') as f:
            f.write(content)

        print(f"  Updated SEASON_TRACKER.md model version to {new_version}")
        return True

    return False


def update_distribution_tables(race_name: str, race_date: str, category: str,
                                distribution_data: dict, validation_results: dict):
    """
    Update the Distribution by Race and Distribution vs Accuracy tables in SEASON_TRACKER.md.

    Args:
        race_name: Race name (e.g., 'Koksijde')
        race_date: Date string (e.g., '2025-12-21')
        category: Category (e.g., 'Men Elite')
        distribution_data: Dict with low_pct, mid_pct, high_pct, pattern, field_size, new_riders
        validation_results: Dict with hits_10, hits_3, etc.
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    cat_abbrev = "WE" if "women" in category.lower() else "ME"
    race_label = f"{race_name} {cat_abbrev}"

    # Extract distribution values
    low_pct = distribution_data.get('low_pct', 0) * 100
    mid_pct = distribution_data.get('mid_pct', 0) * 100
    high_pct = distribution_data.get('high_pct', 0) * 100
    pattern = distribution_data.get('pattern', 'MODERATE')
    field_size = distribution_data.get('field_size', 0)
    new_riders = distribution_data.get('new_riders', 0)

    # ---- Update Distribution by Race table ----
    dist_table_marker = "| Race        | Low (<30%) | Mid (30-60%) | High (>60%) | Pattern   | Field | New Riders |"

    if dist_table_marker in content:
        # Check if this race/category already exists
        existing_pattern = rf"\| {race_label}\s+\|"
        if not re.search(existing_pattern, content):
            # Find the end of the table (blank line after last row)
            lines = content.split('\n')
            new_lines = []
            in_dist_table = False
            last_row_idx = -1

            for i, line in enumerate(lines):
                new_lines.append(line)
                if dist_table_marker in line:
                    in_dist_table = True
                    continue
                if in_dist_table:
                    if line.startswith('|'):
                        last_row_idx = len(new_lines) - 1
                    elif line.strip() == '' or line.startswith('#'):
                        # End of table - insert new row before this line
                        if last_row_idx > 0:
                            new_row = f"| {race_label:<11} | {low_pct:.1f}%{' ' * (6 - len(f'{low_pct:.1f}'))}| {mid_pct:.1f}%{' ' * (8 - len(f'{mid_pct:.1f}'))}| {high_pct:.1f}%{' ' * (7 - len(f'{high_pct:.1f}'))}| {pattern:<9} | {field_size:<5} | {new_riders:<10} |"
                            new_lines.insert(last_row_idx + 1, new_row)
                        in_dist_table = False

            content = '\n'.join(new_lines)
            print(f"  Added {race_label} to Distribution by Race table")

    # ---- Update Distribution vs Accuracy table ----
    # This table shows combined race-level stats (avg of ME + WE)
    accuracy_table_marker = "| Race        | Pattern   | Mid % | Hits@10 (v6.4+) | Precision | Notes"

    if accuracy_table_marker in content:
        # More flexible pattern to check if race already exists
        existing_acc_pattern = rf"\|\s*{race_name}\s*\|"
        if not re.search(existing_acc_pattern, content):
            # Calculate precision (assuming high_conf predictions)
            hits_10 = validation_results.get('hits_10', 0)
            precision = int((hits_10 / 10) * 100) if hits_10 else 0

            # Determine notes based on surprises or key results
            cat_abbrev = "WE" if "women" in category.lower() else "ME"
            notes = ""

            # Check for notable results in pred_top10_detail
            if 'pred_top10_detail' in validation_results:
                misses = []
                surprises = []
                for d in validation_results['pred_top10_detail']:
                    if not d.get('hit') and isinstance(d.get('actual_place'), int):
                        if d['actual_place'] > 10:
                            # Get short name (last name + first initial)
                            full_name = d.get('rider', '')
                            parts = full_name.split()
                            short = parts[0] if parts else ''
                            misses.append(f"{short} P{d['actual_place']}")

                # Generate concise notes
                if misses:
                    notes = ", ".join(misses[:2])  # Show up to 2 misses

            lines = content.split('\n')
            new_lines = []
            in_acc_table = False
            last_row_idx = -1

            for i, line in enumerate(lines):
                new_lines.append(line)
                if accuracy_table_marker in line:
                    in_acc_table = True
                    continue
                if in_acc_table:
                    if line.startswith('|') and not line.startswith('|--'):
                        last_row_idx = len(new_lines) - 1
                    elif line.strip() == '' or line.startswith('#'):
                        if last_row_idx > 0:
                            # Format: Hits@10 shows single category value, will be updated when 2nd category validated
                            hits_str = f"{hits_10}/10"
                            new_row = f"| {race_name:<11} | {pattern:<9} | {mid_pct:.1f}% | {hits_str:<15} | {precision}%{' ' * (7 - len(str(precision)))}| {notes:<24} |"
                            new_lines.insert(last_row_idx + 1, new_row)
                        in_acc_table = False

            content = '\n'.join(new_lines)
            print(f"  Added {race_name} to Distribution vs Accuracy table")
        else:
            # Race already exists - update with combined stats if this is the second category
            # Find and update the existing row to show combined (avg) hits
            print(f"  {race_name} already in Distribution vs Accuracy table - skipping duplicate")

    with open(tracker_path, 'w') as f:
        f.write(content)

    return True


def update_season_trend_charts(race_name: str, model_version: str, distribution_data: dict):
    """
    Update the ASCII trend charts in SEASON_TRACKER.md.

    Args:
        race_name: Race name (e.g., 'Koksijde')
        model_version: Model version (e.g., 'v6.5')
        distribution_data: Dict with low_pct, mid_pct, high_pct
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    low_pct = distribution_data.get('low_pct', 0) * 100
    mid_pct = distribution_data.get('mid_pct', 0) * 100
    high_pct = distribution_data.get('high_pct', 0) * 100

    race_label = f"{race_name} ({model_version})"

    # Helper to generate bar
    def make_bar(pct, max_width=90):
        filled = int((pct / 100) * max_width)
        bar = "█" * filled
        # Add partial block for fractional part
        remainder = ((pct / 100) * max_width) - filled
        if remainder >= 0.75:
            bar += "▊"
        elif remainder >= 0.5:
            bar += "▌"
        elif remainder >= 0.25:
            bar += "▍"
        return bar

    # Check if race already in charts
    if race_label in content:
        print(f"  Season trend charts already have {race_label} - skipping")
        return True

    # Find and update each chart section
    # Low Range chart
    low_marker = "**🔵 Low Range (<30%) - Non-contenders**"
    if low_marker in content:
        lines = content.split('\n')
        new_lines = []
        in_low_chart = False
        chart_end_idx = -1

        for i, line in enumerate(lines):
            new_lines.append(line)
            if low_marker in line:
                in_low_chart = True
                continue
            if in_low_chart and line.strip() == '```':
                if chart_end_idx == -1:
                    # Opening backticks
                    chart_end_idx = 0
                else:
                    # Closing backticks - insert new line before this
                    bar = make_bar(low_pct)
                    new_line = f"{race_label:<16} {bar} {low_pct:.1f}%"
                    new_lines.insert(len(new_lines) - 1, new_line)
                    in_low_chart = False

        content = '\n'.join(new_lines)

    # Mid Range chart
    mid_marker = "**🟡 Mid Range (30-60%) - Uncertain zone**"
    if mid_marker in content:
        lines = content.split('\n')
        new_lines = []
        in_mid_chart = False
        chart_end_idx = -1

        for i, line in enumerate(lines):
            new_lines.append(line)
            if mid_marker in line:
                in_mid_chart = True
                continue
            if in_mid_chart and line.strip() == '```':
                if chart_end_idx == -1:
                    chart_end_idx = 0
                else:
                    bar = make_bar(mid_pct)
                    new_line = f"{race_label:<16} {bar:<20} {mid_pct:.1f}%"
                    new_lines.insert(len(new_lines) - 1, new_line)
                    in_mid_chart = False

        content = '\n'.join(new_lines)

    # High Range chart
    high_marker = "**🟢 High Range (>60%) - Likely contenders**"
    if high_marker in content:
        lines = content.split('\n')
        new_lines = []
        in_high_chart = False
        chart_end_idx = -1

        for i, line in enumerate(lines):
            new_lines.append(line)
            if high_marker in line:
                in_high_chart = True
                continue
            if in_high_chart and line.strip() == '```':
                if chart_end_idx == -1:
                    chart_end_idx = 0
                else:
                    bar = make_bar(high_pct)
                    new_line = f"{race_label:<16} {bar:<35} {high_pct:.1f}%"
                    new_lines.insert(len(new_lines) - 1, new_line)
                    in_high_chart = False

        content = '\n'.join(new_lines)

    with open(tracker_path, 'w') as f:
        f.write(content)

    print(f"  Added {race_label} to Season Trend charts")
    return True


def update_version_history_table(model_version: str, race_date: str, description: str,
                                  accuracy: float, validation_notes: str):
    """
    Update the Evolution Overview table in VERSION_HISTORY.md.

    Args:
        model_version: Model version (e.g., 'v6.6')
        race_date: Date string (e.g., '2025-12-21')
        description: Brief description of changes
        accuracy: Top-10 accuracy percentage
        validation_notes: Notes about validation status
    """
    history_path = config.PROJECT_ROOT / "VERSION_HISTORY.md"

    if not history_path.exists():
        print(f"  Warning: VERSION_HISTORY.md not found")
        return False

    with open(history_path, 'r') as f:
        content = f.read()

    # Parse date to get month/day
    date_obj = datetime.strptime(race_date, "%Y-%m-%d")
    date_short = date_obj.strftime("%b %d")

    # Check if this version already exists in the table
    existing_pattern = rf"\| \*\*{model_version}\*\* \|"
    if re.search(existing_pattern, content):
        print(f"  VERSION_HISTORY.md already has {model_version} in Evolution table - skipping")
        return True

    # Find the Evolution Overview table and add new row
    # Look for the last row before the --- separator
    evolution_marker = "Evolution Overview"  # Works with or without emoji prefix

    if evolution_marker in content:
        lines = content.split('\n')
        new_lines = []
        in_evolution = False
        last_row_idx = -1

        for i, line in enumerate(lines):
            new_lines.append(line)
            if evolution_marker in line:
                in_evolution = True
                continue
            if in_evolution:
                if line.startswith('|') and 'Current' in line:
                    # This is the current version row - update it to Superseded first
                    new_lines[-1] = line.replace('**Current**', 'Superseded')
                    last_row_idx = len(new_lines) - 1
                elif line.startswith('|') and not line.startswith('|--') and not 'Version' in line:
                    last_row_idx = len(new_lines) - 1
                elif line.strip() == '---':
                    # End of section - insert new row before ---
                    if last_row_idx > 0:
                        new_row = f"| **{model_version}** | {date_short} | **{description}** | {accuracy:.1f}% | {validation_notes} | **Current** |"
                        new_lines.insert(last_row_idx + 1, new_row)
                    in_evolution = False

        content = '\n'.join(new_lines)

    # Update header version
    old_header = r"\*\*Current Version:\*\* v\d+\.\d+"
    new_header = f"**Current Version:** {model_version}"
    content = re.sub(old_header, new_header, content)

    with open(history_path, 'w') as f:
        f.write(content)

    print(f"  Added {model_version} to VERSION_HISTORY.md Evolution table")
    return True


def update_version_history_current(race_name: str, race_date: str, model_version: str,
                                    category: str, validation_results: dict,
                                    training_stats: dict = None):
    """
    Update the Current Status section in VERSION_HISTORY.md with validation results.

    Args:
        race_name: Race name (e.g., 'Koksijde')
        race_date: Date string (e.g., '2025-12-21')
        model_version: Model version (e.g., 'v6.5')
        category: Category (e.g., 'Men Elite')
        validation_results: Dict with hits_10, hits_3, spearman, mae_rank
        training_stats: Optional dict with observations, races, accuracy, etc.
    """
    history_path = config.PROJECT_ROOT / "VERSION_HISTORY.md"

    if not history_path.exists():
        return False

    with open(history_path, 'r') as f:
        content = f.read()

    cat_abbrev = "ME" if "men" in category.lower() else "WE"

    # Check if this race/category already has validation in Current Status
    validation_marker = f"{race_name}.*{cat_abbrev}.*{validation_results['hits_10']}/10"
    if re.search(validation_marker, content):
        print(f"  VERSION_HISTORY.md Current Status already has {race_name} {cat_abbrev} - skipping")
        return True

    # Build validation entry for this category
    hits_10 = validation_results['hits_10']
    hits_3 = validation_results['hits_3']
    spearman = validation_results.get('spearman', 0)
    mae_rank = validation_results.get('mae_rank', 0)

    targets_met = sum([
        1 if hits_10 >= 7 else 0,
        1 if hits_3 >= 2 else 0,
        1 if spearman and spearman > 0.5 else 0,
        1 if mae_rank and mae_rank < 3 else 0
    ])

    # Find the Season Totals table and add/update the race row
    season_totals_marker = "**Season Totals"

    if season_totals_marker in content:
        # Check if race already in Season Totals
        race_pattern = rf"\| {race_name}\s+\|"
        if not re.search(race_pattern, content):
            # Add new row to Season Totals table
            lines = content.split('\n')
            new_lines = []
            in_season_totals = False
            last_row_idx = -1

            for i, line in enumerate(lines):
                new_lines.append(line)
                if season_totals_marker in line:
                    in_season_totals = True
                    continue
                if in_season_totals:
                    if line.startswith('|') and not line.startswith('|--') and not 'Race' in line:
                        last_row_idx = len(new_lines) - 1
                    elif line.strip() == '' or line.startswith('**'):
                        if last_row_idx > 0:
                            me_hits = f"{hits_10}/10" if cat_abbrev == "ME" else "-"
                            we_hits = f"{hits_10}/10" if cat_abbrev == "WE" else "-"
                            notes = "4/4 targets" if targets_met == 4 else ""
                            new_row = f"| {race_name:<11} | {model_version:<5} | {me_hits:<10} | {we_hits:<10} | {notes} |"
                            new_lines.insert(last_row_idx + 1, new_row)
                        in_season_totals = False

            content = '\n'.join(new_lines)

    # Update footer with race count and observations
    if training_stats:
        obs = training_stats.get('observations', 0)
        races = training_stats.get('races', 0)

        # Update footer line
        footer_pattern = r"\*\*Races Validated:\*\* \d+ \([^)]+\)"
        # Count validated races from content
        race_count_match = re.findall(r"\| \d{4}-\d{2}-\d{2} \|", content)
        race_count = len(set(race_count_match)) // 2 if race_count_match else races

        new_footer = f"**Races Validated:** {race_count} (including {race_name})"
        content = re.sub(footer_pattern, new_footer, content)

        # Update dataset size
        dataset_pattern = r"\*\*Dataset Size:\*\* [\d,]+ observations, \d+ races"
        new_dataset = f"**Dataset Size:** {obs:,} observations, {races} races"
        content = re.sub(dataset_pattern, new_dataset, content)

    with open(history_path, 'w') as f:
        f.write(content)

    print(f"  Updated VERSION_HISTORY.md Current Status with {race_name} {cat_abbrev}")
    return True


def update_training_metrics_table(model_version: str, accuracy: float, auc: float,
                                    observations: int, innovation: str):
    """
    Update the Training Metrics table in VERSION_HISTORY.md after retraining.

    Args:
        model_version: Model version (e.g., 'v6.7')
        accuracy: Top-10 accuracy percentage (e.g., 81.2)
        auc: AUC-ROC value (e.g., 0.812)
        observations: Total training observations
        innovation: Brief description (e.g., '+Hofstade Results')
    """
    history_path = config.PROJECT_ROOT / "VERSION_HISTORY.md"

    if not history_path.exists():
        print(f"  Warning: VERSION_HISTORY.md not found")
        return False

    with open(history_path, 'r') as f:
        content = f.read()

    # Check if this version already exists in the Training Metrics table
    existing_pattern = rf"\| {model_version}\s+\|"
    # Only check in the Training Metrics section
    training_section = re.search(r"### Training Metrics.*?(?=### Live Validation|$)", content, re.DOTALL)
    if training_section and re.search(existing_pattern, training_section.group()):
        print(f"  Training Metrics already has {model_version} - skipping")
        return True

    # Find the Training Metrics table
    metrics_marker = "### Training Metrics"

    if metrics_marker not in content:
        print(f"  Warning: Training Metrics table not found in VERSION_HISTORY.md")
        return False

    lines = content.split('\n')
    new_lines = []
    in_metrics = False
    last_row_idx = -1
    prev_version_row = None

    for i, line in enumerate(lines):
        new_lines.append(line)
        if metrics_marker in line:
            in_metrics = True
            continue
        if in_metrics:
            if line.startswith('|') and not line.startswith('|--') and 'Version' not in line:
                last_row_idx = len(new_lines) - 1
                # Mark current version as not bold if this is the current row
                if '**' in line and model_version not in line:
                    # Remove bold from previous "current" row
                    new_lines[-1] = line.replace('**', '')
            elif line.strip() == '' or line.startswith('###'):
                # End of table - insert new row
                if last_row_idx > 0:
                    new_row = f"| {model_version}    | **{accuracy:.1f}%**  | ~58%      | **{auc:.3f}** | **{observations:,}**    | **{innovation}** |"
                    new_lines.insert(last_row_idx + 1, new_row)
                in_metrics = False

    content = '\n'.join(new_lines)

    with open(history_path, 'w') as f:
        f.write(content)

    print(f"  Added {model_version} to Training Metrics table")
    return True


def update_evolution_overview_table(model_version: str, race_date: str, innovation: str,
                                     accuracy: float, validation_notes: str):
    """
    Update the Evolution Overview table in VERSION_HISTORY.md after retraining.

    Args:
        model_version: Model version (e.g., 'v6.7')
        race_date: Date string (e.g., '2025-12-22')
        innovation: Brief description (e.g., '+Hofstade Results')
        accuracy: Top-10 accuracy percentage
        validation_notes: Notes about validation status
    """
    history_path = config.PROJECT_ROOT / "VERSION_HISTORY.md"

    if not history_path.exists():
        print(f"  Warning: VERSION_HISTORY.md not found")
        return False

    with open(history_path, 'r') as f:
        content = f.read()

    # Parse date to get month/day
    date_obj = datetime.strptime(race_date, "%Y-%m-%d")
    date_short = date_obj.strftime("%b %d")

    # Check if this version already exists
    existing_pattern = rf"\| \*\*{model_version}\*\* \|"
    if re.search(existing_pattern, content):
        print(f"  Evolution Overview already has {model_version} - skipping")
        return True

    # Find the Evolution Overview table
    evolution_marker = "Evolution Overview"

    if evolution_marker not in content:
        print(f"  Warning: Evolution Overview table not found")
        return False

    lines = content.split('\n')
    new_lines = []
    in_evolution = False
    last_row_idx = -1

    for i, line in enumerate(lines):
        # Update previous "Current" to "Superseded"
        if in_evolution and '**Current**' in line and model_version not in line:
            line = line.replace('**Current**', 'Superseded')

        new_lines.append(line)

        if evolution_marker in line:
            in_evolution = True
            continue
        if in_evolution:
            if line.startswith('|') and not line.startswith('|--') and 'Version' not in line:
                last_row_idx = len(new_lines) - 1
            elif line.strip() == '---':
                # End of section - insert new row before ---
                if last_row_idx > 0:
                    new_row = f"| **{model_version}** | {date_short} | **{innovation}** | {accuracy:.1f}% | {validation_notes} | **Current** |"
                    new_lines.insert(last_row_idx + 1, new_row)
                in_evolution = False

    # Update header version
    old_header = r"\*\*Current Version:\*\* v\d+\.\d+"
    new_header = f"**Current Version:** {model_version}"
    content = '\n'.join(new_lines)
    content = re.sub(old_header, new_header, content)

    with open(history_path, 'w') as f:
        f.write(content)

    print(f"  Added {model_version} to Evolution Overview table")
    return True


def update_season_tracker_version_table(model_version: str, innovation: str,
                                         accuracy: float, auc: float,
                                         observations: int, notes: str):
    """
    Update the Model Version History table in SEASON_TRACKER.md after retraining.

    Args:
        model_version: Model version (e.g., 'v6.7')
        innovation: Brief description (e.g., '+Hofstade Results')
        accuracy: Top-10 accuracy percentage (e.g., 81.2)
        auc: AUC-ROC score (e.g., 0.812)
        observations: Total training observations
        notes: Notes for this version
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        print(f"  Warning: SEASON_TRACKER.md not found")
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    # Check if this version already exists
    existing_pattern = rf"\*\*{model_version}\*\*"
    if re.search(existing_pattern, content):
        print(f"  SEASON_TRACKER Model Version History already has {model_version} - skipping")
        return True

    # Find the Model Version History table
    table_marker = "## Model Version History"

    if table_marker not in content:
        print(f"  Warning: Model Version History table not found in SEASON_TRACKER.md")
        return False

    lines = content.split('\n')
    new_lines = []
    in_table = False
    last_row_idx = -1

    for i, line in enumerate(lines):
        # Update previous "Current" row to remove bold and current marker
        if in_table and '**Current' in line and model_version not in line:
            # Remove bold from version and update notes
            line = re.sub(r'\*\*v(\d+\.\d+)\*\*', r'v\1', line)
            line = re.sub(r'\*\*Current[^|]*\*\*', lambda m: m.group(0).replace('**', '').replace('Current - ', ''), line)

        new_lines.append(line)

        if table_marker in line:
            in_table = True
            continue
        if in_table:
            if line.startswith('|') and not line.startswith('|--') and 'Version' not in line and 'Innovation' not in line:
                last_row_idx = len(new_lines) - 1
            elif line.strip() == '---' or (line.strip() == '' and last_row_idx > 0):
                # End of table section - insert new row
                if last_row_idx > 0:
                    new_row = f"| **{model_version}**   | {innovation:<26} | {accuracy:.1f}%         | {auc:.3f} | {observations:,}        | **{notes}** |"
                    new_lines.insert(last_row_idx + 1, new_row)
                in_table = False

    content = '\n'.join(new_lines)

    with open(tracker_path, 'w') as f:
        f.write(content)

    print(f"  Added {model_version} to SEASON_TRACKER Model Version History table")
    return True


def update_retraining_history_table(model_version: str, race_date: str, innovation: str,
                                     observations: int, race_name: str):
    """
    Update the Retraining History table in SEASON_TRACKER.md after retraining.

    Args:
        model_version: Model version (e.g., 'v6.9')
        race_date: Date of the race that triggered retrain (e.g., '2025-12-27')
        innovation: Brief description (e.g., '+Gavere Results')
        observations: Total training observations
        race_name: Name of the race
    """
    tracker_path = config.PROJECT_ROOT / "SEASON_TRACKER.md"

    if not tracker_path.exists():
        print(f"  Warning: SEASON_TRACKER.md not found")
        return False

    with open(tracker_path, 'r') as f:
        content = f.read()

    # Check if this version already exists in Retraining History
    # Look for the version in the retraining history section
    if f"| {model_version}" in content and "Retraining History" in content:
        # Check if it's specifically in the Retraining History table
        retraining_section = content.split("### Retraining History")[1].split("---")[0] if "### Retraining History" in content else ""
        if f"| {model_version}" in retraining_section:
            print(f"  Retraining History already has {model_version} - skipping")
            return True

    # Find the Retraining History table
    table_marker = "### Retraining History"

    if table_marker not in content:
        print(f"  Warning: Retraining History table not found in SEASON_TRACKER.md")
        return False

    # Format date for display (Dec 27 format)
    from datetime import datetime as dt
    try:
        date_obj = dt.strptime(race_date, "%Y-%m-%d")
        date_display = date_obj.strftime("%Y-%m-%d")
    except:
        date_display = race_date

    lines = content.split('\n')
    new_lines = []
    in_table = False
    last_row_idx = -1
    found_table = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        if table_marker in line:
            found_table = True
            continue
        if found_table and line.startswith('| Version'):
            in_table = True
            continue
        if found_table and line.startswith('|--'):
            continue
        if in_table:
            if line.startswith('|') and not line.startswith('|--'):
                last_row_idx = len(new_lines) - 1
            elif line.strip() == '' or line.startswith('#') or line.strip() == '---':
                # End of table - insert new row before this
                if last_row_idx > 0:
                    notes = f"Post-{race_name}"
                    new_row = f"| {model_version}    | {date_display} | {innovation:<23} | {observations:,}        | {notes:<20} |"
                    new_lines.insert(last_row_idx + 1, new_row)
                in_table = False
                found_table = False

    content = '\n'.join(new_lines)

    with open(tracker_path, 'w') as f:
        f.write(content)

    print(f"  Added {model_version} to Retraining History table")
    return True


def get_distribution_from_predictions(predictions_df: pd.DataFrame) -> dict:
    """
    Calculate distribution metrics from a predictions DataFrame.

    Returns dict with: low_pct, mid_pct, high_pct, pattern, field_size, new_riders
    """
    probs = predictions_df['Top-10 Probability'].values

    low_count = sum(1 for p in probs if p < 0.30)
    mid_count = sum(1 for p in probs if 0.30 <= p < 0.60)
    high_count = sum(1 for p in probs if p >= 0.60)
    total = len(probs)

    low_pct = low_count / total if total > 0 else 0
    mid_pct = mid_count / total if total > 0 else 0
    high_pct = high_count / total if total > 0 else 0

    # Determine pattern
    if mid_pct < 0.10:
        pattern = "BIMODAL"
    elif mid_pct < 0.20:
        pattern = "MODERATE"
    else:
        pattern = "BALANCED"

    # Count new riders (those with no H2H data)
    new_riders = 0
    if 'H2H Win %' in predictions_df.columns:
        new_riders = predictions_df['H2H Win %'].isna().sum()

    return {
        'low_pct': low_pct,
        'mid_pct': mid_pct,
        'high_pct': high_pct,
        'pattern': pattern,
        'field_size': total,
        'new_riders': new_riders
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

  # Validate predictions against results (basic)
  python pipeline.py validate --predictions data/clean/predictions_namur.csv --results data/results/namur.csv

  # Validate with auto-updates (registry + SEASON_TRACKER.md + validation report)
  python pipeline.py validate-race \\
    --predictions data/clean/predictions_antwerpen_men_2025-12-20.csv \\
    --results "data/results/Results__UCI-WC__ Antwerpen__Men-Elite__2025-12-20.csv" \\
    --race-name Antwerpen --race-date 2025-12-20 --category "Men Elite"

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

    # Backfill distribution command
    backfill_parser = subparsers.add_parser('backfill-distribution', help='Calculate distribution metrics for all races')

    # Update validation reports command
    update_reports_parser = subparsers.add_parser('update-reports', help='Add distribution section to validation reports')

    # Update prediction reports command
    update_predictions_parser = subparsers.add_parser('update-predictions', help='Add distribution section to prediction reports')

    # Validate-race command (full validation with auto-updates)
    validate_race_parser = subparsers.add_parser('validate-race', help='Validate predictions and auto-update registry + SEASON_TRACKER')
    validate_race_parser.add_argument('--predictions', required=True, help='Path to predictions CSV')
    validate_race_parser.add_argument('--results', required=True, help='Path to results CSV')
    validate_race_parser.add_argument('--race-name', required=True, help='Race name (e.g., Antwerpen)')
    validate_race_parser.add_argument('--race-date', required=True, help='Race date (e.g., 2025-12-20)')
    validate_race_parser.add_argument('--category', required=True, help='Category (e.g., "Men Elite")')
    validate_race_parser.add_argument('--series', default='UCI World Cup', help='Series name')
    validate_race_parser.add_argument('--threshold', type=float, help='Confidence threshold')

    # Validate-race-ltr command (A/B test validation)
    validate_ltr_parser = subparsers.add_parser('validate-race-ltr', help='Validate LTR predictions and update A/B experiment')
    validate_ltr_parser.add_argument('--ltr-predictions', required=True, help='Path to LTR predictions CSV')
    validate_ltr_parser.add_argument('--v6-predictions', required=True, help='Path to v6.x predictions CSV')
    validate_ltr_parser.add_argument('--results', required=True, help='Path to results CSV')
    validate_ltr_parser.add_argument('--race-name', required=True, help='Race name (e.g., Diegem)')
    validate_ltr_parser.add_argument('--race-date', required=True, help='Race date (e.g., 2025-12-30)')
    validate_ltr_parser.add_argument('--category', required=True, help='Category (e.g., "Men Elite")')
    validate_ltr_parser.add_argument('--series', default='Superprestige', help='Series name')

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
    elif args.command == 'backfill-distribution':
        backfill_distribution_metrics()
    elif args.command == 'update-reports':
        update_validation_reports_with_distribution()
    elif args.command == 'update-predictions':
        update_prediction_reports_with_distribution()
    elif args.command == 'validate-race':
        # Full validation with auto-updates
        print(f"=" * 70)
        print(f"VELOPREDICT: VALIDATE RACE (with auto-updates)")
        print(f"=" * 70)
        print(f"Race: {args.race_name} ({args.category})")
        print(f"Date: {args.race_date}")
        print(f"Series: {args.series}")

        # Run validation
        validation_results = validate(args.predictions, args.results, args.threshold)

        if validation_results:
            # Update registry
            race_id = f"{args.race_name.lower()}_{args.race_date}"
            print(f"\n[AUTO-UPDATE] Updating registry...")
            update_registry_validation(race_id, args.category, validation_results)

            # Update SEASON_TRACKER.md
            print(f"[AUTO-UPDATE] Updating SEASON_TRACKER.md...")
            registry = load_registry()
            model_version = registry.get("current_version", "v6.4")
            update_season_tracker(args.race_name, args.race_date, args.series, args.category, validation_results)
            add_race_details_to_tracker(args.race_name, args.race_date, args.category, validation_results)
            update_season_summary_table(args.race_name, args.race_date, args.series, args.category, model_version, validation_results)

            # Load predictions to get distribution data
            try:
                predictions_df = pd.read_csv(args.predictions)
                distribution_data = get_distribution_from_predictions(predictions_df)

                # Update distribution tables
                print(f"[AUTO-UPDATE] Updating distribution tables...")
                update_distribution_tables(args.race_name, args.race_date, args.category,
                                          distribution_data, validation_results)

                # Update season trend charts
                print(f"[AUTO-UPDATE] Updating season trend charts...")
                update_season_trend_charts(args.race_name, model_version, distribution_data)
            except Exception as e:
                print(f"  Warning: Could not update distribution data: {e}")

            # Update VERSION_HISTORY.md
            print(f"[AUTO-UPDATE] Updating VERSION_HISTORY.md...")
            try:
                # Get training stats from model metadata
                model_metadata_path = config.MODELS_DIR / "model_metadata.json"
                training_stats = None
                if model_metadata_path.exists():
                    with open(model_metadata_path) as f:
                        metadata = json.load(f)
                        training_stats = {
                            'observations': metadata.get('training_samples', 0),
                            'races': metadata.get('num_races', 0),
                            'accuracy': metadata.get('top10_accuracy', 0)
                        }

                update_version_history_current(args.race_name, args.race_date, model_version,
                                               args.category, validation_results, training_stats)
            except Exception as e:
                print(f"  Warning: Could not update VERSION_HISTORY.md: {e}")

            # Generate validation report
            print(f"\n[AUTO-UPDATE] Generating validation report...")
            matched_df = pd.DataFrame([{
                'rider': d['rider'],
                'prob': d['prob'],
                'actual_place': d['actual_place'] if isinstance(d['actual_place'], int) else 999,
                'predicted_top10': True,
                'actual_top10': d['hit']
            } for d in validation_results['pred_top10_detail']])

            report_path = generate_validation_report(
                validation_results,
                matched_df,
                args.race_name,
                args.race_date,
                args.category,
                args.series
            )
            print(f"  Validation report: {report_path}")

            print(f"\n" + "=" * 70)
            print(f"VALIDATION COMPLETE - All trackers updated")
            print(f"=" * 70)
    elif args.command == 'validate-race-ltr':
        # LTR A/B test validation with auto-updates
        print(f"=" * 70)
        print(f"VELOPREDICT: VALIDATE LTR A/B TEST")
        print(f"=" * 70)
        print(f"Race: {args.race_name} ({args.category})")
        print(f"Date: {args.race_date}")
        print(f"Series: {args.series}")

        # Validate v6.x predictions
        print(f"\n[1/4] Validating v6.x predictions...")
        v6_results = validate(args.v6_predictions, args.results)

        if not v6_results:
            print(f"Error: v6.x validation failed")
        else:
            print(f"  v6.x: Hits@10={v6_results['hits_10']}/10, Hits@3={v6_results['hits_3']}/3")

            # Validate LTR predictions
            print(f"\n[2/4] Validating LTR predictions...")
            ltr_results = validate_ltr_predictions(args.ltr_predictions, args.results)
            print(f"  LTR:  Hits@10={ltr_results['hits_10']}/10, Hits@3={ltr_results['hits_3']}/3")

            # Determine winner
            ltr_wins = 0
            v6_wins = 0
            if ltr_results['hits_10'] > v6_results['hits_10']:
                ltr_wins += 1
            elif v6_results['hits_10'] > ltr_results['hits_10']:
                v6_wins += 1
            if ltr_results['hits_3'] > v6_results['hits_3']:
                ltr_wins += 1
            elif v6_results['hits_3'] > ltr_results['hits_3']:
                v6_wins += 1
            if ltr_results['spearman'] > v6_results['spearman']:
                ltr_wins += 1
            elif v6_results['spearman'] > ltr_results['spearman']:
                v6_wins += 1
            if ltr_results['mae_rank'] < v6_results['mae_rank']:
                ltr_wins += 1
            elif v6_results['mae_rank'] < ltr_results['mae_rank']:
                v6_wins += 1

            winner = "LTR" if ltr_wins > v6_wins else ("v6.x" if v6_wins > ltr_wins else "TIE")
            print(f"\n  Winner: {winner} (LTR: {ltr_wins}, v6.x: {v6_wins})")

            # Update LTR experiment doc
            print(f"\n[3/4] Updating LTR_EXPERIMENT.md...")
            registry = load_registry()
            v6_model = registry.get("current_version", "v6.10")
            update_ltr_experiment(args.race_name, args.race_date, args.series, args.category,
                                  v6_results, ltr_results, v6_model)

            # Generate/update LTR validation report
            print(f"\n[4/4] Generating LTR validation report...")
            ltr_pred_df = pd.read_csv(args.ltr_predictions)
            results_df = pd.read_csv(args.results)
            report_path = generate_ltr_validation_report(
                args.race_name, args.race_date, args.category,
                v6_results, ltr_results, ltr_pred_df, results_df
            )
            print(f"  Report: {report_path}")

            print(f"\n" + "=" * 70)
            print(f"LTR VALIDATION COMPLETE")
            print(f"  Winner: {winner}")
            print(f"  LTR_EXPERIMENT.md updated")
            print(f"  {args.race_name.upper()}_LTR_PREDICTIONS_{args.race_date}.md updated")
            print(f"=" * 70)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
