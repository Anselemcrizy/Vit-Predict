import pandas as pd
from pathlib import Path

print("="*60)
print("🔍 NBA DATA VERIFICATION")
print("="*60)

# Check raw data
raw_dir = Path("raw")
if raw_dir.exists():
    raw_files = list(raw_dir.glob("*.csv"))
    if raw_files:
        print(f"\n📁 Raw data files found: {len(raw_files)}")
        for file in raw_files:
            df = pd.read_csv(file)
            print(f"\n  File: {file.name}")
            print(f"    Games: {len(df)}")
            print(f"    Columns: {list(df.columns)}")
            print(f"    Sample: {df.head(2)}")
    else:
        print("\n⚠️ No CSV files in raw directory yet")

# Check processed data
processed_dir = Path("processed")
if processed_dir.exists():
    processed_files = list(processed_dir.glob("*.csv"))
    if processed_files:
        print(f"\n📁 Processed data files found: {len(processed_files)}")
        for file in processed_files:
            df = pd.read_csv(file)
            print(f"\n  File: {file.name}")
            print(f"    Games: {len(df)}")
            print(f"    Columns: {list(df.columns)}")
            print(f"    Average home score: {df['home_score'].mean():.1f}")
            print(f"    Average away score: {df['away_score'].mean():.1f}")
            print(f"    Home win %: {df['home_win'].mean():.1%}")

print("\n" + "="*60)
