import pandas as pd
import numpy as np

print("Downloading NBA data...")

try:
    # Try to download
    url = "https://www.basketball-reference.com/leagues/NBA_2024_games.html"
    tables = pd.read_html(url)
    
    if tables:
        df = tables[0]
        print(f"Raw data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Try to identify the correct columns
        # Look for columns with "Pts" or "Score" in them
        score_cols = [col for col in df.columns if 'Pts' in str(col) or 'Score' in str(col)]
        print(f"\nPossible score columns: {score_cols}")
        
        # Save the raw data for inspection
        df.to_csv("raw_data_inspect.csv", index=False)
        print(f"\nRaw data saved to raw_data_inspect.csv for inspection")
        print("\nPlease check raw_data_inspect.csv to see the structure")
        
except Exception as e:
    print(f"Error: {e}")

print("\nDone!")
