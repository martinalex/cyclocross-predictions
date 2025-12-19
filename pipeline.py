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


def _generate_category_section(predictions_df: pd.DataFrame, category: str, threshold: float) -> list:
    """Generate markdown lines for a single category's predictions."""
    lines = []

    # Include ALL riders (no DNS filtering) - DNS is just informational
    all_riders = predictions_df.copy()

    top10_preds = all_riders[
        all_riders["Top-10 Probability"] >= threshold
    ].sort_values("Top-10 Probability", ascending=False)

    # Borderline: between 30% and threshold (55%)
    borderline_preds = all_riders[
        (all_riders["Top-10 Probability"] >= 0.30) &
        (all_riders["Top-10 Probability"] < threshold)
    ].sort_values("Top-10 Probability", ascending=False)

    # Rest of field: below 30%
    rest_of_field = all_riders[
        all_riders["Top-10 Probability"] < 0.30
    ].sort_values("Top-10 Probability", ascending=False)

    high_conf = predictions_df[predictions_df["Top-10 Probability"] >= 0.70]

    lines.extend([
        f"## {category}",
        f"",
        f"**{len(predictions_df)} riders** | {len(top10_preds)} predicted Top-10 | {len(high_conf)} high confidence",
        f"",
        f"### Predicted Top-10",
        f"",
    ])

    # Build Top-10 table rows with Notes (DNS flag shown in notes if applicable)
    table_rows = []
    for i, (_, row) in enumerate(top10_preds.iterrows(), 1):
        h2h = f"{row['H2H Field Score']*100:.0f}%" if row['H2H Confidence'] > 0.3 else "N/A"
        form = f"{row['Recent Form']:.1f}" if pd.notna(row['Recent Form']) else "N/A"
        top10_pct = f"{row['Top-10 Probability']*100:.1f}%"
        top3_pct = f"{row['Top-3 Probability']*100:.1f}%"
        note = _generate_rider_note(row)

        # Add DNS flag to rider name if applicable
        if row.get('DNS Risk', False):
            rider_display = f"{row['Rider']} ⚠️"
        elif row['Top-10 Probability'] >= 0.70:
            rider_display = f"**{row['Rider']}**"
        else:
            rider_display = row['Rider']

        table_rows.append([i, rider_display, top10_pct, top3_pct, h2h, form, note])

    # Use format_markdown_table for aligned output
    headers = ['#', 'Rider', 'Top-10 %', 'Podium %', 'H2H', 'Form', 'Notes']
    alignments = ['right', 'left', 'right', 'right', 'right', 'right', 'left']
    lines.extend(format_markdown_table(headers, table_rows, alignments))

    lines.extend([
        f"",
        f"### Podium Prediction",
        f"",
    ])

    podium_top3 = all_riders.nlargest(3, "Top-3 Probability")
    medals = ["1.", "2.", "3."]
    for medal, (_, row) in zip(medals, podium_top3.iterrows()):
        dns_flag = " ⚠️" if row.get('DNS Risk', False) else ""
        lines.append(f"{medal} **{row['Rider']}**{dns_flag} ({row['Top-3 Probability']*100:.1f}%)")

    # Borderline section
    if len(borderline_preds) > 0:
        lines.extend([
            f"",
            f"### Borderline (30-55%)",
            f"",
        ])

        borderline_rows = []
        for _, row in borderline_preds.iterrows():
            h2h = f"{row['H2H Field Score']*100:.0f}%" if row['H2H Confidence'] > 0.3 else "N/A"
            form = f"{row['Recent Form']:.1f}" if pd.notna(row['Recent Form']) else "N/A"
            top10_pct = f"{row['Top-10 Probability']*100:.1f}%"
            note = _generate_rider_note(row)
            rider_display = f"{row['Rider']} ⚠️" if row.get('DNS Risk', False) else row['Rider']
            borderline_rows.append([rider_display, top10_pct, h2h, form, note])

        borderline_headers = ['Rider', 'Top-10 %', 'H2H', 'Form', 'Notes']
        borderline_alignments = ['left', 'right', 'right', 'right', 'left']
        lines.extend(format_markdown_table(borderline_headers, borderline_rows, borderline_alignments))

    # Full startlist - rest of field
    if len(rest_of_field) > 0:
        lines.extend([
            f"",
            f"### Rest of Field",
            f"",
        ])

        rest_rows = []
        for _, row in rest_of_field.iterrows():
            h2h = f"{row['H2H Field Score']*100:.0f}%" if row['H2H Confidence'] > 0.3 else "N/A"
            top10_pct = f"{row['Top-10 Probability']*100:.1f}%"
            rider_display = f"{row['Rider']} ⚠️" if row.get('DNS Risk', False) else row['Rider']
            rest_rows.append([rider_display, top10_pct, h2h])

        rest_headers = ['Rider', 'Top-10 %', 'H2H']
        rest_alignments = ['left', 'right', 'right']
        lines.extend(format_markdown_table(rest_headers, rest_rows, rest_alignments))

    # DNS risks legend (informational only)
    dns_risks = predictions_df[predictions_df["DNS Risk"] == True]
    if len(dns_risks) > 0:
        lines.extend([
            f"",
            f"*⚠️ = DNS risk flagged (limited recent races - may still start)*",
        ])

    lines.append("")
    return lines


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
    Includes probability distribution analysis for confidence tier insights.
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

        # Add new category section before distribution or metrics explanation (or footer if no metrics)
        distribution_marker = "---\n\n## Probability Distribution Analysis"
        metrics_marker = "---\n\n## Understanding the Metrics"
        footer_marker = "---\n\n*Generated by"

        new_section = _generate_category_section(predictions_df, category, threshold)
        new_section_text = "---\n\n" + '\n'.join(new_section)

        if distribution_marker in existing_content:
            # Insert before distribution section
            parts = existing_content.split(distribution_marker, 1)
            updated_content = parts[0] + new_section_text + distribution_marker + parts[1]
        elif metrics_marker in existing_content:
            # Insert before metrics section
            parts = existing_content.split(metrics_marker, 1)
            updated_content = parts[0] + new_section_text + metrics_marker + parts[1]
        elif footer_marker in existing_content:
            # No metrics section, insert before footer
            parts = existing_content.rsplit(footer_marker, 1)
            updated_content = parts[0] + new_section_text + footer_marker + parts[1]
        else:
            # No footer found, just append
            updated_content = existing_content + "\n" + new_section_text

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

    # Calculate and add distribution analysis section
    distribution = calculate_distribution_metrics(predictions_df)
    if distribution:
        lines.append("---")
        lines.append("")
        lines.extend(_generate_distribution_section(distribution))

    # Add metrics explanation section
    lines.append("---")
    lines.append("")
    lines.extend(_generate_metrics_explanation())

    lines.extend([
        f"---",
        f"",
        f"*Generated by VeloPredict pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
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
    """Generate markdown lines for a single category's validation results."""
    lines = []

    # Get correct/missed/false positives from matched data
    correct = matched_df[(matched_df['predicted_top10']) & (matched_df['actual_top10'])].sort_values('actual_place')
    missed = matched_df[(~matched_df['predicted_top10']) & (matched_df['actual_top10'])].sort_values('actual_place')
    false_pos = matched_df[(matched_df['predicted_top10']) & (~matched_df['actual_top10'])].sort_values('actual_place')

    # Build validation metrics table using format_markdown_table
    recall_val = f"{validation_results['recall']:.1%} ({len(correct)}/{validation_results['actual_top10']})"
    precision_val = f"{validation_results['precision']:.1%} ({len(correct)}/{validation_results['predicted_top10']})"
    high_conf_val = f"{validation_results.get('high_conf_accuracy', 0):.1%}"

    lines.extend([
        f"## {category}",
        f"",
    ])

    metrics_headers = ['Metric', 'Value']
    metrics_rows = [
        ['**Recall**', recall_val],
        ['**Precision**', precision_val],
        ['High Confidence Accuracy', high_conf_val],
    ]
    lines.extend(format_markdown_table(metrics_headers, metrics_rows, ['left', 'left']))

    lines.extend([
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

    return {
        'recall': recall,
        'precision': precision,
        'high_conf_accuracy': high_conf_accuracy,
        'podium_accuracy': podium_accuracy,
        'matched': len(df),
        'predicted_top10': len(predicted_top10),
        'actual_top10': len(actual_top10),
        'distribution': distribution
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

    # Backfill distribution command
    backfill_parser = subparsers.add_parser('backfill-distribution', help='Calculate distribution metrics for all races')

    # Update validation reports command
    update_reports_parser = subparsers.add_parser('update-reports', help='Add distribution section to validation reports')

    # Update prediction reports command
    update_predictions_parser = subparsers.add_parser('update-predictions', help='Add distribution section to prediction reports')

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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
