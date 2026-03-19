from fastapi import FastAPI
from model import FootballPredictionModel
from data import get_data

app = FastAPI()
model = FootballPredictionModel()

@app.get("/")
def home():
    return {"status": "VIT Engine Running"}

@app.get("/predict")
def run_prediction():
    data = get_data()
    result = model.simulate_match(data["home_xg"], data["away_xg"])

    return {
        "match": f'{data["home"]} vs {data["away"]}',
        "prediction": result
    }
