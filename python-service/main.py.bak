"""
VIT Platform - Main API Server
===============================
FastAPI server for football, basketball, and tennis predictions
with advanced Expected Value calculations and ticket analysis.

Version: 2.0
"""

import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from enum import Enum

# Import existing models
from model import FootballPredictionModel
from data import get_data

# Import enhanced models
from enhanced_model import FootballPredictionModel as EnhancedFootballModel
from analyze_ticket import TicketAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="VIT Prediction Engine",
    description="Sports betting analytics with EV calculations",
    version="2.0.0"
)

# Initialize models
football_model = FootballPredictionModel()  # Original model
enhanced_model = EnhancedFootballModel()     # New enhanced model
ticket_analyzer = TicketAnalyzer(model=enhanced_model)

# ============================================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================================

class Sport(str, Enum):
    """Supported sports"""
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    TENNIS = "tennis"


class PredictRequest(BaseModel):
    """Prediction request model"""
    sport: Sport = Field(..., description="Sport type")
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    league: Optional[str] = Field(None, description="League name (for football)")
    odds: Optional[Dict[str, float]] = Field(None, description="Bookmaker odds for EV calculation")


class PredictResponse(BaseModel):
    """Prediction response model"""
    home_win: float = Field(..., description="Probability of home win")
    draw: Optional[float] = Field(None, description="Probability of draw (football only)")
    away_win: float = Field(..., description="Probability of away win")
    predicted_home_score: Optional[float] = Field(None, description="Expected home score")
    predicted_away_score: Optional[float] = Field(None, description="Expected away score")
    expected_goals: Optional[Dict[str, float]] = Field(None, description="Expected goals breakdown")
    additional_markets: Optional[Dict[str, float]] = Field(None, description="Over/Under and BTTS probabilities")
    score_simulations: List[Dict] = Field(default=[], description="Top scoreline probabilities")
    expected_value: Optional[Dict[str, Any]] = Field(None, description="Expected Value calculations")
    value_bets: Optional[List[Dict]] = Field(None, description="Identified value bets")
    model_meta: Dict = Field(..., description="Model metadata")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class Selection(BaseModel):
    """Single betting selection"""
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    odds: float = Field(..., description="Decimal odds for Over 2.5")
    league: Optional[str] = Field(None, description="League name")


class TicketRequest(BaseModel):
    """Betting ticket analysis request"""
    selections: List[Selection] = Field(..., description="List of selections")
    bankroll: float = Field(1000, description="Total bankroll", ge=0)


class TicketResponse(BaseModel):
    """Ticket analysis response"""
    total_selections: int
    selections: List[Dict]
    value_selections: List[Dict]
    parlay: Dict
    recommendations: List[str]
    timestamp: str


class LeagueStatsResponse(BaseModel):
    """League statistics response"""
    league: str
    avg_goals: float
    over_2_5_rate: float
    over_3_5_rate: float
    btts_rate: float
    home_win_rate: float


class ValueBetRequest(BaseModel):
    """Value bet detection request"""
    matches: List[Selection] = Field(..., description="List of matches with odds")


# ============================================================================
# Health Check & Root Endpoints
# ============================================================================

@app.get("/")
async def home():
    """Root endpoint - API status"""
    return {
        "status": "VIT Engine Running",
        "version": "2.0.0",
        "endpoints": [
            "/predict",
            "/predict/enhanced",
            "/analyze/ticket",
            "/leagues/stats",
            "/value-bets",
            "/health"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models": {
            "football": "loaded",
            "enhanced": "loaded"
        }
    }


# ============================================================================
# Prediction Endpoints
# ============================================================================

@app.get("/predict", response_model=PredictResponse)
async def run_prediction_get(
    sport: Sport = Query(..., description="Sport type"),
    home_team: str = Query(..., description="Home team"),
    away_team: str = Query(..., description="Away team")
):
    """
    GET endpoint for predictions (simplified)
    """
    request = PredictRequest(
        sport=sport,
        home_team=home_team,
        away_team=away_team
    )
    return await run_prediction(request)


@app.post("/predict", response_model=PredictResponse)
async def run_prediction(body: PredictRequest):
    """
    POST endpoint for predictions with full features

    Supports football, basketball, and tennis predictions.
    For football, includes Expected Value calculations if odds are provided.
    """
    start = time.time()

    # Football predictions
    if body.sport == Sport.FOOTBALL:
        try:
            # Get data from API
            data = get_data(body.home_team, body.away_team)

            # Use enhanced model if odds are provided
            if body.odds:
                result = enhanced_model.predict_with_league_stats(
                    home_team=body.home_team,
                    away_team=body.away_team,
                    league=body.league,
                    odds_data=body.odds,
                    simulations=50000
                )

                # Extract results
                home_win = result["home_win"]
                draw = result["draw"]
                away_win = result["away_win"]
                home_score = result["expected_goals"]["home"]
                away_score = result["expected_goals"]["away"]
                score_sims = result.get("score_simulations", [])
                additional_markets = result["additional_markets"]
                expected_value = result.get("expected_value")
                value_bets = result.get("value_bets")

                meta = {
                    "model": "Enhanced Poisson Monte Carlo with EV",
                    "home_xg": data["home_xg"],
                    "away_xg": data["away_xg"],
                    "league": body.league,
                    "simulations": 50000,
                    "ev_calculated": True
                }
            else:
                # Use original model for basic predictions
                result = football_model.simulate_match(data["home_xg"], data["away_xg"])
                home_win = result["home_win"]
                draw = result["draw"]
                away_win = result["away_win"]
                home_score = result["expected_goals"]["home"]
                away_score = result["expected_goals"]["away"]
                score_sims = result.get("score_simulations", [])
                additional_markets = result["additional_markets"]
                expected_value = None
                value_bets = None

                meta = {
                    "model": "Poisson Monte Carlo",
                    "home_xg": data["home_xg"],
                    "away_xg": data["away_xg"],
                    "simulations": 50000,
                    "ev_calculated": False
                }

            processing_ms = int((time.time() - start) * 1000)

            return PredictResponse(
                home_win=home_win,
                draw=draw,
                away_win=away_win,
                predicted_home_score=home_score,
                predicted_away_score=away_score,
                expected_goals=result["expected_goals"],
                additional_markets=additional_markets,
                score_simulations=score_sims[:10],  # Top 10 scorelines
                expected_value=expected_value,
                value_bets=value_bets,
                model_meta=meta,
                processing_time_ms=processing_ms
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    # Basketball predictions (placeholder - to be enhanced)
    elif body.sport == Sport.BASKETBALL:
        # Basic basketball prediction
        home_win = 0.58
        draw = None
        away_win = 0.42
        home_score = 112.4
        away_score = 108.1
        score_sims = []
        additional_markets = {
            "over_220": 0.52,
            "over_230": 0.45,
            "over_240": 0.38
        }

        meta = {
            "model": "Pace-Adjusted Normal",
            "note": "Enhanced basketball model coming soon"
        }

        processing_ms = int((time.time() - start) * 1000)

        return PredictResponse(
            home_win=home_win,
            draw=draw,
            away_win=away_win,
            predicted_home_score=home_score,
            predicted_away_score=away_score,
            expected_goals={"home": home_score, "away": away_score, "total": home_score + away_score},
            additional_markets=additional_markets,
            score_simulations=score_sims,
            expected_value=None,
            value_bets=None,
            model_meta=meta,
            processing_time_ms=processing_ms
        )

    # Tennis predictions (placeholder)
    elif body.sport == Sport.TENNIS:
        home_win = 0.61
        draw = None
        away_win = 0.39
        home_score = None
        away_score = None
        score_sims = []

        meta = {
            "model": "Markov Set Model",
            "note": "Tennis model coming soon"
        }

        processing_ms = int((time.time() - start) * 1000)

        return PredictResponse(
            home_win=home_win,
            draw=draw,
            away_win=away_win,
            predicted_home_score=home_score,
            predicted_away_score=away_score,
            expected_goals=None,
            additional_markets=None,
            score_simulations=score_sims,
            expected_value=None,
            value_bets=None,
            model_meta=meta,
            processing_time_ms=processing_ms
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported sport: {body.sport}")


# ============================================================================
# Enhanced Prediction Endpoints
# ============================================================================

@app.post("/predict/enhanced", response_model=PredictResponse)
async def predict_enhanced(body: PredictRequest):
    """
    Enhanced prediction endpoint with full features
    Always uses the enhanced model with league statistics
    """
    start = time.time()

    if body.sport != Sport.FOOTBALL:
        raise HTTPException(status_code=400, detail="Enhanced predictions only available for football")

    try:
        # Get data from API
        data = get_data(body.home_team, body.away_team)

        # Use enhanced model
        result = enhanced_model.predict_with_league_stats(
            home_team=body.home_team,
            away_team=body.away_team,
            league=body.league,
            odds_data=body.odds,
            simulations=50000
        )

        processing_ms = int((time.time() - start) * 1000)

        return PredictResponse(
            home_win=result["home_win"],
            draw=result["draw"],
            away_win=result["away_win"],
            predicted_home_score=result["expected_goals"]["home"],
            predicted_away_score=result["expected_goals"]["away"],
            expected_goals=result["expected_goals"],
            additional_markets=result["additional_markets"],
            score_simulations=result.get("score_simulations", [])[:10],
            expected_value=result.get("expected_value"),
            value_bets=result.get("value_bets"),
            model_meta={
                "model": "Enhanced Poisson with League Stats",
                "home_xg": data["home_xg"],
                "away_xg": data["away_xg"],
                "league": body.league,
                "simulations": 50000,
                "league_stats": result.get("league_stats", {})
            },
            processing_time_ms=processing_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced prediction error: {str(e)}")


# ============================================================================
# Ticket Analysis Endpoints
# ============================================================================

@app.post("/analyze/ticket", response_model=TicketResponse)
async def analyze_ticket(request: TicketRequest):
    """
    Analyze a betting ticket/accumulator

    Provides:
    - Individual selection analysis with EV
    - Parlay probability and expected value
    - Kelly Criterion bet sizing
    - Actionable recommendations
    """
    start = time.time()

    try:
        # Convert selections to dictionary format
        selections = [
            {
                "home_team": sel.home_team,
                "away_team": sel.away_team,
                "odds": sel.odds,
                "league": sel.league
            }
            for sel in request.selections
        ]

        # Analyze the ticket
        result = ticket_analyzer.analyze_ticket(
            selections=selections,
            bankroll=request.bankroll
        )

        # Add processing time
        result["processing_time_ms"] = int((time.time() - start) * 1000)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticket analysis error: {str(e)}")


# ============================================================================
# League Statistics Endpoints
# ============================================================================

@app.get("/leagues/stats", response_model=List[LeagueStatsResponse])
async def get_league_stats(
    league: Optional[str] = Query(None, description="Filter by league name")
):
    """
    Get statistics for all leagues or a specific league

    Returns:
        - Average goals per game
        - Over 2.5/3.5 rates
        - BTTS rate
        - Home win rate
    """
    try:
        if league:
            stats = enhanced_model.league_stats.get(league)
            if not stats:
                raise HTTPException(status_code=404, detail=f"League '{league}' not found")
            return [LeagueStatsResponse(league=league, **stats)]

        # Return all leagues
        return [
            LeagueStatsResponse(league=name, **stats)
            for name, stats in enhanced_model.league_stats.items()
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching league stats: {str(e)}")


# ============================================================================
# Value Bet Detection Endpoints
# ============================================================================

@app.post("/value-bets")
async def detect_value_bets(request: ValueBetRequest):
    """
    Detect value betting opportunities across multiple matches

    Returns matches where the model probability suggests
    the odds offer positive expected value.
    """
    start = time.time()

    try:
        value_bets = []

        for match in request.matches:
            # Prepare odds data
            odds_data = {"over_2_5": match.odds}

            # Get prediction
            result = enhanced_model.predict_with_league_stats(
                home_team=match.home_team,
                away_team=match.away_team,
                league=match.league,
                odds_data=odds_data,
                simulations=50000
            )

            # Check for value bets
            if result.get("value_bets"):
                for bet in result["value_bets"]:
                    bet["match"] = f"{match.home_team} vs {match.away_team}"
                    bet["league"] = match.league
                    value_bets.append(bet)

        # Sort by highest expected value
        value_bets.sort(key=lambda x: -x["expected_value"])

        return {
            "total_value_bets": len(value_bets),
            "value_bets": value_bets,
            "processing_time_ms": int((time.time() - start) * 1000)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Value bet detection error: {str(e)}")


# ============================================================================
# Batch Prediction Endpoint
# ============================================================================

@app.post("/predict/batch")
async def batch_predict(matches: List[PredictRequest]):
    """
    Batch prediction for multiple matches

    Useful for analyzing multiple fixtures at once
    """
    start = time.time()

    results = []

    for match in matches:
        try:
            # Get prediction
            data = get_data(match.home_team, match.away_team)
            result = football_model.simulate_match(data["home_xg"], data["away_xg"])

            results.append({
                "match": f"{match.home_team} vs {match.away_team}",
                "home_win": result["home_win"],
                "draw": result["draw"],
                "away_win": result["away_win"],
                "expected_goals": result["expected_goals"],
                "over_2_5": result["additional_markets"]["over_2_5"]
            })
        except Exception as e:
            results.append({
                "match": f"{match.home_team} vs {match.away_team}",
                "error": str(e)
            })

    return {
        "total": len(matches),
        "results": results,
        "processing_time_ms": int((time.time() - start) * 1000)
    }


# ============================================================================
# Model Information Endpoint
# ============================================================================

@app.get("/model/info")
async def model_info():
    """Get information about the prediction models"""
    return {
        "models": {
            "football": {
                "name": "Poisson Monte Carlo",
                "version": "2.0",
                "features": [
                    "Team strength parameters",
                    "Home advantage factor",
                    "Overdispersion (negative binomial)",
                    "Monte Carlo simulations",
                    "Expected Value calculation"
                ]
            },
            "enhanced": {
                "name": "Enhanced Poisson with League Stats",
                "version": "2.0",
                "features": [
                    "All football features",
                    "League-specific statistics",
                    "Expected Value calculation",
                    "Kelly Criterion",
                    "Ticket/accumulator analysis",
                    "Value bet detection"
                ]
            }
        },
        "supported_leagues": list(enhanced_model.league_stats.keys()),
        "simulations_default": 50000
    }


# ============================================================================
# Main entry point (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)