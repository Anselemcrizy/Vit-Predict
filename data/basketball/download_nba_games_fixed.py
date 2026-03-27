import pandas as pd
import numpy as np
from pathlib import Path
import re

print("="*60)
print("🏀 NBA DATA DOWNLOADER - CORRECT PARSER")
print("="*60)

try:
    # Download the data
    url = "https://www.basketball-reference.com/leagues/NBA_2024_games.html"
    print(f"\n📥 Downloading from: {url}")
    
    tables = pd.read_html(url)
    df = tables[0]
    
    print(f"✓ Downloaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    
    # Initialize lists to store clean data
    games = []
    
    # Process each row using iloc for positional indexing
    for idx in range(len(df)):
        row = df.iloc[idx]
        
        # Skip header rows
        first_col = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        if 'Date' in first_col or 'Start' in first_col:
            continue
            
        try:
            # Get the visitor column (index 2) and home column (index 4)
            visitor_col = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
            home_col = str(row.iloc[4]) if pd.notna(row.iloc[4]) else ""
            
            # Skip if this is a playoff game or has no data
            if 'Box Score' in visitor_col or 'Box Score' in home_col:
                continue
                
            # Parse visitor team and score
            if visitor_col and len(visitor_col.split()) >= 2:
                # Split the last part which should be the score
                visitor_parts = visitor_col.rsplit(' ', 1)
                away_team = ' '.join(visitor_parts[:-1]) if len(visitor_parts) > 1 else visitor_parts[0]
                away_score = int(visitor_parts[-1]) if visitor_parts[-1].isdigit() else None
            else:
                continue
                
            # Parse home team and score
            if home_col and len(home_col.split()) >= 2:
                home_parts = home_col.rsplit(' ', 1)
                home_team = ' '.join(home_parts[:-1]) if len(home_parts) > 1 else home_parts[0]
                home_score = int(home_parts[-1]) if home_parts[-1].isdigit() else None
            else:
                continue
            
            # Skip if scores are missing
            if away_score is None or home_score is None:
                continue
                
            # Get date and other info
            date = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            attendance = row.iloc[8] if len(row) > 8 and pd.notna(row.iloc[8]) else None
            arena = row.iloc[10] if len(row) > 10 and pd.notna(row.iloc[10]) else None
            
            games.append({
                'date': date,
                'away_team': away_team.strip(),
                'away_score': away_score,
                'home_team': home_team.strip(),
                'home_score': home_score,
                'attendance': attendance,
                'arena': arena
            })
            
        except Exception as e:
            # Skip rows that can't be parsed
            continue
    
    # Create DataFrame
    if games:
        games_df = pd.DataFrame(games)
        print(f"✓ Successfully parsed {len(games_df)} games")
        
        # Create directories
        raw_dir = Path("raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw data
        output_file = raw_dir / "NBA_2023_2024.csv"
        games_df.to_csv(output_file, index=False)
        print(f"✓ Saved to {output_file}")
        
        # Create processed data with features
        processed_dir = Path("processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert scores to numeric
        games_df['home_score'] = pd.to_numeric(games_df['home_score'])
        games_df['away_score'] = pd.to_numeric(games_df['away_score'])
        
        # Add derived features
        games_df['total_points'] = games_df['home_score'] + games_df['away_score']
        games_df['point_diff'] = games_df['home_score'] - games_df['away_score']
        games_df['home_win'] = (games_df['home_score'] > games_df['away_score']).astype(int)
        
        # Try to parse date
        try:
            games_df['date_parsed'] = pd.to_datetime(games_df['date'], errors='coerce')
            games_df['month'] = games_df['date_parsed'].dt.month
            games_df['day_of_week'] = games_df['date_parsed'].dt.dayofweek
        except:
            pass
        
        # Save processed data
        processed_file = processed_dir / "NBA_2023_2024_processed.csv"
        games_df.to_csv(processed_file, index=False)
        print(f"✓ Saved processed data to {processed_file}")
        
        # Show statistics
        print("\n" + "="*60)
        print("📊 DATA STATISTICS")
        print("="*60)
        print(f"Total Games: {len(games_df)}")
        print(f"\nScoring Averages:")
        print(f"  Home Team: {games_df['home_score'].mean():.1f} points/game")
        print(f"  Away Team: {games_df['away_score'].mean():.1f} points/game")
        print(f"  Total: {games_df['total_points'].mean():.1f} points/game")
        print(f"\nHome Win Rate: {games_df['home_win'].mean():.1%}")
        
        # Show top teams
        print(f"\n🏀 Top 10 Teams by Games Played:")
        all_teams = pd.concat([games_df['home_team'], games_df['away_team']])
        team_counts = all_teams.value_counts().head(10)
        for team, count in team_counts.items():
            print(f"  {team}: {count} games")
        
        # Preview the data
        print("\n📋 Sample Games (First 10):")
        print("="*80)
        for idx, row in games_df.head(10).iterrows():
            print(f"{row['date']}: {row['away_team']} ({int(row['away_score'])}) @ {row['home_team']} ({int(row['home_score'])})")
        
        print("\n" + "="*60)
        print("✅ Download complete! Data ready for model training")
        print(f"📍 Files saved in: {raw_dir}/ and {processed_dir}/")
        
    else:
        print("❌ No games were parsed. The data structure might be different.")
        print("\nLet's inspect the first few rows to debug:")
        print(df.head(10))
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n📝 Manual download option:")
    print("1. Go to: https://www.basketball-reference.com/leagues/NBA_2024_games.html")
    print("2. Click 'Share & Export' → 'Get table as CSV'")
    print("3. Save to: data/basketball/raw/NBA_2023_2024.csv")

print("\n" + "="*60)
