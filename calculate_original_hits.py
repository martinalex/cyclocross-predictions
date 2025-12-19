"""
Calculate Hits@10 and Hits@3 for original predictions.
Uses the prediction files from race_registry.json and compares against actual results.
"""
import pandas as pd
import json
from pathlib import Path
from src.features.names import standardize_name


def clean_name(name):
    """Clean name from various formats."""
    if pd.isna(name):
        return ""

    name = str(name).strip()

    # Handle FIRSTNAME\nLASTNAME format
    if '\n' in name:
        parts = name.split('\n')
        if len(parts) == 2:
            firstname = parts[0].strip().title()
            lastname = parts[1].strip().upper()
            return f"{lastname} {firstname}"

    # Handle all-caps "FIRSTNAME LASTNAME" format
    if name.isupper():
        parts = name.split()
        if len(parts) >= 2:
            firstname = parts[0].title()
            lastname = ' '.join(parts[1:])
            return f"{lastname} {firstname}"
        return name

    # Handle "Firstname Lastname" format
    parts = name.strip().split()
    if len(parts) >= 2:
        if parts[0][0].isupper() and len(parts[0]) > 1 and parts[0][1:].islower():
            firstname = parts[0]
            lastname = ' '.join(parts[1:]).upper()
            return f"{lastname} {firstname}"

    return name


def parse_results(results_path):
    """Parse results CSV and return DataFrame with Place, Name."""
    df = pd.read_csv(results_path)
    columns = df.columns.tolist()

    results = []

    if 'Position' in columns and 'Name' in columns:
        for _, row in df.iterrows():
            place = row['Position']
            if pd.isna(place):
                continue
            try:
                place_int = int(place)
            except (ValueError, TypeError):
                continue
            results.append({'Place': place_int, 'Name': clean_name(row['Name'])})

    elif 'Place' in columns and 'Name' in columns:
        for _, row in df.iterrows():
            place = row['Place']
            if pd.isna(place):
                continue
            try:
                place_int = int(place)
            except (ValueError, TypeError):
                continue
            results.append({'Place': place_int, 'Name': clean_name(row['Name'])})

    return pd.DataFrame(results)


def calculate_hits(predictions_df, results_df):
    """Calculate Hits@10 and Hits@3 for predictions."""
    # Determine column names for probability
    top10_col = None
    top3_col = None
    rider_col = None

    for col in predictions_df.columns:
        if 'top-10' in col.lower() or 'top10' in col.lower():
            if 'prob' in col.lower():
                top10_col = col
        if 'top-3' in col.lower() or 'top3' in col.lower():
            if 'prob' in col.lower():
                top3_col = col
        if 'rider' in col.lower() or 'name' in col.lower():
            rider_col = col

    if top10_col is None:
        # Try common column names
        for col in predictions_df.columns:
            if 'probability' in col.lower() and '10' in col:
                top10_col = col
                break
        if top10_col is None and 'Top-10 Probability' in predictions_df.columns:
            top10_col = 'Top-10 Probability'

    if top3_col is None:
        for col in predictions_df.columns:
            if 'probability' in col.lower() and '3' in col:
                top3_col = col
                break
        if top3_col is None and 'Top-3 Probability' in predictions_df.columns:
            top3_col = 'Top-3 Probability'

    if rider_col is None:
        if 'Rider' in predictions_df.columns:
            rider_col = 'Rider'
        elif 'Name' in predictions_df.columns:
            rider_col = 'Name'

    if top10_col is None or rider_col is None:
        print(f"  Columns: {predictions_df.columns.tolist()}")
        return None, None

    # Get top 10 by top-10 probability
    pred_top10 = predictions_df.nlargest(10, top10_col)
    pred_top10_names = set(standardize_name(n) for n in pred_top10[rider_col])

    # Get top 3 by top-3 probability (or top-10 if no top-3 column)
    prob_col_for_podium = top3_col if top3_col else top10_col
    pred_top3 = predictions_df.nlargest(3, prob_col_for_podium)
    pred_top3_names = set(standardize_name(n) for n in pred_top3[rider_col])

    # Get actual top-10 and top-3
    actual_top10 = results_df[results_df['Place'] <= 10]
    actual_top10_names = set(standardize_name(n) for n in actual_top10['Name'])

    actual_top3 = results_df[results_df['Place'] <= 3]
    actual_top3_names = set(standardize_name(n) for n in actual_top3['Name'])

    # Calculate hits
    hits_10 = len(pred_top10_names & actual_top10_names)
    hits_3 = len(pred_top3_names & actual_top3_names)

    return hits_10, hits_3


def main():
    # Load race registry
    with open('data/clean/race_registry.json', 'r') as f:
        registry = json.load(f)

    results = []

    for race in registry['races']:
        print(f"\n{'='*60}")
        print(f"Race: {race['name']} ({race['date']})")
        print(f"{'='*60}")

        for category in ['Men Elite', 'Women Elite']:
            pred_path = race['predictions'].get(category)
            results_path = race['results'].get(category)

            if not pred_path or not results_path:
                print(f"  {category}: Missing files")
                continue

            pred_file = Path(pred_path)
            results_file = Path(results_path)

            if not pred_file.exists():
                print(f"  {category}: Prediction file not found: {pred_path}")
                continue

            if not results_file.exists():
                print(f"  {category}: Results file not found: {results_path}")
                continue

            # Load predictions
            try:
                predictions = pd.read_csv(pred_file)
            except Exception as e:
                print(f"  {category}: Error loading predictions: {e}")
                continue

            # Load results
            try:
                race_results = parse_results(results_file)
            except Exception as e:
                print(f"  {category}: Error loading results: {e}")
                continue

            # Calculate hits
            hits_10, hits_3 = calculate_hits(predictions, race_results)

            if hits_10 is not None:
                print(f"  {category}: Hits@10 = {hits_10}/10, Hits@3 = {hits_3}/3")
                results.append({
                    'race': race['name'],
                    'date': race['date'],
                    'category': category,
                    'version': race['version'],
                    'hits_10': hits_10,
                    'hits_3': hits_3
                })
            else:
                print(f"  {category}: Could not calculate hits")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY: Original Prediction Hits@10 and Hits@3")
    print(f"{'='*60}\n")

    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    # Save
    df.to_csv('data/clean/original_prediction_hits.csv', index=False)
    print(f"\nSaved to data/clean/original_prediction_hits.csv")


if __name__ == "__main__":
    main()
