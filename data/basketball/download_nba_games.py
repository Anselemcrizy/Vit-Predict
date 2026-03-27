import pandas as pd
import requests
import time
from pathlib import Path

class NBADataDownloader:
    def __init__(self):
        self.base_url = "https://www.basketball-reference.com/leagues/NBA_{}_games.html"
        self.data_dir = Path("raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_season(self, season_year: int):
        print(f"\n📥 Downloading NBA {season_year-1}-{season_year} season...")
        url = self.base_url.format(season_year)
        
        try:
            # Add headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"   Fetching URL: {url}")
            
            # Try to read directly with pandas (simpler)
            games_df = pd.read_html(url, header=0)[0]
            
            print(f"   Downloaded {len(games_df)} rows")
            
            # Clean up column names
            if len(games_df.columns) >= 5:
                games_df.columns = ['date', 'away_team', 'away_score', 'home_team', 'home_score'] + list(games_df.columns[5:])
            
            # Save to CSV
            output_file = self.data_dir / f"NBA_{season_year-1}_{season_year}.csv"
            games_df.to_csv(output_file, index=False)
            print(f"   ✓ Saved to {output_file}")
            
            # Show preview
            print(f"\n   Preview:")
            print(games_df.head(3))
            
            return games_df
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print(f"   Trying alternative method...")
            
            # Alternative method with requests
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                games_df = pd.read_html(response.text)[0]
                print(f"   ✓ Alternative method worked! Downloaded {len(games_df)} games")
                return games_df
            except Exception as e2:
                print(f"   ✗ Both methods failed: {e2}")
                return None

def quick_test():
    print("="*60)
    print("🏀 NBA DATA DOWNLOADER - QUICK TEST")
    print("="*60)
    
    downloader = NBADataDownloader()
    df = downloader.download_season(2024)
    
    if df is not None:
        print(f"\n✅ Success! Downloaded {len(df)} games")
        print(f"\n📊 Columns: {list(df.columns)}")
        print(f"\n📈 Basic Stats:")
        if 'home_score' in df.columns:
            print(f"   Average Home Score: {df['home_score'].mean():.1f}")
        if 'away_score' in df.columns:
            print(f"   Average Away Score: {df['away_score'].mean():.1f}")
    else:
        print("\n❌ Download failed. Check your internet connection.")
        print("   You can also manually download CSV from:")
        print("   https://www.basketball-reference.com/leagues/NBA_2024_games.html")
        print("   Click 'Share & Export' -> 'Get table as CSV'")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏀 NBA DATA DOWNLOADER FOR VIT PLATFORM")
    print("="*60)
    print("\nOptions:")
    print("1. Quick test - Download current season (2023-24)")
    print("2. Exit")
    
    choice = input("\nSelect option (1-2): ")
    
    if choice == "1":
        quick_test()
    else:
        print("Exiting...")
