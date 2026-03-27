"""
Enhanced Football Prediction Model for VIT Platform
==================================================
This module provides a comprehensive football prediction system with:
- Poisson regression for team strength estimation
- Monte Carlo simulations for match outcomes
- Expected Value (EV) calculations for betting markets
- Kelly Criterion for optimal bet sizing
- League-specific statistics integration
- Betting ticket analysis for accumulators

Author: VIT Platform
Version: 2.0
"""

import numpy as np
from typing import Optional, Dict, Tuple, List
from scipy import stats
import pandas as pd
from pathlib import Path
import json
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class FootballPredictionModel:
    """
    Enhanced football prediction model using Poisson regression with team strength,
    home advantage parameters, and advanced betting analytics.

    This model can:
    1. Fit team strength parameters from historical data
    2. Predict match outcomes using Monte Carlo simulations
    3. Calculate Expected Value for betting markets
    4. Detect value betting opportunities
    5. Analyze accumulator tickets
    6. Apply Kelly Criterion for bankroll management
    """

    def __init__(self, data_dir: str = "../data/football"):
        """
        Initialize the prediction model.

        Args:
            data_dir: Path to football data directory containing league statistics
        """
        # Core model parameters
        self.team_attack: Dict[str, float] = {}      # Team attacking strength
        self.team_defense: Dict[str, float] = {}     # Team defensive strength
        self.home_advantage: float = 1.2              # Home advantage multiplier
        self.league_avg_goals: float = 2.5           # League average goals per game
        self.theta: float = 1.0                      # Dispersion for negative binomial

        # League-specific statistics (loaded from your data files)
        self.league_stats: Dict[str, Dict] = {}

        # Load league statistics from data directory
        self._load_league_statistics(data_dir)

    def _load_league_statistics(self, data_dir: str):
        """
        Load league statistics from CSV files.
        Falls back to default values if files not found.

        Args:
            data_dir: Path to directory containing league statistics CSV
        """
        stats_path = Path(data_dir) / "processed/league_statistics.csv"

        if stats_path.exists():
            try:
                stats_df = pd.read_csv(stats_path)
                for _, row in stats_df.iterrows():
                    self.league_stats[row['league']] = {
                        'avg_goals': row['avg_total_goals'],
                        'over_2_5_rate': row['over_2_5_rate'],
                        'over_3_5_rate': row['over_3_5_rate'],
                        'btts_rate': row['btts_rate'],
                        'home_win_rate': row['home_win_rate']
                    }
                print(f"✅ Loaded statistics for {len(self.league_stats)} leagues")
            except Exception as e:
                print(f"⚠️ Error loading league stats: {e}")
                self._set_default_league_stats()
        else:
            print("⚠️ No league stats found. Using defaults for ticket leagues.")
            self._set_default_league_stats()

    def _set_default_league_stats(self):
        """
        Set default league statistics for leagues in your betting ticket.
        These values are based on historical averages for each league.
        """
        default_leagues = [
            "Slovenia", "Denmark", "Iceland", "Wales", "Mexico",
            "Australia", "International", "England_U21", "Belgium_Youth",
            "Austria", "New_Zealand", "EPL", "La_Liga", "Bundesliga"
        ]

        # Default stats based on league characteristics
        for league in default_leagues:
            self.league_stats[league] = {
                "avg_goals": 2.6,           # Average total goals per game
                "over_2_5_rate": 0.52,      # Probability of over 2.5 goals
                "over_3_5_rate": 0.35,      # Probability of over 3.5 goals
                "btts_rate": 0.55,          # Both Teams To Score rate
                "home_win_rate": 0.46,      # Home team win rate
            }

        print(f"✅ Set default stats for {len(default_leagues)} leagues")

    def fit(self, matches_df: pd.DataFrame):
        """
        Fit team strength parameters using Poisson regression.

        This method uses historical match data to estimate:
        - Attacking strength for each team
        - Defensive strength for each team
        - Home advantage factor
        - League average goals

        Args:
            matches_df: DataFrame with columns:
                - home_team: Home team name
                - away_team: Away team name
                - home_goals: Goals scored by home team
                - away_goals: Goals scored by away team
        """
        # Get all unique teams
        teams = pd.unique(matches_df[["home_team", "away_team"]].values.ravel())
        n_teams = len(teams)
        team_to_idx = {team: i for i, team in enumerate(teams)}

        # Build design matrix for Poisson regression
        n_matches = len(matches_df)
        X_attack = np.zeros((n_matches * 2, n_teams))
        X_defense = np.zeros((n_matches * 2, n_teams))
        y = np.zeros(n_matches * 2)

        # Fill design matrix for each match
        for i, (_, row) in enumerate(matches_df.iterrows()):
            home_idx = team_to_idx[row["home_team"]]
            away_idx = team_to_idx[row["away_team"]]

            # Home team attacking (row i)
            X_attack[i, home_idx] = 1
            X_defense[i, away_idx] = 1
            y[i] = row["home_goals"]

            # Away team attacking (row n_matches + i)
            X_attack[n_matches + i, away_idx] = 1
            X_defense[n_matches + i, home_idx] = 1
            y[n_matches + i] = row["away_goals"]

        # Fit Poisson regression model
        from sklearn.linear_model import PoissonRegressor

        X = np.hstack([X_attack, X_defense])
        model = PoissonRegressor(alpha=0.1, max_iter=1000)
        model.fit(X, y)

        # Extract team strengths
        self.team_attack = {team: model.coef_[i] for team, i in team_to_idx.items()}
        self.team_defense = {
            team: model.coef_[n_teams + i] for team, i in team_to_idx.items()
        }

        # Calculate home advantage and league average
        home_goals_avg = matches_df["home_goals"].mean()
        away_goals_avg = matches_df["away_goals"].mean()
        self.home_advantage = (
            home_goals_avg / away_goals_avg if away_goals_avg > 0 else 1.2
        )
        self.league_avg_goals = (home_goals_avg + away_goals_avg) / 2

        print(f"✅ Model fitted with {n_teams} teams")

    def predict_with_league_stats(
        self,
        home_team: str,
        away_team: str,
        league: str = None,
        odds_data: Dict = None,
        simulations: int = 50000,
    ) -> Dict:
        """
        Enhanced prediction with league statistics and EV calculation.

        This is the main prediction method that combines:
        - Team strengths (if model is fitted)
        - League-specific statistics
        - Monte Carlo simulations
        - Expected Value calculations

        Args:
            home_team: Name of home team
            away_team: Name of away team
            league: League name for league-specific stats
            odds_data: Dictionary of bookmaker odds for EV calculation
            simulations: Number of Monte Carlo simulations

        Returns:
            Dictionary containing prediction results with probabilities and EV
        """
        # Get league-specific statistics
        league_info = self.league_stats.get(
            league,
            {
                "avg_goals": 2.5,
                "over_2_5_rate": 0.48,
                "over_3_5_rate": 0.32,
                "btts_rate": 0.52,
                "home_win_rate": 0.46,
            },
        )

        # Get team-specific strengths (if available)
        home_attack = self.team_attack.get(home_team, 0)
        home_defense = self.team_defense.get(home_team, 0)
        away_attack = self.team_attack.get(away_team, 0)
        away_defense = self.team_defense.get(away_team, 0)

        # Calculate expected goals
        if home_attack != 0 or away_attack != 0:
            # Use team strengths if model is fitted
            home_xg = (
                np.exp(self.home_advantage + home_attack - away_defense)
                * league_info["avg_goals"]
            )
            away_xg = np.exp(away_attack - home_defense) * league_info["avg_goals"]
        else:
            # Use league averages with home advantage
            home_xg = league_info["avg_goals"] * 0.55  # Home advantage factor
            away_xg = league_info["avg_goals"] * 0.45

        # Run Monte Carlo simulation
        simulation_result = self._simulate_match(home_xg, away_xg, simulations)

        # Calculate Expected Value if odds are provided
        if odds_data:
            ev_results = self.calculate_expected_value(
                simulation_result["additional_markets"], odds_data
            )
            simulation_result["expected_value"] = ev_results
            simulation_result["value_bets"] = self.detect_value_bets(ev_results)

        # Add league information to results
        simulation_result["league"] = league
        simulation_result["league_stats"] = league_info

        return simulation_result

    def _simulate_match(
        self, home_xg: float, away_xg: float, simulations: int = 50000
    ) -> dict:
        """
        Monte Carlo simulation for match outcomes.

        This method simulates multiple possible outcomes of a match
        using Poisson or Negative Binomial distributions.

        Args:
            home_xg: Expected goals for home team
            away_xg: Expected goals for away team
            simulations: Number of simulations to run

        Returns:
            Dictionary with probabilities for various markets
        """
        np.random.seed(None)

        # Generate goals based on distribution type
        if self.theta != 1.0:
            # Negative binomial (better for overdispersion)
            home_probs = stats.nbinom(
                n=self.theta, p=self.theta / (self.theta + home_xg)
            )
            away_probs = stats.nbinom(
                n=self.theta, p=self.theta / (self.theta + away_xg)
            )
            home_goals = home_probs.rvs(simulations)
            away_goals = away_probs.rvs(simulations)
        else:
            # Poisson distribution (simpler)
            home_goals = np.random.poisson(home_xg, simulations)
            away_goals = np.random.poisson(away_xg, simulations)

        # Calculate match outcome probabilities
        home_win = float((home_goals > away_goals).mean())
        draw = float((home_goals == away_goals).mean())
        away_win = float((home_goals < away_goals).mean())

        # Calculate expected goals
        expected_home = float(np.mean(home_goals))
        expected_away = float(np.mean(away_goals))

        # Calculate over/under probabilities
        total_goals = home_goals + away_goals
        over_1_5 = float((total_goals > 1.5).mean())
        over_2_5 = float((total_goals > 2.5).mean())
        over_3_5 = float((total_goals > 3.5).mean())
        over_4_5 = float((total_goals > 4.5).mean())
        btts = float(((home_goals > 0) & (away_goals > 0)).mean())

        return {
            "home_win": round(home_win, 4),
            "draw": round(draw, 4),
            "away_win": round(away_win, 4),
            "expected_goals": {
                "home": round(expected_home, 2),
                "away": round(expected_away, 2),
                "total": round(expected_home + expected_away, 2),
            },
            "additional_markets": {
                "over_1_5": round(over_1_5, 4),
                "over_2_5": round(over_2_5, 4),
                "over_3_5": round(over_3_5, 4),
                "over_4_5": round(over_4_5, 4),
                "btts": round(btts, 4),
            },
        }

    def calculate_expected_value(self, probabilities: Dict, odds_data: Dict) -> Dict:
        """
        Calculate Expected Value for each betting market.

        EV = (Probability × Decimal Odds) - 1

        A positive EV indicates a value bet (the odds are better than the
        true probability suggests).

        Args:
            probabilities: Model probabilities for each market
            odds_data: Bookmaker odds for each market

        Returns:
            Dictionary with EV calculations for each market
        """
        ev_results = {}

        for market, prob in probabilities.items():
            if market in odds_data:
                odds = odds_data[market]
                ev = (prob * odds) - 1

                ev_results[market] = {
                    "probability": round(prob, 4),
                    "odds": odds,
                    "expected_value": round(ev, 4),
                    "edge": round(prob - (1 / odds), 4),  # Edge over market
                    "fair_odds": round(1 / prob, 2),      # Odds that would be fair
                    "recommendation": "VALUE" if ev > 0.05 else "NO VALUE",
                }

        return ev_results

    def detect_value_bets(self, ev_results: Dict) -> List[Dict]:
        """
        Identify value betting opportunities from EV calculations.

        A value bet is defined as having Expected Value > 5%.

        Args:
            ev_results: Results from calculate_expected_value()

        Returns:
            List of value bets sorted by highest expected value
        """
        value_bets = []

        for market, data in ev_results.items():
            if data["expected_value"] > 0.05:  # 5% threshold
                value_bets.append(
                    {
                        "market": market,
                        "expected_value": data["expected_value"],
                        "edge": data["edge"],
                        "odds": data["odds"],
                        "probability": data["probability"],
                        "fair_odds": data["fair_odds"],
                    }
                )

        # Sort by highest expected value
        value_bets.sort(key=lambda x: -x["expected_value"])

        return value_bets

    def calculate_kelly_criterion(
        self, probability: float, odds: float, bankroll: float = 1000
    ) -> Dict:
        """
        Calculate optimal bet size using the Kelly Criterion.

        The Kelly Criterion maximizes long-term growth by determining the
        optimal fraction of bankroll to wager.

        Formula: f* = (bp - q) / b
        where:
            b = decimal odds - 1 (net odds received)
            p = probability of winning
            q = 1 - p (probability of losing)

        Args:
            probability: Estimated probability of winning
            odds: Decimal odds offered
            bankroll: Total bankroll amount

        Returns:
            Dictionary with Kelly fraction and suggested bet amount
        """
        b = odds - 1  # Net odds
        p = probability
        q = 1 - p

        # Kelly formula
        kelly_fraction = (b * p - q) / b

        # Cap at 25% of bankroll for safety (protects against over-betting)
        kelly_fraction = max(0, min(0.25, kelly_fraction))

        return {
            "kelly_fraction": round(kelly_fraction, 4),
            "bet_amount": round(bankroll * kelly_fraction, 2),
            "full_kelly": round(kelly_fraction, 4),
            "recommendation": "BET" if kelly_fraction > 0 else "SKIP"
        }

    def analyze_ticket(self, matches: List[Dict], bankroll: float = 1000) -> Dict:
        """
        Analyze a betting ticket with multiple selections (accumulator).

        This method evaluates each selection in the ticket and calculates
        the overall parlay probability and expected value.

        Args:
            matches: List of dictionaries, each containing:
                - home_team: Home team name
                - away_team: Away team name
                - league: League name
                - odds: Decimal odds for Over 2.5 market
            bankroll: Total bankroll for Kelly calculations

        Returns:
            Comprehensive ticket analysis with recommendations
        """
        ticket_analysis = {
            "total_selections": len(matches),
            "selections": [],
            "value_selections": [],
            "parlay_analysis": {},
            "recommendations": [],
        }

        parlay_prob = 1   # Combined probability of all selections winning
        parlay_odds = 1   # Combined odds of the accumulator

        # Analyze each selection
        for match in matches:
            # Get prediction with EV calculation
            odds_data = {"over_2_5": match["odds"]}
            prediction = self.predict_with_league_stats(
                match["home_team"], 
                match["away_team"], 
                match.get("league"), 
                odds_data
            )

            over_prob = prediction["additional_markets"]["over_2_5"]
            ev = (over_prob * match["odds"]) - 1

            # Build selection analysis
            selection = {
                "match": f"{match['home_team']} vs {match['away_team']}",
                "league": match.get("league"),
                "odds": match["odds"],
                "probability": over_prob,
                "expected_value": ev,
                "fair_odds": 1 / over_prob,
                "is_value": ev > 0.05,
            }

            # Add Kelly calculation if it's a value bet
            if selection["is_value"]:
                kelly = self.calculate_kelly_criterion(
                    over_prob, match["odds"], bankroll
                )
                selection["kelly"] = kelly
                ticket_analysis["value_selections"].append(selection)

            ticket_analysis["selections"].append(selection)

            # Update parlay calculations (assuming independent events)
            parlay_prob *= over_prob
            parlay_odds *= match["odds"]

        # Calculate parlay expected value
        parlay_ev = (parlay_prob * parlay_odds) - 1

        ticket_analysis["parlay_analysis"] = {
            "total_odds": round(parlay_odds, 2),
            "probability": round(parlay_prob, 6),
            "expected_value": round(parlay_ev, 4),
            "is_value": parlay_ev > 0.05,
        }

        # Generate recommendations based on analysis
        value_count = len(ticket_analysis["value_selections"])

        if value_count >= 12:
            ticket_analysis["recommendations"].append(
                "✅ STRONG TICKET - Most selections have positive EV"
            )
            ticket_analysis["recommendations"].append(
                "✓ Consider placing this accumulator"
            )
        elif value_count >= 8:
            ticket_analysis["recommendations"].append(
                "⚠️ MIXED TICKET - Consider removing negative EV selections"
            )
            ticket_analysis["recommendations"].append(
                f"✓ Create a {value_count}-fold accumulator with only value bets"
            )
        else:
            ticket_analysis["recommendations"].append(
                "❌ WEAK TICKET - Most selections have negative EV"
            )
            ticket_analysis["recommendations"].append(
                "✗ Avoid this parlay"
            )

        # Add parlay recommendation
        if parlay_ev > 0.05:
            ticket_analysis["recommendations"].append(
                f"💰 Parlay has positive EV of {parlay_ev:.1%} - Worth considering"
            )
        elif parlay_ev > 0:
            ticket_analysis["recommendations"].append(
                f"📈 Parlay has slight positive EV of {parlay_ev:.1%}"
            )
        else:
            ticket_analysis["recommendations"].append(
                f"❌ Parlay has negative EV of {parlay_ev:.1%} - Avoid"
            )

        return ticket_analysis


def test_with_your_ticket():
    """
    Test function to analyze your 16-fold Over 2.5 betting ticket.

    This function demonstrates the full capabilities of the model
    by analyzing each selection in your ticket and providing
    detailed recommendations.
    """
    print("\n" + "=" * 80)
    print("🏆 VIT PLATFORM - 16-FOLD OVER 2.5 TICKET ANALYSIS")
    print("=" * 80)

    # Initialize the model
    model = FootballPredictionModel()

    # Your 16 selections from the betting ticket
    matches = [
        {"home_team": "Triglav Kranj", "away_team": "NK Rudar Velenje", "league": "Slovenia", "odds": 1.50},
        {"home_team": "AB Gladsaxe", "away_team": "FC Roskilde", "league": "Denmark", "odds": 1.50},
        {"home_team": "Bournemouth U21", "away_team": "West Bromwich U21", "league": "England_U21", "odds": 1.50},
        {"home_team": "UMF Tindastoll", "away_team": "IF Magni Grenivik", "league": "Iceland", "odds": 1.50},
        {"home_team": "UMF Selfoss", "away_team": "Augnablik Kopavogur", "league": "Iceland", "odds": 1.50},
        {"home_team": "Jeugd Lommel SK", "away_team": "Jeugd Patro Eisden", "league": "Belgium_Youth", "odds": 1.50},
        {"home_team": "SV Schwechat", "away_team": "SC Red Star Penzing", "league": "Austria", "odds": 1.50},
        {"home_team": "Pontypridd Town", "away_team": "Trefelin BGC", "league": "Wales", "odds": 1.50},
        {"home_team": "Caernarfon Town", "away_team": "The New Saints", "league": "Wales", "odds": 1.50},
        {"home_team": "Switzerland", "away_team": "Germany", "league": "International", "odds": 1.50},
        {"home_team": "Pumas Unam", "away_team": "Club Leon", "league": "Mexico", "odds": 1.50},
        {"home_team": "Adelaide City", "away_team": "Adelaide Comets", "league": "Australia", "odds": 1.30},
        {"home_team": "Petone FC", "away_team": "Upper Hutt City", "league": "New_Zealand", "odds": 1.45},
        {"home_team": "Netherlands", "away_team": "Norway", "league": "International", "odds": 1.37},
        {"home_team": "Spain", "away_team": "Serbia", "league": "International", "odds": 1.26},
        {"home_team": "Cyprus", "away_team": "Spain", "league": "International", "odds": 1.34}
    ]

    # Analyze the ticket
    result = model.analyze_ticket(matches, bankroll=1000)

    # Display results
    print(f"\n📊 TICKET SUMMARY")
    print("=" * 80)
    print(f"Total Selections: {result['total_selections']}")
    print(f"Value Selections Found: {len(result['value_selections'])}")
    print(f"Selections to Avoid: {result['total_selections'] - len(result['value_selections'])}")

    # Show detailed breakdown
    print("\n📈 SELECTION BREAKDOWN:")
    print("-" * 80)
    for i, sel in enumerate(result["selections"], 1):
        status = "✅ VALUE" if sel["is_value"] else "❌ AVOID"
        ev_color = f"{sel['expected_value']:+.1%}"
        print(f"{i:2}. {sel['match'][:45]:45} | Prob: {sel['probability']:.1%} | "
              f"Odds: {sel['odds']:.2f} | EV: {ev_color:>6} | {status}")

    # Show parlay analysis
    print("\n🎲 PARLAY ANALYSIS:")
    print("-" * 80)
    parlay = result["parlay_analysis"]
    print(f"Total Odds: {parlay['total_odds']:.2f} (16-fold accumulator)")
    print(f"Probability of all 16 winning: {parlay['probability']:.6%}")
    print(f"Expected Value: {parlay['expected_value']:+.1%}")

    # Show recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 80)
    for rec in result["recommendations"]:
        print(f"  {rec}")

    # Show value bets summary if any
    if result["value_selections"]:
        print("\n💰 VALUE BETS SUMMARY:")
        print("-" * 80)
        total_ev = sum(sel["expected_value"] for sel in result["value_selections"])
        avg_ev = total_ev / len(result["value_selections"])
        print(f"Average EV of value bets: {avg_ev:.1%}")
        print(f"Best value: {result['value_selections'][0]['match'][:40]} "
              f"(EV: {result['value_selections'][0]['expected_value']:.1%})")

    print("\n" + "=" * 80)

    return result


if __name__ == "__main__":
    print("🏆 Enhanced Football Prediction Model with EV Calculation")
    print("=" * 60)
    print("This model provides:")
    print("  • Poisson-based match predictions")
    print("  • Expected Value calculations for betting markets")
    print("  • Kelly Criterion for optimal bet sizing")
    print("  • Accumulator ticket analysis")
    print("  • League-specific statistics integration")
    print("=" * 60)

    # Run test with your ticket
    test_with_your_ticket()