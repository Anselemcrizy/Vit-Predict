import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import simple model for testing
from simple_model import SimplePredictionEngine

app = FastAPI(title="VIT Prediction Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize prediction engine
prediction_engine = SimplePredictionEngine()

class PredictRequest(BaseModel):
    sport: str
    home_team: str
    away_team: str
    league: Optional[str] = None
    odds: Optional[Dict[str, float]] = None

@app.get("/")
def home():
    return {"status": "VIT Engine Running", "version": "2.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
async def run_prediction(body: PredictRequest):
    """Predict match outcome"""
    start = time.time()
    
    try:
        if body.sport.lower() == "football":
            odds_data = body.odds if body.odds else {"over_2_5": 1.85}
            
            result = prediction_engine.predict_football_match(
                home_team=body.home_team,
                away_team=body.away_team,
                league=body.league,
                odds_data=odds_data
            )
            
            probs = result.get("probabilities", {})
            expected_goals = result.get("expected_goals", {})
            
            return {
                "home_win": probs.get("home_win", 0.5),
                "draw": probs.get("draw", 0.25),
                "away_win": probs.get("away_win", 0.25),
                "predicted_home_score": expected_goals.get("home"),
                "predicted_away_score": expected_goals.get("away"),
                "expected_goals": expected_goals,
                "over_2_5_prob": probs.get("over_2_5"),
                "expected_value": result.get("expected_value"),
                "value_bets": result.get("value_bets"),
                "model_meta": {
                    "model": "Simple Prediction Engine",
                    "league": body.league
                },
                "processing_time_ms": int((time.time() - start) * 1000)
            }
        else:
            return {
                "home_win": 0.5,
                "draw": None,
                "away_win": 0.5,
                "predicted_home_score": None,
                "predicted_away_score": None,
                "expected_goals": None,
                "over_2_5_prob": None,
                "expected_value": None,
                "value_bets": None,
                "model_meta": {"model": "Unknown sport"},
                "processing_time_ms": int((time.time() - start) * 1000)
            }
            
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_match(body: PredictRequest):
    """Simple analysis endpoint"""
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
            
            over_prob = result["probabilities"]["over_2_5"]
            ev = (over_prob * 1.85) - 1
            
            if ev > 0.1:
                value_status = "HIGH VALUE"
            elif ev > 0.05:
                value_status = "VALUE"
            elif ev > 0:
                value_status = "LOW VALUE"
            else:
                value_status = "NO VALUE"
            
            return {
                "match": f"{body.home_team} vs {body.away_team}",
                "value_status": value_status,
                "home_win": result["probabilities"]["home_win"],
                "away_win": result["probabilities"]["away_win"],
                "over_2_5": over_prob,
                "expected_value": round(ev, 4),
                "processing_time_ms": int((time.time() - start) * 1000)
            }
        else:
            return {
                "match": f"{body.home_team} vs {body.away_team}",
                "value_status": "NO VALUE",
                "message": "Analysis only available for football",
                "processing_time_ms": int((time.time() - start) * 1000)
            }
            
    except Exception as e:
        print(f"Error in analyze: {e}")
        return {
            "match": f"{body.home_team} vs {body.away_team}",
            "value_status": "ERROR",
            "error": str(e),
            "processing_time_ms": int((time.time() - start) * 1000)
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
