from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import time
import numpy as np

app = FastAPI()

class PredictRequest(BaseModel):
    sport: str
    home_team: str
    away_team: str
    league: Optional[str] = None

@app.get("/")
def home():
    return {"status": "VIT Engine Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(body: PredictRequest):
    """Simple analyze endpoint"""
    try:
        print(f"Received request: {body}")
        
        # Simple prediction logic
        if body.sport == "football":
            # Calculate a simple probability
            over_2_5_prob = 0.52  # Default
            odds = 1.85
            ev = (over_2_5_prob * odds) - 1
            
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
                "home_win": 0.46,
                "away_win": 0.27,
                "over_2_5": over_2_5_prob,
                "expected_value": ev,
                "processing_time_ms": 50
            }
        else:
            return {
                "match": f"{body.home_team} vs {body.away_team}",
                "value_status": "NO VALUE",
                "message": "Only football supported"
            }
            
    except Exception as e:
        print(f"Error: {e}")
        return {
            "match": f"{body.home_team} vs {body.away_team}",
            "value_status": "ERROR",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
