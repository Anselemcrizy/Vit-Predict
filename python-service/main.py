"""
main.py — VIT Prediction Engine (Python FastAPI Service)
"""

import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal

from data import get_data
from model import predict_football, predict_basketball, predict_tennis

app = FastAPI(title="VIT Model Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    sport: Literal["football", "basketball", "tennis"]
    home_team: str
    away_team: str


class PredictResponse(BaseModel):
    sport: str
    home_team: str
    away_team: str
    home_win: float
    draw: Optional[float]
    away_win: float
    predicted_home_score: Optional[float]
    predicted_away_score: Optional[float]
    score_simulations: list[dict]
    model_meta: dict
    processing_time_ms: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    start = time.time()

    sport = req.sport
    home = req.home_team.strip()
    away = req.away_team.strip()

    if not home or not away:
        raise HTTPException(status_code=400, detail="home_team and away_team are required")

    data = get_data()
    home_xg = data["home_xg"]
    away_xg = data["away_xg"]

    if sport == "football":
        result = predict_football(home_xg, away_xg)
        meta = {"model": "Poisson Monte Carlo", "home_xg": home_xg, "away_xg": away_xg, "simulations": 50000}

    elif sport == "basketball":
        result = predict_basketball(
            home_ortg=115.0,
            away_ortg=113.0,
            home_pace=99.0,
            away_pace=99.0,
        )
        meta = {"model": "Pace-Adjusted Normal", "note": "stub data"}

    elif sport == "tennis":
        result = predict_tennis(
            home_serve_win=0.63,
            away_serve_win=0.61,
        )
        meta = {"model": "Set-Win Markov", "note": "stub data"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")

    elapsed_ms = int((time.time() - start) * 1000)

    return PredictResponse(
        sport=sport,
        home_team=home,
        away_team=away,
        home_win=result["home_win"],
        draw=result.get("draw"),
        away_win=result["away_win"],
        predicted_home_score=result.get("predicted_home_score"),
        predicted_away_score=result.get("predicted_away_score"),
        score_simulations=result.get("score_simulations", []),
        model_meta=meta,
        processing_time_ms=elapsed_ms,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=False)
