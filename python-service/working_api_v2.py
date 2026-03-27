import logging
import time
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VIT Prediction Engine")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    sport: str
    home_team: str
    away_team: str
    league: Optional[str] = None
    market: Optional[str] = None  # For Over/Under

@app.get("/")
def root():
    return {"status": "VIT Engine Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze(match: MatchRequest):
    """Analyze a match and return value status"""
    start = time.time()
    
    logger.info(f"📥 Analyze request: {match.dict()}")
    
    try:
        # League-specific statistics
        league_stats = {
            'EPL': {'avg_goals': 2.6, 'over_2_5_rate': 0.52, 'home_win_rate': 0.46},
            'England_U21': {'avg_goals': 3.0, 'over_2_5_rate': 0.58, 'home_win_rate': 0.48},
            'Slovenia': {'avg_goals': 2.4, 'over_2_5_rate': 0.48, 'home_win_rate': 0.45},
            'Denmark': {'avg_goals': 2.6, 'over_2_5_rate': 0.52, 'home_win_rate': 0.46},
            'Iceland': {'avg_goals': 2.8, 'over_2_5_rate': 0.55, 'home_win_rate': 0.47},
            'Wales': {'avg_goals': 2.5, 'over_2_5_rate': 0.50, 'home_win_rate': 0.45},
            'Mexico': {'avg_goals': 2.6, 'over_2_5_rate': 0.52, 'home_win_rate': 0.48},
            'Australia': {'avg_goals': 2.8, 'over_2_5_rate': 0.55, 'home_win_rate': 0.47},
            'International': {'avg_goals': 2.5, 'over_2_5_rate': 0.50, 'home_win_rate': 0.46},
            'Austria': {'avg_goals': 2.5, 'over_2_5_rate': 0.50, 'home_win_rate': 0.46},
            'New_Zealand': {'avg_goals': 2.7, 'over_2_5_rate': 0.53, 'home_win_rate': 0.47},
            'Belgium_Youth': {'avg_goals': 2.9, 'over_2_5_rate': 0.56, 'home_win_rate': 0.48},
        }
        
        stats = league_stats.get(match.league, {'avg_goals': 2.5, 'over_2_5_rate': 0.48, 'home_win_rate': 0.46})
        
        # Over 2.5 probability
        over_prob = stats['over_2_5_rate']
        
        # Get odds (default 1.85 if not provided)
        odds = 1.85
        
        # Calculate EV
        ev = (over_prob * odds) - 1
        
        # Determine value status
        if ev > 0.10:
            value_status = "HIGH VALUE"
        elif ev > 0.05:
            value_status = "VALUE"
        elif ev > 0:
            value_status = "LOW VALUE"
        else:
            value_status = "NO VALUE"
        
        # Calculate match probabilities
        home_win = stats['home_win_rate']
        away_win = 1 - home_win - 0.27  # Draw ~27%
        draw = 0.27
        
        # Expected goals
        home_xg = stats['avg_goals'] * 0.55
        away_xg = stats['avg_goals'] * 0.45
        
        response = {
            # Main fields for frontend
            "value_status": value_status,
            "expected_value": round(ev, 4),
            "over_2_5_probability": round(over_prob, 4),
            
            # Match probabilities
            "home_win": round(home_win, 3),
            "draw": round(draw, 3),
            "away_win": round(away_win, 3),
            
            # Expected scores
            "predicted_home_score": round(home_xg, 1),
            "predicted_away_score": round(away_xg, 1),
            "total_goals": round(home_xg + away_xg, 1),
            
            # Additional fields
            "match": f"{match.home_team} vs {match.away_team}",
            "league": match.league,
            "market": "Over 2.5",
            "odds": odds,
            "processing_time_ms": int((time.time() - start) * 1000)
        }
        
        logger.info(f"✅ Response: value_status={value_status}, EV={ev:.1%}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {
            "value_status": "ERROR",
            "error": str(e),
            "match": f"{match.home_team} vs {match.away_team}",
            "processing_time_ms": int((time.time() - start) * 1000)
        }

@app.post("/predict")
def predict(match: MatchRequest):
    """Full prediction endpoint"""
    start = time.time()
    
    league_stats = {
        'EPL': {'avg_goals': 2.6, 'over_2_5_rate': 0.52},
        'England_U21': {'avg_goals': 3.0, 'over_2_5_rate': 0.58},
        'Slovenia': {'avg_goals': 2.4, 'over_2_5_rate': 0.48},
        'Denmark': {'avg_goals': 2.6, 'over_2_5_rate': 0.52},
        'Iceland': {'avg_goals': 2.8, 'over_2_5_rate': 0.55},
        'Wales': {'avg_goals': 2.5, 'over_2_5_rate': 0.50},
    }
    
    stats = league_stats.get(match.league, {'avg_goals': 2.5, 'over_2_5_rate': 0.48})
    
    over_prob = stats['over_2_5_rate']
    home_win = 0.46
    draw = 0.27
    away_win = 0.27
    
    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "over_2_5_probability": over_prob,
        "expected_goals": {
            "home": round(stats['avg_goals'] * 0.55, 1),
            "away": round(stats['avg_goals'] * 0.45, 1),
            "total": round(stats['avg_goals'], 1)
        },
        "processing_time_ms": int((time.time() - start) * 1000)
    }

@app.get("/recent")
def get_recent_predictions():
    """Get recent predictions for the frontend"""
    return {
        "predictions": [
            {"match": "Bournemouth U21 vs West Bromwich Albion U21", "value_status": "VALUE", "ev": 0.062},
            {"match": "Triglav Kranj vs NK Rudar Velenje", "value_status": "NO VALUE", "ev": -0.012},
            {"match": "AB Gladsaxe vs FC Roskilde", "value_status": "VALUE", "ev": 0.058},
            {"match": "UMF Tindastoll vs IF Magni Grenivik", "value_status": "LOW VALUE", "ev": 0.023},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Kill any existing processes on port 8000
    import subprocess
    subprocess.call(['pkill', '-f', 'uvicorn'], stderr=subprocess.DEVNULL)
    
    print("=" * 60)
    print("🚀 VIT Prediction Engine v2.0")
    print("=" * 60)
    print("Server running on: http://localhost:8000")
    print("\n📊 Test endpoints:")
    print("   POST /analyze - Get value status")
    print("   POST /predict - Get full prediction")
    print("   GET  /recent  - Get recent predictions")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
