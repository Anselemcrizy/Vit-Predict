import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import numpy as np

# Import models
from enhanced_model import VITPredictionEngine

app = FastAPI(title="VIT Prediction Engine")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize prediction engine
prediction_engine = VITPredictionEngine()

class PredictRequest(BaseModel):
    sport: str
    home_team: str
    away_team: str
    league: Optional[str] = None
    odds: Optional[Dict[str, float]] = None

class PredictResponse(BaseModel):
    home_win: float
    draw: Optional[float] = None
    away_win: float
    predicted_home_score: Optional[float] = None
    predicted_away_score: Optional[float] = None
    expected_goals: Optional[Dict[str, float]] = None
    over_2_5_prob: Optional[float] = None
    btts_prob: Optional[float] = None
    expected_value: Optional[Dict[str, Any]] = None
    value_bets: Optional[list] = None
    model_meta: Dict[str, Any]
    processing_time_ms: int

@app.get("/")
def home():
    return {"status": "VIT Engine Running", "version": "2.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "models": ["football", "basketball"]}

@app.post("/predict", response_model=PredictResponse)
async def run_prediction(body: PredictRequest):
    """
    Predict match outcome with EV calculation
    """
    start = time.time()
    
    try:
        if body.sport.lower() == "football":
            # Get prediction from enhanced model
            odds_data = body.odds if body.odds else {"over_2_5": 1.85}
            
            result = prediction_engine.predict_football_match(
                home_team=body.home_team,
                away_team=body.away_team,
                league=body.league,
                odds_data=odds_data
            )
            
            processing_ms = int((time.time() - start) * 1000)
            
            # Extract probabilities
            probs = result.get("probabilities", {})
            expected_goals = result.get("expected_goals", {})
            expected_value = result.get("expected_value", {})
            value_bets = result.get("value_bets", [])
            
            return PredictResponse(
                home_win=probs.get("home_win", 0.5),
                draw=probs.get("draw", 0.25),
                away_win=probs.get("away_win", 0.25),
                predicted_home_score=expected_goals.get("home"),
                predicted_away_score=expected_goals.get("away"),
                expected_goals=expected_goals,
                over_2_5_prob=probs.get("over_2_5"),
                btts_prob=probs.get("btts"),
                expected_value=expected_value if expected_value else None,
                value_bets=value_bets if value_bets else None,
                model_meta={
                    "model": "Enhanced Poisson with League Stats",
                    "league": body.league,
                    "simulations": 50000
                },
                processing_time_ms=processing_ms
            )
        
        elif body.sport.lower() == "basketball":
            # Basketball prediction (placeholder)
            processing_ms = int((time.time() - start) * 1000)
            
            return PredictResponse(
                home_win=0.55,
                draw=None,
                away_win=0.45,
                predicted_home_score=108.5,
                predicted_away_score=104.2,
                expected_goals={"home": 108.5, "away": 104.2, "total": 212.7},
                over_2_5_prob=None,
                btts_prob=None,
                expected_value=None,
                value_bets=None,
                model_meta={"model": "Basketball Model", "note": "Coming soon"},
                processing_time_ms=processing_ms
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported sport: {body.sport}")
            
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_match(body: PredictRequest):
    """
    Simple analysis endpoint that returns value bet status
    """
    start = time.time()
    
    try:
        if body.sport.lower() == "football":
            odds_data = {"over_2_5": 1.85}
            result = prediction_engine.predict_football_match(
                home_team=body.home_team,
                away_team=body.away_team,
                league=body.league,
                odds_data=odds_data
            )
            
            # Determine value level
            value_bets = result.get("value_bets", [])
            if value_bets:
                best_ev = max(b.get("expected_value", 0) for b in value_bets)
                if best_ev > 0.1:
                    value_level = "HIGH VALUE"
                elif best_ev > 0.05:
                    value_level = "VALUE"
                else:
                    value_level = "LOW VALUE"
            else:
                value_level = "NO VALUE"
            
            return {
                "match": f"{body.home_team} vs {body.away_team}",
                "value_status": value_level,
                "home_win": result["probabilities"]["home_win"],
                "away_win": result["probabilities"]["away_win"],
                "over_2_5": result["probabilities"]["over_2_5"],
                "expected_value": value_bets[0]["expected_value"] if value_bets else 0,
                "processing_time_ms": int((time.time() - start) * 1000)
            }
        
        else:
            return {
                "match": f"{body.home_team} vs {body.away_team}",
                "value_status": "NO VALUE",
                "message": "Analysis only available for football"
            }
            
    except Exception as e:
        return {
            "match": f"{body.home_team} vs {body.away_team}",
            "value_status": "ERROR",
            "error": str(e)
        }

@app.get("/leagues")
async def get_leagues():
    """Get available leagues"""
    return {
        "leagues": list(prediction_engine.league_stats.keys()),
        "count": len(prediction_engine.league_stats)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
