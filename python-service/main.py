import time
from fastapi import FastAPI
from pydantic import BaseModel
from model import FootballPredictionModel
from data import get_data

app = FastAPI()
football_model = FootballPredictionModel()


class PredictRequest(BaseModel):
    sport: str
    home_team: str
    away_team: str


@app.get("/")
def home():
    return {"status": "VIT Engine Running"}


@app.get("/predict")
def run_prediction_get():
    data = get_data()
    result = football_model.simulate_match(data["home_xg"], data["away_xg"])
    return {
        "match": f'{data["home"]} vs {data["away"]}',
        "prediction": result
    }


@app.post("/predict")
def run_prediction(body: PredictRequest):
    start = time.time()
    data = get_data()

    if body.sport == "football":
        result = football_model.simulate_match(data["home_xg"], data["away_xg"])
        home_score = result["expected_goals"]["home"]
        away_score = result["expected_goals"]["away"]
        draw = result["draw"]
        score_sims = result["score_simulations"]
        meta = {
            "model": "Poisson Monte Carlo",
            "home_xg": data["home_xg"],
            "away_xg": data["away_xg"],
            "simulations": 50000,
        }

    elif body.sport == "basketball":
        # Stub: pace-adjusted normal model placeholder until real data arrives
        home_win = 0.58
        draw = None
        away_win = 0.42
        home_score = 112.4
        away_score = 108.1
        result = {"home_win": home_win, "away_win": away_win}
        score_sims = []
        meta = {"model": "Pace-Adjusted Normal", "note": "stub data"}

    elif body.sport == "tennis":
        # Stub: Markov set model placeholder until real data arrives
        home_win = 0.61
        draw = None
        away_win = 0.39
        home_score = None
        away_score = None
        result = {"home_win": home_win, "away_win": away_win}
        score_sims = []
        meta = {"model": "Markov Set Model", "note": "stub data"}

    else:
        result = {"home_win": 0.5, "away_win": 0.5}
        home_score = None
        away_score = None
        draw = None
        score_sims = []
        meta = {"model": "unknown"}

    processing_ms = int((time.time() - start) * 1000)

    return {
        "home_win": result.get("home_win", 0.5),
        "draw": draw if body.sport == "football" else None,
        "away_win": result.get("away_win", 0.5),
        "predicted_home_score": home_score,
        "predicted_away_score": away_score,
        "score_simulations": score_sims,
        "model_meta": meta,
        "processing_time_ms": processing_ms,
    }
