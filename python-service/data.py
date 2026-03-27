import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List

class FootballDataLoader:
    """Load and process football data"""
    
    def __init__(self, data_dir: str = "../data/football"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.football_data = None
        self.league_stats = None
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_football_data(self) -> pd.DataFrame:
        """Load football match data"""
        if self.football_data is not None:
            return self.football_data
        
        # Check for processed data
        processed_file = self.processed_dir / "football_processed.csv"
        if processed_file.exists():
            self.football_data = pd.read_csv(processed_file)
            print(f"✅ Loaded {len(self.football_data)} matches")
            return self.football_data
        
        # Check for raw files
        raw_files = list(self.raw_dir.glob("*.csv"))
        if raw_files:
            all_data = []
            for file in raw_files:
                df = pd.read_csv(file)
                all_data.append(df)
            self.football_data = pd.concat(all_data, ignore_index=True)
            print(f"✅ Loaded {len(self.football_data)} matches from {len(raw_files)} files")
            return self.football_data
        
        # Create sample data
        print("Creating sample data...")
        self._create_sample_data()
        return self.football_data
    
    def _create_sample_data(self):
        """Create sample data"""
        np.random.seed(42)
        matches = []
        
        leagues = ['EPL', 'La_Liga', 'Bundesliga', 'Serie_A']
        for league in leagues:
            for _ in range(200):
                home_goals = np.random.poisson(1.5)
                away_goals = np.random.poisson(1.2)
                matches.append({
                    'league': league,
                    'home_score': home_goals,
                    'away_score': away_goals,
                    'total_goals': home_goals + away_goals,
                    'over_2_5': 1 if (home_goals + away_goals) > 2.5 else 0,
                    'btts': 1 if (home_goals > 0 and away_goals > 0) else 0
                })
        
        self.football_data = pd.DataFrame(matches)
        self._create_league_stats()
    
    def _create_league_stats(self):
        """Create league statistics"""
        stats = []
        for league in self.football_data['league'].unique():
            league_df = self.football_data[self.football_data['league'] == league]
            stats.append({
                'league': league,
                'avg_total_goals': league_df['total_goals'].mean(),
                'over_2_5_rate': league_df['over_2_5'].mean(),
                'btts_rate': league_df['btts'].mean()
            })
        
        self.league_stats = pd.DataFrame(stats)
        self.league_stats.to_csv(self.processed_dir / "league_statistics.csv", index=False)
        self.football_data.to_csv(self.processed_dir / "football_processed.csv", index=False)

def get_data(home_team: str = "Arsenal", away_team: str = "Chelsea") -> dict:
    """Simple function for backward compatibility"""
    return {
        "home": home_team,
        "away": away_team,
        "home_xg": 1.6,
        "away_xg": 1.2
    }

if __name__ == "__main__":
    loader = FootballDataLoader()
    data = loader.load_football_data()
    print(f"✅ Data loaded: {len(data)} matches")
