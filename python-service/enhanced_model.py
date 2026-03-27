"""
Enhanced Football Prediction Model for VIT Platform
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from pathlib import Path

class VITPredictionEngine:
    """Enhanced prediction engine with EV calculations"""
    
    def __init__(self):
        self.league_stats = self._load_league_stats()
    
    def _load_league_stats(self) -> Dict:
        """Load league statistics"""
        stats_path = Path("../data/football/processed/league_statistics.csv")
        
        if stats_path.exists():
            df = pd.read_csv(stats_path)
            stats = {}
            for _, row in df.iterrows():
                stats[row['league']] = {
                    'avg_goals': row.get('avg_total_goals', 2.5),
                    'over_2_5_rate': row.get('over_2_5_rate', 0.48),
                    'btts_rate': row.get('btts_rate', 0.52)
                }
            return stats
        
        # Default stats for leagues
        default_leagues = ['EPL', 'La_Liga', 'Bundesliga', 'Serie_A', 
                          'Slovenia', 'Denmark', 'Iceland', 'Wales']
        stats = {}
        for league in default_leagues:
            stats[league] = {
                'avg_goals': 2.6,
                'over_2_5_rate': 0.52,
                'btts_rate': 0.55
            }
        return stats
    
    def predict_football_match(self, home_team: str, away_team: str,
                               league: str = None, odds_data: Dict = None) -> Dict:
        """Predict football match with EV"""
        
        # Get league stats
        league_info = self.league_stats.get(league, {
            'avg_goals': 2.5,
            'over_2_5_rate': 0.48
        })
        
        # Calculate expected goals
        home_xg = league_info['avg_goals'] * 0.55
        away_xg = league_info['avg_goals'] * 0.45
        
        # Simulate
        home_goals = np.random.poisson(home_xg, 10000)
        away_goals = np.random.poisson(away_xg, 10000)
        total_goals = home_goals + away_goals
        
        # Calculate probabilities
        over_2_5 = (total_goals > 2.5).mean()
        btts = ((home_goals > 0) & (away_goals > 0)).mean()
        home_win = (home_goals > away_goals).mean()
        draw = (home_goals == away_goals).mean()
        away_win = (home_goals < away_goals).mean()
        
        prediction = {
            'match': f"{home_team} vs {away_team}",
            'league': league,
            'expected_goals': {
                'home': round(home_xg, 2),
                'away': round(away_xg, 2),
                'total': round(home_xg + away_xg, 2)
            },
            'probabilities': {
                'home_win': round(home_win, 4),
                'draw': round(draw, 4),
                'away_win': round(away_win, 4),
                'over_2_5': round(over_2_5, 4),
                'btts': round(btts, 4)
            }
        }
        
        # Calculate EV if odds provided
        if odds_data:
            ev_results = {}
            for market, prob in prediction['probabilities'].items():
                if market in odds_data:
                    odds = odds_data[market]
                    ev = (prob * odds) - 1
                    ev_results[market] = {
                        'probability': prob,
                        'odds': odds,
                        'expected_value': round(ev, 4),
                        'is_value': ev > 0.05
                    }
            prediction['expected_value'] = ev_results
            prediction['value_bets'] = [
                {'market': m, 'expected_value': d['expected_value']}
                for m, d in ev_results.items() if d.get('is_value', False)
            ]
        
        return prediction
    
    def predict_with_league_stats(self, home_team: str, away_team: str,
                                  league: str = None, odds_data: Dict = None,
                                  simulations: int = 50000) -> Dict:
        """Alias for predict_football_match"""
        return self.predict_football_match(home_team, away_team, league, odds_data)
    
    def analyze_betting_ticket(self, matches: List[Dict]) -> Dict:
        """Analyze a betting ticket"""
        results = []
        for match in matches:
            odds_data = {'over_2_5': match.get('odds', 1.5)}
            pred = self.predict_football_match(
                match['home_team'],
                match['away_team'],
                match.get('league'),
                odds_data
            )
            results.append(pred)
        
        return {
            'total_bets': len(matches),
            'results': results,
            'value_bets_found': sum(1 for r in results if r.get('value_bets'))
        }


# Alias for backward compatibility
FootballPredictionModel = VITPredictionEngine


if __name__ == "__main__":
    print("Testing Enhanced Model...")
    engine = VITPredictionEngine()
    result = engine.predict_football_match("Arsenal", "Chelsea", "EPL")
    print(f"✅ Prediction: Over 2.5 = {result['probabilities']['over_2_5']:.1%}")
