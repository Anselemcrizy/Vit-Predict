import pandas as pd
import numpy as np
from pathlib import Path

print("="*60)
print("🎯 OVER/UNDER PREDICTION MODEL")
print("="*60)

# Load data
data_file = Path("data/football/processed/football_processed.csv")
df = pd.read_csv(data_file)

# Create simple prediction model
def predict_over_under(home_team, away_team, threshold=2.5):
    """Predict probability of over threshold goals"""
    
    # Get team stats
    home_games = df[(df['home_team'] == home_team) | (df['away_team'] == home_team)]
    away_games = df[(df['home_team'] == away_team) | (df['away_team'] == away_team)]
    
    # Get league average
    league = df[(df['home_team'] == home_team)]['league'].iloc[0] if len(df[df['home_team'] == home_team]) > 0 else 'EPL'
    league_games = df[df['league'] == league]
    
    # Calculate probabilities
    home_over_rate = home_games[f'over_{int(threshold*10)/10}'.replace('.', '_')].mean() if len(home_games) > 0 else 0.5
    away_over_rate = away_games[f'over_{int(threshold*10)/10}'.replace('.', '_')].mean() if len(away_games) > 0 else 0.5
    league_over_rate = league_games[f'over_{int(threshold*10)/10}'.replace('.', '_')].mean()
    
    # Weighted prediction
    prediction = (home_over_rate * 0.4 + away_over_rate * 0.4 + league_over_rate * 0.2)
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'threshold': threshold,
        'probability': prediction,
        'fair_odds': 1/prediction,
        'home_form': home_over_rate,
        'away_form': away_over_rate,
        'league_avg': league_over_rate
    }

# Test with teams from your ticket
print("\n📊 Testing predictions for your ticket matches:\n")

test_matches = [
    ('Triglav Kranj', 'NK Rudar Velenje'),
    ('AB Gladsaxe', 'FC Roskilde'),
    ('Bournemouth U21', 'West Bromwich U21'),
    ('UMF Tindastoll', 'IF Magni Grenivik'),
    ('Pumas Unam', 'Club Leon'),
    ('Petone FC', 'Upper Hutt City')
]

for home, away in test_matches:
    result = predict_over_under(home, away, 2.5)
    print(f"{home} vs {away}:")
    print(f"  Over 2.5 Probability: {result['probability']:.1%}")
    print(f"  Fair Odds: {result['fair_odds']:.2f}")
    print(f"  Home Form: {result['home_form']:.1%} | Away Form: {result['away_form']:.1%}")
    print()

print("="*60)
