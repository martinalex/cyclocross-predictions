"""
Prepare Flamanville race results to match expected format
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
RESULTS_DIR = DATA_DIR / "results"

print("=" * 70)
print("PREPARING FLAMANVILLE DATA FOR TRAINING DATASET")
print("=" * 70)

# Files to process
files_to_fix = [
    "Results__UCI-World-Cup__Flamanville__Men-Elite__2025-11-30__Flamanville-FRANCE.csv",
    "Results__UCI-World-Cup__Flamanville__Women-Elite__2025-11-30__Flamanville-FRANCE.csv"
]

for filename in files_to_fix:
    filepath = RESULTS_DIR / filename

    if not filepath.exists():
        print(f"\n⚠️  File not found: {filename}")
        continue

    print(f"\nProcessing: {filename}")

    # Read original
    df = pd.read_csv(filepath)
    print(f"  Original columns: {list(df.columns)}")

    # Determine category from filename
    if "Men-Elite" in filename:
        category = "Men Elite"
    elif "Women-Elite" in filename:
        category = "Women Elite"
    else:
        category = "Unknown"

    # Split Name into First Name and Last Name
    # Format: "LASTNAME Firstname" -> First Name: "Firstname", Last Name: "LASTNAME"
    def split_name(name):
        if pd.isna(name):
            return "", ""
        parts = str(name).strip().split()
        if len(parts) >= 2:
            # Assume first part is LASTNAME, rest is firstname
            last_name = parts[0]
            first_name = " ".join(parts[1:])
            return first_name, last_name
        return name, ""

    df[["First Name", "Last Name"]] = df["Name"].apply(
        lambda x: pd.Series(split_name(x))
    )

    # Rename Position -> Place
    if "Position" in df.columns:
        df["Place"] = df["Position"]
        df = df.drop(columns=["Position"])

    # Add missing columns with placeholders
    df["Category Name"] = category
    df["Team Name"] = ""  # Not available in Flamanville results
    df["RacerID"] = ""
    df["License"] = ""
    df["Carried Points"] = 0  # Not available - will need to fill from historical data
    df["Scored Points"] = 0   # Not available

    # Reorder columns to match expected format
    expected_cols = [
        "Category Name", "Place", "RacerID", "First Name", "Last Name",
        "Team Name", "Time", "License", "Carried Points", "Scored Points"
    ]

    # Add any extra columns
    for col in df.columns:
        if col not in expected_cols:
            expected_cols.append(col)

    # Keep only columns that exist
    final_cols = [col for col in expected_cols if col in df.columns]
    df = df[final_cols]

    # Save back
    df.to_csv(filepath, index=False)
    print(f"  ✓ Updated columns: {list(df.columns)}")
    print(f"  ✓ Rows: {len(df)}")
    print(f"  ✓ Category: {category}")
    print(f"  ✓ Sample names:")
    for _, row in df.head(3).iterrows():
        print(f"     - {row['First Name']} {row['Last Name']}")

print("\n" + "=" * 70)
print("✓ FLAMANVILLE DATA PREPARED")
print("=" * 70)
print("\nNext step: Run rebuild_data.py to incorporate into dataset")
