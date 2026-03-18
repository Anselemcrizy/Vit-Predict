from fastapi import FastAPI
from model import predict
from data import get_data

app = FastAPI()

@app.get("/")
def home():
    return {"status": "VIT Engine Running"}

@app.get("/predict")
def run_prediction():
    data = get_data()
    result = predict(data["home_xg"], data["away_xg"])

    return {
        "match": f'{data["home"]} vs {data["away"]}',
        "prediction": result
    }
