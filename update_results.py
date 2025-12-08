"""
Update results_with_features.csv with Tabor and Flamanville results
Then recompute features for all riders
"""
import pandas as pd
import numpy as np
from pathlib import Path
import re

DATA_DIR = Path("data")
CLEAN_DIR = DATA_DIR / "clean"
RESULTS_DIR = DATA_DIR / "results"

print("=" * 60)
print("UPDATING RESULTS WITH TABOR, FLAMANVILLE & SARDINIA")
print("=" * 60)

# Load existing results
existing = pd.read_csv(CLEAN_DIR / "results_with_features.csv", parse_dates=["race_date"])
print(f"\nExisting results: {len(existing)} rows")
print(f"Date range: {existing['race_date'].min()} to {existing['race_date'].max()}")

# Helper function to normalize names
def normalize_name(s):
    if pd.isna(s):
        return None
    s = str(s).strip().lower()
    s = (
        s.replace("é", "e").replace("è", "e").replace("ë", "e")
         .replace("ó", "o").replace("ò", "o").replace("ö", "o")
         .replace("á", "a").replace("à", "a").replace("ä", "a")
         .replace("ü", "u").replace("ï", "i").replace("ř", "r")
         .replace("ž", "z").replace("š", "s").replace("č", "c")
         .replace("ý", "y").replace("í", "i").replace("ň", "n")
         .replace("ě", "e").replace("ď", "d").replace("ť", "t")
    )
    s = re.sub(r"\s+", " ", s)
    return s

def standardize_name(s):
    """Standardize name to 'firstname lastname' format for consistent grouping.
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
        # first_lower_idx = 2 for "VAN ALPHEN Aniek"
        first_name_parts = parts[first_lower_idx:]  # ["aniek"]
        last_name_parts = parts[:first_lower_idx]   # ["van", "alphen"]
        return f"{' '.join(first_name_parts)} {' '.join(last_name_parts)}"
    elif all(p.isupper() for p in orig_parts):
        # All uppercase: "LASTNAME FIRSTNAME" -> assume first word is last name
        return f"{parts[1]} {parts[0]}"

    # Default: already in firstname lastname format
    return normalized

# Parse Flamanville results (standard format)
def parse_flamanville_results(filepath):
    """Parse Flamanville CSV"""
    df = pd.read_csv(filepath)
    df['race_date'] = pd.Timestamp('2025-11-30')
    df['race_id'] = '20251130_uci-world-cup_flamanville_flamanville-fra'
    df['series_name'] = 'UCI-World-Cup'
    df['race_name'] = 'Flamanville'
    df['race_location'] = 'Flamanville-FRA'
    df['rider_name'] = df['Name']
    return df

print("\n--- Parsing Tabor Men Elite ---")
tabor_men_raw = pd.read_csv(
    RESULTS_DIR / "Results__UCI-World-Cup__Tabor__Men-Elite__2025-11-23__Tabor-CZECHIA.csv"
)
# Names have \n between first and last - convert to "First Last"
tabor_men_raw['rider_name'] = tabor_men_raw['Name'].str.replace('\n', ' ').str.title()
tabor_men = pd.DataFrame({
    'Category Name': 'Men Elite',
    'Place': pd.to_numeric(tabor_men_raw['Place'], errors='coerce'),
    'rider_name': tabor_men_raw['rider_name'],
    'NAT': tabor_men_raw['NAT'],
    'race_date': pd.Timestamp('2025-11-23'),
    'race_id': '20251123_uci-world-cup_tabor_tabor-cze',
    'series_name': 'UCI-World-Cup',
    'race_name': 'Tabor',
    'race_location': 'Tabor-CZE'
})
tabor_men = tabor_men.dropna(subset=['Place'])
print(f"Parsed {len(tabor_men)} riders")
print(tabor_men[['Place', 'rider_name']].head(10))

print("\n--- Parsing Tabor Women Elite ---")
tabor_women_raw = pd.read_csv(
    RESULTS_DIR / "Results__UCI-World-Cup__Tabor__Women-Elite__2025-11-23__Tabor-CZECHIA.csv"
)
tabor_women = pd.DataFrame({
    'Category Name': 'Women Elite',
    'Place': pd.to_numeric(tabor_women_raw['Place'], errors='coerce'),
    'rider_name': tabor_women_raw['Name'].str.title(),
    'NAT': tabor_women_raw['NAT'],
    'race_date': pd.Timestamp('2025-11-23'),
    'race_id': '20251123_uci-world-cup_tabor_tabor-cze',
    'series_name': 'UCI-World-Cup',
    'race_name': 'Tabor',
    'race_location': 'Tabor-CZE'
})
tabor_women = tabor_women.dropna(subset=['Place'])
print(f"Parsed {len(tabor_women)} riders")
print(tabor_women[['Place', 'rider_name']].head(10))

print("\n--- Parsing Flamanville Men Elite ---")
flam_men = parse_flamanville_results(
    RESULTS_DIR / "Results__UCI-World-Cup__Flamanville__Men-Elite__2025-11-30__Flamanville-FRANCE.csv"
)
print(f"Parsed {len(flam_men)} riders")

print("\n--- Parsing Flamanville Women Elite ---")
flam_women = parse_flamanville_results(
    RESULTS_DIR / "Results__UCI-World-Cup__Flamanville__Women-Elite__2025-11-30__Flamanville-FRANCE.csv"
)
print(f"Parsed {len(flam_women)} riders")

# Parse Sardinia results (Dec 7, 2025)
def parse_sardinia_results(filepath, category):
    """Parse Sardinia CSV - format: Position,Name,Nationality,YOB,Time"""
    df = pd.read_csv(filepath)
    return pd.DataFrame({
        'Category Name': category,
        'Place': pd.to_numeric(df['Position'], errors='coerce'),
        'rider_name': df['Name'],
        'NAT': df['Nationality'],
        'race_date': pd.Timestamp('2025-12-07'),
        'race_id': '20251207_uci-world-cup_sardinia_sardinia-ita',
        'series_name': 'UCI-World-Cup',
        'race_name': 'Sardinia',
        'race_location': 'Sardinia-ITA'
    })

print("\n--- Parsing Sardinia Men Elite ---")
sardinia_men_file = RESULTS_DIR / "Results__UCI-World-Cup__Sardinia__Men-Elite__2025-12-07__Sardinia-ITALY.csv"
if sardinia_men_file.exists():
    sardinia_men = parse_sardinia_results(sardinia_men_file, 'Men Elite')
    sardinia_men = sardinia_men.dropna(subset=['Place'])
    print(f"Parsed {len(sardinia_men)} riders")
    print(sardinia_men[['Place', 'rider_name']].head(10))
else:
    sardinia_men = pd.DataFrame()
    print("File not found, skipping")

print("\n--- Parsing Sardinia Women Elite ---")
sardinia_women_file = RESULTS_DIR / "Results__UCI-World-Cup__Sardinia__Women-Elite__2025-12-07__Sardinia-ITALY.csv"
if sardinia_women_file.exists():
    sardinia_women = parse_sardinia_results(sardinia_women_file, 'Women Elite')
    sardinia_women = sardinia_women.dropna(subset=['Place'])
    print(f"Parsed {len(sardinia_women)} riders")
    print(sardinia_women[['Place', 'rider_name']].head(10))
else:
    sardinia_women = pd.DataFrame()
    print("File not found, skipping")

# Combine new results
new_results = pd.concat([tabor_men, tabor_women, flam_men, flam_women, sardinia_men, sardinia_women], ignore_index=True)
print(f"\nTotal new results: {len(new_results)}")

# Add missing columns with defaults
for col in existing.columns:
    if col not in new_results.columns:
        new_results[col] = np.nan

# Keep only columns that exist in existing
new_results = new_results[[c for c in existing.columns if c in new_results.columns]]

# Concatenate
combined = pd.concat([existing, new_results], ignore_index=True)
print(f"Combined results: {len(combined)} rows")

# Standardize rider names to consistent format for grouping
combined["rider_name_norm"] = combined["rider_name"].apply(standardize_name)

# Sort by rider and date for time-based features
combined = combined.sort_values(["rider_name_norm", "race_date"])

print("\n" + "=" * 60)
print("RECOMPUTING FEATURES")
print("=" * 60)

# 1. UCI Points features
print("\n1. UCI Points features...")
combined["Carried Points"] = pd.to_numeric(combined["Carried Points"], errors="coerce")
combined["Scored Points"] = pd.to_numeric(combined["Scored Points"], errors="coerce")

max_points = combined["Carried Points"].max()
if pd.isna(max_points) or max_points == 0:
    max_points = 700  # fallback
combined["uci_points_normalized"] = combined["Carried Points"].fillna(0) / max_points

combined["points_tier"] = pd.cut(
    combined["Carried Points"].fillna(0),
    bins=[0, 50, 150, 1000],
    labels=["low", "mid", "high"]
).fillna("low")

# 2. Team tier
print("2. Team tier features...")
TOP_TEAMS = [
    "ALPECIN", "DECEUNINCK", "BALOISE", "TREK", "LIONS",
    "PAUWELS", "SAUZEN", "CRELAN", "CORENDON",
    "VISMA", "LEASE", "BIKE", "INTERMARCHE", "CIRCUS"
]

def categorize_team(team_name):
    if pd.isna(team_name):
        return "no_team"
    team_upper = str(team_name).upper()
    if any(top in team_upper for top in TOP_TEAMS):
        return "top_team"
    return "other_team"

combined["team_tier"] = combined["Team Name"].apply(categorize_team)

# 3. Category features
print("3. Category features...")
combined["is_elite"] = combined["Category Name"].str.contains("Elite", case=False, na=False).astype(int)
combined["is_women"] = combined["Category Name"].str.contains("Women", case=False, na=False).astype(int)

# 4. Form features
print("4. Form features (historical performance)...")
combined["races_so_far"] = combined.groupby("rider_name_norm").cumcount()

place_shifted = combined.groupby("rider_name_norm")["Place"].shift(1)

combined["avg_place_last3"] = (
    place_shifted.groupby(combined["rider_name_norm"])
    .rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
)

combined["best_place_last5"] = (
    place_shifted.groupby(combined["rider_name_norm"])
    .rolling(5, min_periods=1).min().reset_index(level=0, drop=True)
)

combined["last_place"] = place_shifted

combined["days_since_last_race"] = (
    combined.groupby("rider_name_norm")["race_date"].diff().dt.days
)

combined["last_carried_points"] = combined.groupby("rider_name_norm")["Carried Points"].shift(1)
combined["last_scored_points"] = combined.groupby("rider_name_norm")["Scored Points"].shift(1)

# 5. Win rate features
print("5. Win rate features...")
combined["top3_finish"] = (combined["Place"] <= 3).astype(int)
top3_shifted = combined.groupby("rider_name_norm")["top3_finish"].shift(1)
combined["top3_rate_career"] = (
    top3_shifted.groupby(combined["rider_name_norm"])
    .expanding().mean().reset_index(level=0, drop=True)
)

combined["top10_finish"] = (combined["Place"] <= 10).astype(int)
top10_shifted = combined.groupby("rider_name_norm")["top10_finish"].shift(1)
combined["top10_rate_career"] = (
    top10_shifted.groupby(combined["rider_name_norm"])
    .expanding().mean().reset_index(level=0, drop=True)
)

# 6. Series performance
print("6. Series-specific features...")
combined["series_appearances"] = combined.groupby(["rider_name_norm", "series_name"]).cumcount()

# 6b. New rider flag (rider's first race in our dataset = high uncertainty)
print("6b. New rider flag...")
combined["is_new_rider"] = (combined["races_so_far"] == 0).astype(int)
print(f"  New rider observations: {combined['is_new_rider'].sum()} ({100*combined['is_new_rider'].mean():.1f}%)")

# 7. Head-to-head features (per race, against field)
print("7. Head-to-head features (this takes a while)...")
from collections import defaultdict

# Build cumulative H2H records as we iterate through races chronologically
# h2h_records[rider1][rider2] = [wins, total] - rider1's record vs rider2
h2h_records = defaultdict(lambda: defaultdict(lambda: [0, 0]))

# Sort by date to process chronologically
combined = combined.sort_values("race_date")

# For each race, compute H2H score for each rider BEFORE updating records
h2h_scores = []
h2h_known = []

races = combined.groupby("race_id")
total_races = len(races)

for race_idx, (race_id, race_df) in enumerate(races):
    if race_idx % 10 == 0:
        print(f"  Processing race {race_idx+1}/{total_races}...")

    # Get riders in this race with valid places
    race_riders = race_df[race_df["Place"].notna()][["rider_name_norm", "Place", "Category Name"]].values

    # Calculate H2H score for each rider against THIS field (using historical data only)
    race_h2h_scores = {}
    race_h2h_known = {}

    for rider_name, place, category in race_riders:
        if pd.isna(rider_name):
            race_h2h_scores[rider_name] = 0.5
            race_h2h_known[rider_name] = 0
            continue

        # Get opponents in same category
        opponents = [(r, p, c) for r, p, c in race_riders if r != rider_name and c == category and not pd.isna(r)]

        if not opponents:
            race_h2h_scores[rider_name] = 0.5
            race_h2h_known[rider_name] = 0
            continue

        # Calculate win rate against known opponents (using HISTORICAL data only)
        win_rates = []
        for opp_name, _, _ in opponents:
            if opp_name in h2h_records[rider_name] and h2h_records[rider_name][opp_name][1] > 0:
                wins, total = h2h_records[rider_name][opp_name]
                win_rates.append(wins / total)

        if win_rates:
            race_h2h_scores[rider_name] = np.mean(win_rates)
            race_h2h_known[rider_name] = len(win_rates)
        else:
            race_h2h_scores[rider_name] = 0.5  # Neutral for unknown
            race_h2h_known[rider_name] = 0

    # Store scores for this race's rows
    for idx in race_df.index:
        rider = race_df.loc[idx, "rider_name_norm"]
        h2h_scores.append(race_h2h_scores.get(rider, 0.5))
        h2h_known.append(race_h2h_known.get(rider, 0))

    # NOW update H2H records with this race's results (for future races)
    for i in range(len(race_riders)):
        for j in range(i + 1, len(race_riders)):
            r1_name, r1_place, r1_cat = race_riders[i]
            r2_name, r2_place, r2_cat = race_riders[j]

            if pd.isna(r1_name) or pd.isna(r2_name) or r1_cat != r2_cat:
                continue

            # Update totals
            h2h_records[r1_name][r2_name][1] += 1
            h2h_records[r2_name][r1_name][1] += 1

            # Update wins
            if r1_place < r2_place:
                h2h_records[r1_name][r2_name][0] += 1
            elif r2_place < r1_place:
                h2h_records[r2_name][r1_name][0] += 1

# Add H2H columns to dataframe
combined["h2h_field_score"] = h2h_scores
combined["h2h_known_opponents"] = h2h_known

print(f"  H2H features computed for {len(combined)} rows")
print(f"  Avg H2H score: {combined['h2h_field_score'].mean():.3f}")
print(f"  Avg known opponents: {combined['h2h_known_opponents'].mean():.1f}")

# Save
output_path = CLEAN_DIR / "results_with_features.csv"
combined.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total rows: {len(combined)}")
print(f"Date range: {combined['race_date'].min()} to {combined['race_date'].max()}")
print(f"Unique races: {combined['race_id'].nunique()}")
print(f"\nSaved to: {output_path}")

# Verify Alvarado
print("\n--- Verifying Alvarado ---")
alvarado = combined[combined['rider_name_norm'].str.contains('alvarado', na=False)]
print(f"Found {len(alvarado)} records")
print(alvarado[['rider_name', 'race_date', 'Place', 'Category Name']].tail(10))
