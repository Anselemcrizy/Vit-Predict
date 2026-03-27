#!/usr/bin/env python3
"""
Simple Ticket Analyzer for VIT Platform
"""

from enhanced_model import VITPredictionEngine

# Your 16 selections
TICKET_MATCHES = [
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

def main():
    print("=" * 80)
    print("🏆 VIT PLATFORM - 16-FOLD OVER 2.5 TICKET ANALYSIS")
    print("=" * 80)
    
    # Initialize engine
    engine = VITPredictionEngine()
    
    results = []
    value_count = 0
    
    for i, match in enumerate(TICKET_MATCHES, 1):
        print(f"\n{i}. {match['home_team']} vs {match['away_team']}")
        print("-" * 40)
        
        # Get prediction
        odds_data = {"over_2_5": match["odds"]}
        prediction = engine.predict_football_match(
            match["home_team"],
            match["away_team"],
            match["league"],
            odds_data
        )
        
        over_prob = prediction["probabilities"]["over_2_5"]
        odds = match["odds"]
        ev = (over_prob * odds) - 1
        is_value = ev > 0.05
        
        if is_value:
            value_count += 1
        
        print(f"  Over 2.5 Probability: {over_prob:.1%}")
        print(f"  Market Odds: {odds:.2f}")
        print(f"  Fair Odds: {1/over_prob:.2f}")
        print(f"  Expected Value: {ev:+.1%}")
        print(f"  Status: {'✅ VALUE BET' if is_value else '❌ AVOID'}")
        
        results.append({
            'match': f"{match['home_team']} vs {match['away_team']}",
            'probability': over_prob,
            'ev': ev,
            'is_value': is_value
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TICKET SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Selections: {len(results)}")
    print(f"Value Bets Found: {value_count}")
    print(f"Selections to Avoid: {len(results) - value_count}")
    
    # Show value bets
    value_bets = [r for r in results if r['is_value']]
    if value_bets:
        print("\n✅ VALUE BETS:")
        for bet in value_bets:
            print(f"  • {bet['match']}: EV = {bet['ev']:.1%}")
    
    # Show bets to avoid
    avoid_bets = [r for r in results if not r['is_value']]
    if avoid_bets:
        print("\n❌ SELECTIONS TO AVOID:")
        for bet in avoid_bets[:5]:
            print(f"  • {bet['match']}: EV = {bet['ev']:.1%}")
    
    # Parlay analysis
    parlay_prob = 1
    parlay_odds = 1
    for r in results:
        parlay_prob *= r['probability']
    for match in TICKET_MATCHES:
        parlay_odds *= match['odds']
    
    parlay_ev = (parlay_prob * parlay_odds) - 1
    
    print("\n🎲 PARLAY ANALYSIS:")
    print(f"  Parlay Odds: {parlay_odds:.2f}")
    print(f"  Parlay Probability: {parlay_prob:.6%}")
    print(f"  Parlay Expected Value: {parlay_ev:+.1%}")
    
    # Final recommendation
    print("\n💡 FINAL RECOMMENDATION:")
    if value_count >= 12:
        print("  ✅ STRONG TICKET - Most selections have positive EV")
        print("  ✓ Consider placing this accumulator")
    elif value_count >= 8:
        print("  ⚠️ MIXED TICKET - Consider removing negative EV selections")
        print(f"  ✓ Create a {value_count}-fold accumulator with only value bets")
    else:
        print("  ❌ WEAK TICKET - Most selections have negative EV")
        print("  ✗ Avoid this parlay")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
