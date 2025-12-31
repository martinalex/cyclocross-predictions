"""
Update LTR_EXPERIMENT.md validation summary table from validation results JSON.
Run this after validating a new race to update the experiment documentation.
"""
import json
import re
from pathlib import Path

DATA_DIR = Path("data/clean")
VALIDATION_FILE = DATA_DIR / "ltr_validation_results.json"
EXPERIMENT_FILE = Path("LTR_EXPERIMENT.md")


def load_validation_results():
    """Load validation results from JSON"""
    with open(VALIDATION_FILE, 'r') as f:
        return json.load(f)


def generate_validation_table(data):
    """Generate markdown validation summary table"""
    lines = []

    # Header
    lines.append("## Validation Summary")
    lines.append("")
    lines.append("### v7.1-LTR vs v6.x Performance")
    lines.append("")
    lines.append("| Race                | Date       | Category | Model   | Hits@10 | Hits@3 | Spearman | MAE  | Winner  |")
    lines.append("|:-------------------:|:----------:|:--------:|:-------:|:-------:|:------:|:--------:|:----:|:-------:|")

    # Data rows
    for v in data["validations"]:
        race = v["race"]
        date = v["date"]
        cat = "Men" if "Men" in v["category"] else "Women"

        # v6 row
        v6_hits10 = f"{v['v6_hits10']}/10"
        v6_hits3 = f"{v['v6_hits3']}/3"
        v6_spearman = f"{v['v6_spearman']:.2f}"
        v6_mae = f"{v['v6_mae']:.1f}"

        # LTR row
        ltr_hits10 = f"{v['ltr_hits10']}/10"
        ltr_hits3 = f"{v['ltr_hits3']}/3"
        ltr_spearman = f"{v['ltr_spearman']:.2f}"
        ltr_mae = f"{v['ltr_mae']:.1f}"

        # Bold winners
        if v['ltr_hits10'] > v['v6_hits10']:
            ltr_hits10 = f"**{ltr_hits10}**"
        elif v['v6_hits10'] > v['ltr_hits10']:
            v6_hits10 = f"**{v6_hits10}**"

        if v['ltr_hits3'] > v['v6_hits3']:
            ltr_hits3 = f"**{ltr_hits3}**"
        elif v['v6_hits3'] > v['ltr_hits3']:
            v6_hits3 = f"**{v6_hits3}**"

        if v['ltr_spearman'] > v['v6_spearman']:
            ltr_spearman = f"**{ltr_spearman}**"
        elif v['v6_spearman'] > v['ltr_spearman']:
            v6_spearman = f"**{v6_spearman}**"

        if v['ltr_mae'] < v['v6_mae']:
            ltr_mae = f"**{ltr_mae}**"
        elif v['v6_mae'] < v['ltr_mae']:
            v6_mae = f"**{v6_mae}**"

        winner_str = f"**{v['winner']}**" if v['winner'] != "TIE" else "TIE"

        lines.append(f"| {race:19s} | {date} | {cat:8s} | {v['v6_model']:7s} | {v6_hits10:7s} | {v6_hits3:6s} | {v6_spearman:8s} | {v6_mae:4s} |         |")
        lines.append(f"|                     |            |          | v7.1-LTR| {ltr_hits10:7s} | {ltr_hits3:6s} | {ltr_spearman:8s} | {ltr_mae:4s} | {winner_str:7s} |")

    # Aggregate results
    agg = data["aggregate"]
    lines.append("")
    lines.append("### Aggregate Results")
    lines.append("")
    lines.append("|   Metric    | v6.x Total | v7.1-LTR Total | Winner  |")
    lines.append("|:-----------:|:----------:|:--------------:|:-------:|")

    # Hits@10
    v6_h10 = f"{agg['v6_hits10_total']}/{agg['v6_hits10_possible']}"
    ltr_h10 = f"{agg['ltr_hits10_total']}/{agg['ltr_hits10_possible']}"
    if agg['ltr_hits10_total'] > agg['v6_hits10_total']:
        ltr_h10 = f"**{ltr_h10}**"
        h10_winner = "**LTR**"
    elif agg['v6_hits10_total'] > agg['ltr_hits10_total']:
        v6_h10 = f"**{v6_h10}**"
        h10_winner = "**v6.x**"
    else:
        h10_winner = "TIE"
    lines.append(f"| Hits@10     | {v6_h10:10s} | {ltr_h10:14s} | {h10_winner:7s} |")

    # Hits@3
    v6_h3 = f"{agg['v6_hits3_total']}/{agg['v6_hits3_possible']}"
    ltr_h3 = f"{agg['ltr_hits3_total']}/{agg['ltr_hits3_possible']}"
    if agg['ltr_hits3_total'] > agg['v6_hits3_total']:
        ltr_h3 = f"**{ltr_h3}**"
        h3_winner = "**LTR**"
    elif agg['v6_hits3_total'] > agg['ltr_hits3_total']:
        v6_h3 = f"**{v6_h3}**"
        h3_winner = "**v6.x**"
    else:
        h3_winner = "TIE"
    lines.append(f"| Hits@3      | {v6_h3:10s} | {ltr_h3:14s} | {h3_winner:7s} |")

    # Avg MAE
    v6_mae = f"{agg['v6_avg_mae']:.1f}"
    ltr_mae = f"{agg['ltr_avg_mae']:.1f}"
    if agg['ltr_avg_mae'] < agg['v6_avg_mae']:
        ltr_mae = f"**{ltr_mae}**"
        mae_winner = "**LTR**"
    elif agg['v6_avg_mae'] < agg['ltr_avg_mae']:
        v6_mae = f"**{v6_mae}**"
        mae_winner = "**v6.x**"
    else:
        mae_winner = "TIE"
    lines.append(f"| Avg MAE     | {v6_mae:10s} | {ltr_mae:14s} | {mae_winner:7s} |")

    # Races won
    v6_wins = str(agg['v6_wins'])
    ltr_wins = str(agg['ltr_wins'])
    if agg['ltr_wins'] > agg['v6_wins']:
        ltr_wins = f"**{ltr_wins}**"
        wins_winner = "**LTR**"
    elif agg['v6_wins'] > agg['ltr_wins']:
        v6_wins = f"**{v6_wins}**"
        wins_winner = "**v6.x**"
    else:
        wins_winner = "TIE"
    lines.append(f"| Races Won   | {v6_wins:10s} | {ltr_wins:14s} | {wins_winner:7s} |")

    # Overall summary
    total_metrics = agg['v6_wins'] + agg['ltr_wins'] + agg['ties']
    if agg['ltr_wins'] > agg['v6_wins']:
        overall = f"**Overall: v7.1-LTR wins {agg['ltr_wins']}-{agg['v6_wins']}-{agg['ties']}**"
    elif agg['v6_wins'] > agg['ltr_wins']:
        overall = f"**Overall: v6.x wins {agg['v6_wins']}-{agg['ltr_wins']}-{agg['ties']}**"
    else:
        overall = f"**Overall: TIE {agg['v6_wins']}-{agg['ltr_wins']}-{agg['ties']}**"

    lines.append("")
    lines.append(overall)
    lines.append("")
    lines.append("---")

    return "\n".join(lines)


def update_experiment_file(validation_table):
    """Update LTR_EXPERIMENT.md with new validation summary"""
    with open(EXPERIMENT_FILE, 'r') as f:
        content = f.read()

    # Find and replace the validation summary section
    # Pattern: from "## Validation Summary" to "---" before "## Overview"
    pattern = r"## Validation Summary.*?---\n\n## Overview"
    replacement = validation_table + "\n\n## Overview"

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(EXPERIMENT_FILE, 'w') as f:
        f.write(new_content)

    print(f"Updated {EXPERIMENT_FILE}")


def add_validation(race, date, series, category,
                   v6_model, v6_hits10, v6_hits3, v6_spearman, v6_mae,
                   ltr_hits10, ltr_hits3, ltr_spearman, ltr_mae,
                   dns_count=0, notes=""):
    """Add a new validation result and update the experiment doc"""

    # Load existing data
    data = load_validation_results()

    # Determine winner for this race
    ltr_wins = 0
    v6_wins = 0

    if ltr_hits10 > v6_hits10:
        ltr_wins += 1
    elif v6_hits10 > ltr_hits10:
        v6_wins += 1

    if ltr_hits3 > v6_hits3:
        ltr_wins += 1
    elif v6_hits3 > ltr_hits3:
        v6_wins += 1

    if ltr_spearman > v6_spearman:
        ltr_wins += 1
    elif v6_spearman > ltr_spearman:
        v6_wins += 1

    if ltr_mae < v6_mae:
        ltr_wins += 1
    elif v6_mae < ltr_mae:
        v6_wins += 1

    if ltr_wins > v6_wins:
        winner = "LTR"
    elif v6_wins > ltr_wins:
        winner = "v6.x"
    else:
        winner = "TIE"

    # Add new validation
    new_validation = {
        "race": race,
        "date": date,
        "series": series,
        "category": category,
        "v6_model": v6_model,
        "v6_hits10": v6_hits10,
        "v6_hits3": v6_hits3,
        "v6_spearman": v6_spearman,
        "v6_mae": v6_mae,
        "ltr_hits10": ltr_hits10,
        "ltr_hits3": ltr_hits3,
        "ltr_spearman": ltr_spearman,
        "ltr_mae": ltr_mae,
        "winner": winner,
        "dns_count": dns_count,
        "notes": notes
    }

    data["validations"].append(new_validation)

    # Recalculate aggregates
    agg = data["aggregate"]
    agg["total_races"] = len(data["validations"])
    agg["v6_hits10_total"] = sum(v["v6_hits10"] for v in data["validations"])
    agg["ltr_hits10_total"] = sum(v["ltr_hits10"] for v in data["validations"])
    agg["v6_hits10_possible"] = agg["total_races"] * 10
    agg["ltr_hits10_possible"] = agg["total_races"] * 10
    agg["v6_hits3_total"] = sum(v["v6_hits3"] for v in data["validations"])
    agg["ltr_hits3_total"] = sum(v["ltr_hits3"] for v in data["validations"])
    agg["v6_hits3_possible"] = agg["total_races"] * 3
    agg["ltr_hits3_possible"] = agg["total_races"] * 3
    agg["v6_avg_mae"] = sum(v["v6_mae"] for v in data["validations"]) / agg["total_races"]
    agg["ltr_avg_mae"] = sum(v["ltr_mae"] for v in data["validations"]) / agg["total_races"]

    # Count wins
    v6_total_wins = 0
    ltr_total_wins = 0
    ties = 0
    for v in data["validations"]:
        if v["winner"] == "LTR":
            ltr_total_wins += 1
        elif v["winner"] == "v6.x":
            v6_total_wins += 1
        else:
            ties += 1

    # Count metric wins across all validations
    metric_v6_wins = 0
    metric_ltr_wins = 0
    metric_ties = 0
    for v in data["validations"]:
        # hits10
        if v["ltr_hits10"] > v["v6_hits10"]:
            metric_ltr_wins += 1
        elif v["v6_hits10"] > v["ltr_hits10"]:
            metric_v6_wins += 1
        else:
            metric_ties += 1
        # hits3
        if v["ltr_hits3"] > v["v6_hits3"]:
            metric_ltr_wins += 1
        elif v["v6_hits3"] > v["ltr_hits3"]:
            metric_v6_wins += 1
        else:
            metric_ties += 1
        # spearman
        if v["ltr_spearman"] > v["v6_spearman"]:
            metric_ltr_wins += 1
        elif v["v6_spearman"] > v["ltr_spearman"]:
            metric_v6_wins += 1
        else:
            metric_ties += 1
        # mae
        if v["ltr_mae"] < v["v6_mae"]:
            metric_ltr_wins += 1
        elif v["v6_mae"] < v["ltr_mae"]:
            metric_v6_wins += 1
        else:
            metric_ties += 1

    agg["v6_wins"] = metric_v6_wins
    agg["ltr_wins"] = metric_ltr_wins
    agg["ties"] = metric_ties

    data["last_updated"] = str(pd.Timestamp.now().date()) if 'pd' in dir() else date

    # Save updated data
    with open(VALIDATION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Added validation for {race} ({category})")
    print(f"  Winner: {winner}")

    # Update experiment file
    validation_table = generate_validation_table(data)
    update_experiment_file(validation_table)

    return data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update LTR experiment validation summary")
    parser.add_argument("--refresh", action="store_true", help="Just refresh the experiment doc from existing JSON")

    args = parser.parse_args()

    if args.refresh:
        data = load_validation_results()
        validation_table = generate_validation_table(data)
        update_experiment_file(validation_table)
        print("Refreshed LTR_EXPERIMENT.md from validation results")
    else:
        print("Usage:")
        print("  python update_ltr_experiment.py --refresh  # Refresh from existing JSON")
        print("")
        print("To add new validation, import and call add_validation():")
        print("  from update_ltr_experiment import add_validation")
        print("  add_validation('Race Name', '2025-12-30', 'Series', 'Men Elite',")
        print("                 'v6.12', 6, 2, 0.64, 2.7,")
        print("                 7, 1, 0.52, 2.9)")
