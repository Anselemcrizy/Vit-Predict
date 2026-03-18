"""
main.py — VIT Prediction Engine (Python FastAPI Service)
Exposes a /predict endpoint that runs model.py against data.py stats.
"""

import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal

from data import get_football_matchup, get_basketball_matchup, get_tennis_matchup
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

    if sport == "football":
        home_xg, away_xg = get_football_matchup(home, away)
        result = predict_football(home_xg, away_xg)
        meta = {"model": "Poisson Monte Carlo", "home_xg": home_xg, "away_xg": away_xg, "simulations": 50000}

    elif sport == "basketball":
        matchup = get_basketball_matchup(home, away)
        result = predict_basketball(
            home_ortg=matchup["home_ortg"],
            away_ortg=matchup["away_ortg"],
            home_pace=matchup["pace"],
            away_pace=matchup["pace"],
        )
        meta = {"model": "Pace-Adjusted Normal", **matchup}

    elif sport == "tennis":
        matchup = get_tennis_matchup(home, away)
        result = predict_tennis(
            home_serve_win=matchup["home_serve_win"],
            away_serve_win=matchup["away_serve_win"],
        )
        meta = {"model": "Set-Win Markov", **matchup}

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
