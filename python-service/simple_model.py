"""
Simple Prediction Model for VIT Platform
"""

import numpy as np
from typing import Dict, Optional, List

class SimplePredictionEngine:
    """Simple prediction engine for testing"""
    
    def __init__(self):
        self.league_stats = {
            'EPL': {'avg_goals': 2.6, 'over_2_5_rate': 0.52},
            'England_U21': {'avg_goals': 3.0, 'over_2_5_rate': 0.58},
            'Slovenia': {'avg_goals': 2.4, 'over_2_5_rate': 0.48},
            'Denmark': {'avg_goals': 2.6, 'over_2_5_rate': 0.52},
            'Iceland': {'avg_goals': 2.8, 'over_2_5_rate': 0.55},
            'Wales': {'avg_goals': 2.5, 'over_2_5_rate': 0.50},
            'Mexico': {'avg_goals': 2.6, 'over_2_5_rate': 0.52},
            'Australia': {'avg_goals': 2.8, 'over_2_5_rate': 0.55},
            'International': {'avg_goals': 2.5, 'over_2_5_rate': 0.50}
        }
    
    def predict_football_match(self, home_team: str, away_team: str,
                               league: str = None, odds_data: Dict = None) -> Dict:
        """Predict football match"""
        
        # Get league stats
        stats = self.league_stats.get(league, {'avg_goals': 2.5, 'over_2_5_rate': 0.48})
        
        # Expected goals
        home_xg = stats['avg_goals'] * 0.55
        away_xg = stats['avg_goals'] * 0.45
        
        # Simulate
        home_goals = np.random.poisson(home_xg, 10000)
        away_goals = np.random.poisson(away_xg, 10000)
        
        # Calculate probabilities
        over_2_5 = ((home_goals + away_goals) > 2.5).mean()
        home_win = (home_goals > away_goals).mean()
        draw = (home_goals == away_goals).mean()
        away_win = (home_goals < away_goals).mean()
        
        result = {
            'probabilities': {
                'home_win': round(home_win, 4),
                'draw': round(draw, 4),
                'away_win': round(away_win, 4),
                'over_2_5': round(over_2_5, 4)
            },
            'expected_goals': {
                'home': round(home_xg, 2),
                'away': round(away_xg, 2),
                'total': round(home_xg + away_xg, 2)
            }
        }
        
        # Calculate EV if odds provided
        if odds_data and 'over_2_5' in odds_data:
            odds = odds_data['over_2_5']
            ev = (over_2_5 * odds) - 1
            result['expected_value'] = {
                'over_2_5': {
                    'expected_value': round(ev, 4),
                    'is_value': ev > 0.05
                }
            }
            result['value_bets'] = []
            if ev > 0.05:
                result['value_bets'].append({
                    'market': 'over_2_5',
                    'expected_value': round(ev, 4)
                })
        
        return result

# Alias for compatibility
VITPredictionEngine = SimplePredictionEngine
