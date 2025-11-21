"""
Feature engineering with UCI points, team tier, and form metrics
This fixes the high-bias model by adding features that vary per rider
"""
import pandas as pd
import numpy as np
from pathlib import Path
import re

DATA_DIR = Path("data")
CLEAN_DIR = DATA_DIR / "clean"

print("=" * 60)
print("FEATURE ENGINEERING - FIXING HIGH BIAS MODEL")
print("=" * 60)

# Load results
results_path = CLEAN_DIR / "results_all.csv"
print(f"\nLoading: {results_path}")
results = pd.read_csv(results_path, parse_dates=["race_date"])

print(f"Total observations: {len(results)}")
print(f"Unique riders: {results['rider_name'].nunique()}")

# Normalize rider names for consistent tracking
def normalize_name(s):
    if pd.isna(s):
        return None
    s = str(s).strip().lower()
    s = (
        s.replace("é", "e").replace("è", "e").replace("ë", "e")
         .replace("ó", "o").replace("ò", "o").replace("ö", "o")
         .replace("á", "a").replace("à", "a").replace("ä", "a")
         .replace("ü", "u").replace("ï", "i")
    )
    s = re.sub(r"\s+", " ", s)
    return s

results["rider_name_norm"] = results["rider_name"].apply(normalize_name)

# Sort by rider and date for time-based features
results = results.sort_values(["rider_name_norm", "race_date"])

print("\n" + "=" * 60)
print("ADDING NEW FEATURES")
print("=" * 60)

# 1. UCI POINTS FEATURES (high signal!)
print("\n1. UCI Points features...")
results["Carried Points"] = pd.to_numeric(results["Carried Points"], errors="coerce")
results["Scored Points"] = pd.to_numeric(results["Scored Points"], errors="coerce")

# Normalize UCI points (0-1 scale)
max_points = results["Carried Points"].max()
results["uci_points_normalized"] = results["Carried Points"].fillna(0) / max_points

# Points bin (high/mid/low tier)
results["points_tier"] = pd.cut(
    results["Carried Points"].fillna(0),
    bins=[0, 50, 150, 1000],
    labels=["low", "mid", "high"]
).fillna("low")

print(f"  ✓ UCI points range: {results['Carried Points'].min():.0f} - {results['Carried Points'].max():.0f}")
print(f"  ✓ Points tiers: {results['points_tier'].value_counts().to_dict()}")

# 2. TEAM TIER FEATURES
print("\n2. Team tier features...")

# Top teams in cyclocross
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

results["team_tier"] = results["Team Name"].apply(categorize_team)
print(f"  ✓ Team tiers: {results['team_tier'].value_counts().to_dict()}")

# 3. CATEGORY FEATURES
print("\n3. Category features...")
results["is_elite"] = results["Category Name"].str.contains("Elite", case=False, na=False).astype(int)
results["is_women"] = results["Category Name"].str.contains("Women", case=False, na=False).astype(int)
print(f"  ✓ Elite races: {results['is_elite'].sum()}")
print(f"  ✓ Women's races: {results['is_women'].sum()}")

# 4. FORM FEATURES (time-based)
print("\n4. Form features (historical performance)...")

# Races completed so far
results["races_so_far"] = results.groupby("rider_name_norm").cumcount()

# Shift place for historical features (avoid lookahead bias)
place_shifted = results.groupby("rider_name_norm")["Place"].shift(1)

# Last 3 races average
results["avg_place_last3"] = (
    place_shifted.groupby(results["rider_name_norm"])
    .rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
)

# Best place in last 5 races
results["best_place_last5"] = (
    place_shifted.groupby(results["rider_name_norm"])
    .rolling(5, min_periods=1).min().reset_index(level=0, drop=True)
)

# Last race place
results["last_place"] = place_shifted

# Days since last race
results["days_since_last_race"] = (
    results.groupby("rider_name_norm")["race_date"].diff().dt.days
)

# Last points (carried and scored)
results["last_carried_points"] = results.groupby("rider_name_norm")["Carried Points"].shift(1)
results["last_scored_points"] = results.groupby("rider_name_norm")["Scored Points"].shift(1)

print(f"  ✓ Average races per rider: {results['races_so_far'].mean():.1f}")
print(f"  ✓ Riders with history: {(results['races_so_far'] > 0).sum()} / {len(results)}")

# 5. WIN RATE FEATURES
print("\n5. Win rate features...")

# Top-3 finishes (podium)
results["top3_finish"] = (results["Place"] <= 3).astype(int)
top3_shifted = results.groupby("rider_name_norm")["top3_finish"].shift(1)
results["top3_rate_career"] = (
    top3_shifted.groupby(results["rider_name_norm"])
    .expanding().mean().reset_index(level=0, drop=True)
)

# Top-10 finishes (points scoring)
results["top10_finish"] = (results["Place"] <= 10).astype(int)
top10_shifted = results.groupby("rider_name_norm")["top10_finish"].shift(1)
results["top10_rate_career"] = (
    top10_shifted.groupby(results["rider_name_norm"])
    .expanding().mean().reset_index(level=0, drop=True)
)

print(f"  ✓ Top-3 finishes: {results['top3_finish'].sum()}")
print(f"  ✓ Top-10 finishes: {results['top10_finish'].sum()}")

# 6. SERIES PERFORMANCE
print("\n6. Series-specific features...")
results["series_appearances"] = results.groupby(["rider_name_norm", "series_name"]).cumcount()

print("\n" + "=" * 60)
print("FEATURE SUMMARY")
print("=" * 60)

new_features = [
    "uci_points_normalized",
    "points_tier",
    "team_tier",
    "is_elite",
    "is_women",
    "races_so_far",
    "avg_place_last3",
    "best_place_last5",
    "last_place",
    "days_since_last_race",
    "last_carried_points",
    "last_scored_points",
    "top3_rate_career",
    "top10_rate_career",
    "series_appearances"
]

print(f"\nNew features added: {len(new_features)}")
for feat in new_features:
    print(f"  - {feat}")

# Check feature variance (should NOT be near zero)
print("\n" + "=" * 60)
print("FEATURE VARIANCE CHECK (fixing high bias)")
print("=" * 60)

numeric_features = [
    "uci_points_normalized",
    "races_so_far",
    "avg_place_last3",
    "best_place_last5",
    "last_place",
    "days_since_last_race"
]

print("\nVariance in features (should be > 0):")
for feat in numeric_features:
    var = results[feat].var()
    status = "✓ GOOD" if var > 0.01 else "✗ BAD (too low)"
    print(f"  {feat:30s}: {var:10.4f}  {status}")

# Save enriched results
output_path = CLEAN_DIR / "results_with_features.csv"
results.to_csv(output_path, index=False)

print(f"\n✓ Saved to: {output_path}")
print(f"\nTotal columns: {len(results.columns)}")
print(f"Total rows: {len(results)}")

# Show sample
print("\nSample enriched data:")
sample_cols = ["rider_name", "Place", "uci_points_normalized", "team_tier", "races_so_far", "avg_place_last3"]
print(results[sample_cols].head(10).to_string())
