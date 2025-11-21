"""
Quick script to rebuild clean data with all 45 races
Run this first to update the dataset
"""
import pandas as pd
from pathlib import Path
import re

DATA_DIR = Path("data")
RESULTS_DIR = DATA_DIR / "results"
CLEAN_DIR = DATA_DIR / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

def parse_race_meta_from_filename(path: Path):
    """Extract series, race name, date, location from filename"""
    stem = path.stem
    parts = [p.strip() for p in stem.split("__")]

    if len(parts) >= 3:
        series_name = parts[0]
        race_name = parts[1]
        date_str = parts[2] if len(parts) > 2 else None
        location = parts[3] if len(parts) > 3 else None
    else:
        series_name = None
        race_name = stem
        date_str = None
        location = None

    race_date = None
    if date_str:
        try:
            race_date = pd.to_datetime(date_str, format="%Y-%m-%d")
        except:
            pass

    return series_name, race_name, race_date, location

def slugify(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def make_race_id(series_name, race_name, race_date, location):
    date_part = race_date.strftime("%Y%m%d") if (race_date is not None and pd.notnull(race_date)) else "unknown"
    series_part = slugify(series_name) if series_name else "standalone"
    name_part = slugify(race_name)
    loc_part = slugify(location) if location else "noloc"
    return f"{date_part}_{series_part}_{name_part}_{loc_part}"

print("=" * 60)
print("REBUILDING CLEAN DATA WITH ALL RACES")
print("=" * 60)

all_results = []
csv_files = sorted(RESULTS_DIR.glob("*.csv"))

print(f"\nFound {len(csv_files)} race CSV files\n")

for csv_path in csv_files:
    print(f"Processing: {csv_path.name}")

    # Parse metadata from filename
    series_name, race_name, race_date, race_location = parse_race_meta_from_filename(csv_path)
    race_id = make_race_id(series_name, race_name, race_date, race_location)

    # Read CSV
    try:
        df = pd.read_csv(csv_path)

        # Drop empty columns
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

        # Add metadata
        df["series_name"] = series_name
        df["race_name"] = race_name
        df["race_date"] = race_date
        df["race_location"] = race_location
        df["race_id"] = race_id

        # Build rider name
        df["rider_name"] = (
            df["First Name"].fillna("").astype(str).str.strip()
            + " "
            + df["Last Name"].fillna("").astype(str).str.strip()
        ).str.strip()

        # Make Place numeric
        df["Place"] = pd.to_numeric(df["Place"], errors="coerce")

        all_results.append(df)
        print(f"  ✓ Added {len(df)} results")

    except Exception as e:
        print(f"  ✗ ERROR: {e}")

# Combine all
results_all = pd.concat(all_results, ignore_index=True)

print(f"\n" + "=" * 60)
print(f"TOTAL: {len(results_all)} rider-race observations")
print(f"Unique races: {results_all['race_id'].nunique()}")
print(f"Unique riders: {results_all['rider_name'].nunique()}")
print("=" * 60)

# Save
output_path = CLEAN_DIR / "results_all.csv"
results_all.to_csv(output_path, index=False)
print(f"\n✓ Saved to: {output_path}")

print(f"\nSample data:")
print(results_all[['race_date', 'series_name', 'race_name', 'rider_name', 'Place']].head(10))
