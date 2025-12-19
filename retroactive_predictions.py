"""
Retroactive predictions for v6.4 model evaluation.
Runs predictions on historical races and calculates new metrics:
- Hits@10: How many of top-10 predictions made actual top-10
- Hits@3: How many of top-3 predictions made actual podium
- Spearman Correlation: Rank correlation between predicted and actual
- MAE Rank: Mean absolute error of rank positions
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

from predict_race import predict_race
from src.features.names import standardize_name


def clean_name(name):
    """Clean name from various formats to LASTNAME Firstname."""
    if pd.isna(name):
        return ""

    name = str(name).strip()

    # Handle FIRSTNAME\nLASTNAME format (Tabor Men style)
    if '\n' in name:
        parts = name.split('\n')
        if len(parts) == 2:
            # FIRSTNAME\nLASTNAME -> LASTNAME Firstname
            firstname = parts[0].strip().title()
            lastname = parts[1].strip().upper()
            return f"{lastname} {firstname}"

    # Handle all-caps "FIRSTNAME LASTNAME" format (Tabor Women style)
    # e.g., "LUCINDA BRAND" -> "BRAND Lucinda"
    if name.isupper():
        parts = name.split()
        if len(parts) >= 2:
            firstname = parts[0].title()
            lastname = ' '.join(parts[1:])  # Keep uppercase
            return f"{lastname} {firstname}"
        return name

    # Handle "Firstname Lastname" (Kortrijk style) - convert to "LASTNAME Firstname"
    parts = name.strip().split()
    if len(parts) >= 2:
        # Check if it looks like "Firstname Lastname" (first word is title case)
        if parts[0][0].isupper() and len(parts[0]) > 1 and parts[0][1:].islower():
            # Assume Firstname Lastname format
            firstname = parts[0]
            lastname = ' '.join(parts[1:]).upper()
            return f"{lastname} {firstname}"

    return name


def parse_results_file(results_path):
    """Parse results CSV - handles multiple formats from different sources."""
    df = pd.read_csv(results_path)

    # Detect format and normalize to: Place, Name
    results = []

    # Check which columns exist
    columns = df.columns.tolist()

    # Format 1: "Position", "Name" (Namur, Sardinia style)
    if 'Position' in columns and 'Name' in columns:
        for _, row in df.iterrows():
            place = row['Position']
            if pd.isna(place) or str(place).strip() == '':
                continue
            # Skip non-numeric places (DNF, DNS, etc.)
            try:
                place_int = int(place)
            except (ValueError, TypeError):
                continue
            results.append({
                'Place': place_int,
                'Name': clean_name(row['Name'])
            })

    # Format 2: "Place", "Name" (Flamanville style with "Category Name")
    elif 'Place' in columns and 'Name' in columns:
        for _, row in df.iterrows():
            place = row['Place']
            if pd.isna(place) or str(place).strip() == '':
                continue
            results.append({
                'Place': int(place),
                'Name': clean_name(row['Name'])
            })

    # Format 3: Multi-line name format (Tabor old style)
    elif 'Place' in columns or df.columns[0] == 'Place':
        # Try reading with the place column
        place_col = 'Place' if 'Place' in columns else df.columns[0]
        name_col = 'Name' if 'Name' in columns else df.columns[1]
        for _, row in df.iterrows():
            place = row[place_col]
            if pd.isna(place) or str(place).strip() == '' or not str(place).isdigit():
                continue
            results.append({
                'Place': int(place),
                'Name': clean_name(row[name_col])
            })

    else:
        # Try generic: first column is position-like, second is name-like
        for _, row in df.iterrows():
            first_val = row.iloc[0]
            if pd.isna(first_val):
                continue
            try:
                place = int(first_val)
                name = row.iloc[1]
                results.append({
                    'Place': place,
                    'Name': clean_name(name)
                })
            except (ValueError, TypeError):
                continue

    return pd.DataFrame(results)


def calculate_metrics(predictions_df, results_df):
    """
    Calculate new metrics for predictions vs actual results.

    Returns dict with:
    - hits_10: Number of predicted top-10 in actual top-10
    - hits_3: Number of predicted podium in actual podium
    - spearman: Spearman rank correlation
    - mae_rank: Mean absolute error of ranks
    """
    # Get top-10 predictions (sorted by probability, take top 10)
    pred_top10 = predictions_df.nlargest(10, 'Top-10 Probability')
    pred_top10_names = set(standardize_name(n) for n in pred_top10['Rider'])

    # Get top-3 predictions (sorted by podium probability, take top 3)
    pred_top3 = predictions_df.nlargest(3, 'Top-3 Probability')
    pred_top3_names = set(standardize_name(n) for n in pred_top3['Rider'])

    # Get actual top-10 and top-3
    actual_top10 = results_df[results_df['Place'] <= 10]
    actual_top10_names = set(standardize_name(n) for n in actual_top10['Name'])

    actual_top3 = results_df[results_df['Place'] <= 3]
    actual_top3_names = set(standardize_name(n) for n in actual_top3['Name'])

    # Calculate Hits@10 and Hits@3
    hits_10 = len(pred_top10_names & actual_top10_names)
    hits_3 = len(pred_top3_names & actual_top3_names)

    # For Spearman correlation, match predicted ranks with actual ranks
    # Only use riders that appear in both predictions and results
    pred_ranks = {}
    for idx, (_, row) in enumerate(pred_top10.iterrows(), 1):
        name_std = standardize_name(row['Rider'])
        pred_ranks[name_std] = idx

    actual_ranks = {}
    for _, row in actual_top10.iterrows():
        name_std = standardize_name(row['Name'])
        actual_ranks[name_std] = row['Place']

    # Find common riders
    common = set(pred_ranks.keys()) & set(actual_ranks.keys())

    if len(common) >= 2:
        pred_r = [pred_ranks[n] for n in common]
        actual_r = [actual_ranks[n] for n in common]
        spearman, _ = stats.spearmanr(pred_r, actual_r)
    else:
        spearman = np.nan

    # MAE on rank for predicted top-10 that finished
    mae_values = []
    for name_std in pred_top10_names:
        pred_rank = pred_ranks.get(name_std)
        # Find actual rank
        matched = results_df[results_df['Name'].apply(standardize_name) == name_std]
        if len(matched) > 0:
            actual_rank = matched.iloc[0]['Place']
            mae_values.append(abs(pred_rank - actual_rank))

    mae_rank = np.mean(mae_values) if mae_values else np.nan

    # Detailed breakdown
    pred_top10_detail = []
    for idx, (_, row) in enumerate(pred_top10.iterrows(), 1):
        name_std = standardize_name(row['Rider'])
        matched = results_df[results_df['Name'].apply(standardize_name) == name_std]
        actual_place = matched.iloc[0]['Place'] if len(matched) > 0 else 'DNF/DNS'
        in_top10 = actual_place <= 10 if isinstance(actual_place, (int, float)) else False
        pred_top10_detail.append({
            'pred_rank': idx,
            'rider': row['Rider'],
            'prob': row['Top-10 Probability'],
            'actual_place': actual_place,
            'hit': in_top10
        })

    return {
        'hits_10': hits_10,
        'hits_3': hits_3,
        'spearman': spearman,
        'mae_rank': mae_rank,
        'pred_top10_detail': pred_top10_detail,
        'pred_top3_names': list(pred_top3_names),
        'actual_top3_names': list(actual_top3_names)
    }


def run_retroactive_predictions():
    """Run v6.4 predictions on all historical races."""
    races = [
        {
            'name': 'Tabor',
            'date': '2025-11-23',
            'series': 'UCI World Cup',
            'men_startlist': 'data/startlists/tabor_men_elite_2025-11-23.csv',
            'women_startlist': 'data/startlists/tabor_women_elite_2025-11-23.csv',
            'men_results': 'data/results/Results__UCI-World-Cup__Tabor__Men-Elite__2025-11-23__Tabor-CZECHIA.csv',
            'women_results': 'data/results/Results__UCI-World-Cup__Tabor__Women-Elite__2025-11-23__Tabor-CZECHIA.csv',
            'original_version': 'v1'
        },
        {
            'name': 'Flamanville',
            'date': '2025-11-30',
            'series': 'UCI World Cup',
            'men_startlist': 'data/startlists/flamanville_men_elite_2025-11-30.csv',
            'women_startlist': 'data/startlists/flamanville_women_elite_2025-11-30.csv',
            'men_results': 'data/results/Results__UCI-World-Cup__Flamanville__Men-Elite__2025-11-30__Flamanville-FRANCE.csv',
            'women_results': 'data/results/Results__UCI-World-Cup__Flamanville__Women-Elite__2025-11-30__Flamanville-FRANCE.csv',
            'original_version': 'v2'
        },
        {
            'name': 'Sardinia',
            'date': '2025-12-07',
            'series': 'UCI World Cup',
            'men_startlist': 'data/startlists/sardinia_men_elite_2025-12-07.csv',
            'women_startlist': 'data/startlists/sardinia_women_elite_2025-12-07.csv',
            'men_results': 'data/results/Results__UCI-World-Cup__Sardinia__Men-Elite__2025-12-07__Sardinia-ITALY.csv',
            'women_results': 'data/results/Results__UCI-World-Cup__Sardinia__Women-Elite__2025-12-07__Sardinia-ITALY.csv',
            'original_version': 'v6'
        },
        {
            'name': 'Kortrijk',
            'date': '2025-12-13',
            'series': 'Exact Cross',
            'men_startlist': 'data/startlists/Exact-Cross-Kortrijk_men_elite_2025-12-13.csv',
            'women_startlist': 'data/startlists/Exact-Cross-Kortrijk_women_elite_2025-12-13.csv',
            'men_results': 'data/results/Results__Exact-Cross__ Kortrijk__Men-Elite__2025-12-13__ Kortrijk -BELGIUM.csv',
            'women_results': 'data/results/Results__Exact-Cross__ Kortrijk__Women-Elite__2025-12-13__ Kortrijk -BELGIUM.csv',
            'original_version': 'v6.2'
        },
        {
            'name': 'Namur',
            'date': '2025-12-14',
            'series': 'UCI World Cup',
            'men_startlist': 'data/startlists/namur_men_elite_2025-12-14.csv',
            'women_startlist': 'data/startlists/namur_women_elite_2025-12-14.csv',
            'men_results': 'data/results/Results__UCI-WorldCup__ Namur__Men-Elite__2025-12-14__ Namur -BELGIUM.csv',
            'women_results': 'data/results/Results__UCI-WorldCup__ Namur__Women-Elite__2025-12-14__ Namur -BELGIUM.csv',
            'original_version': 'v6.1'
        }
    ]

    all_results = []

    for race in races:
        print(f"\n{'='*70}")
        print(f"RETROACTIVE PREDICTIONS: {race['name']} ({race['date']})")
        print(f"{'='*70}")

        for category, startlist_key, results_key in [
            ('Men Elite', 'men_startlist', 'men_results'),
            ('Women Elite', 'women_startlist', 'women_results')
        ]:
            print(f"\n--- {category} ---")

            startlist_path = Path(race[startlist_key])
            results_path = Path(race[results_key])

            if not startlist_path.exists():
                print(f"  Startlist not found: {startlist_path}")
                continue

            if not results_path.exists():
                print(f"  Results not found: {results_path}")
                continue

            # Run predictions
            try:
                predictions = predict_race(
                    str(startlist_path),
                    category=category,
                    confidence_threshold=0.0  # We want all probabilities for ranking
                )
            except Exception as e:
                print(f"  Error running predictions: {e}")
                continue

            # Parse results
            try:
                results = parse_results_file(results_path)
            except Exception as e:
                print(f"  Error parsing results: {e}")
                continue

            # Calculate metrics
            metrics = calculate_metrics(predictions, results)

            # Print results
            print(f"\n  Results for {race['name']} {category}:")
            print(f"  Hits@10: {metrics['hits_10']}/10")
            print(f"  Hits@3: {metrics['hits_3']}/3")
            print(f"  Spearman ρ: {metrics['spearman']:.3f}" if not np.isnan(metrics['spearman']) else "  Spearman ρ: N/A")
            print(f"  MAE Rank: {metrics['mae_rank']:.1f}" if not np.isnan(metrics['mae_rank']) else "  MAE Rank: N/A")

            print(f"\n  Predicted Top-10 breakdown:")
            for p in metrics['pred_top10_detail']:
                status = "✓" if p['hit'] else "✗"
                print(f"    {p['pred_rank']:2d}. {p['rider'][:25]:25s} ({p['prob']*100:4.1f}%) → P{p['actual_place']} {status}")

            all_results.append({
                'race': race['name'],
                'date': race['date'],
                'series': race['series'],
                'category': category,
                'original_version': race['original_version'],
                'hits_10': metrics['hits_10'],
                'hits_3': metrics['hits_3'],
                'spearman': metrics['spearman'],
                'mae_rank': metrics['mae_rank']
            })

    # Summary
    print(f"\n{'='*70}")
    print("RETROACTIVE PREDICTIONS SUMMARY (v6.4)")
    print(f"{'='*70}\n")

    df = pd.DataFrame(all_results)
    print(df.to_string(index=False))

    print(f"\nAggregates:")
    print(f"  Avg Hits@10: {df['hits_10'].mean():.1f}/10")
    print(f"  Avg Hits@3: {df['hits_3'].mean():.1f}/3")
    print(f"  Avg Spearman ρ: {df['spearman'].mean():.3f}")
    print(f"  Avg MAE Rank: {df['mae_rank'].mean():.1f}")

    # Save results
    output_path = Path('data/clean/retroactive_v64_results.csv')
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")

    return df


if __name__ == "__main__":
    run_retroactive_predictions()
