import numpy as np
from typing import Optional

def predict(home_xg: float, away_xg: float, simulations: int = 50000) -> dict:
    """
    Poisson-based Monte Carlo simulation for football match outcomes.
    Returns win/draw/loss probabilities and most likely scorelines.
    """
    np.random.seed(None)
    home_goals = np.random.poisson(home_xg, simulations)
    away_goals = np.random.poisson(away_xg, simulations)

    home_win = float((home_goals > away_goals).mean())
    draw = float((home_goals == away_goals).mean())
    away_win = float((home_goals < away_goals).mean())

    score_counts: dict[tuple, int] = {}
    for h, a in zip(home_goals.tolist(), away_goals.tolist()):
        k = (int(h), int(a))
        score_counts[k] = score_counts.get(k, 0) + 1

    top_scores = sorted(score_counts.items(), key=lambda x: -x[1])[:8]
    score_simulations = [
        {"home": h, "away": a, "probability": round(count / simulations, 4)}
        for (h, a), count in top_scores
    ]

    return {
        "home_win": round(home_win, 4),
        "draw": round(draw, 4),
        "away_win": round(away_win, 4),
        "score_simulations": score_simulations,
        "predicted_home_score": round(home_xg, 2),
        "predicted_away_score": round(away_xg, 2),
    }


def predict_basketball(home_ortg: float, away_ortg: float, home_pace: float, away_pace: float, simulations: int = 50000) -> dict:
    """
    Pace-adjusted scoring model for basketball.
    Uses normal distribution around expected scores.
    """
    np.random.seed(None)
    avg_pace = (home_pace + away_pace) / 2
    possessions = avg_pace

    home_score_mean = (home_ortg / 100) * possessions
    away_score_mean = (away_ortg / 100) * possessions

    home_scores = np.random.normal(home_score_mean, 10, simulations)
    away_scores = np.random.normal(away_score_mean, 10, simulations)

    home_win = float((home_scores > away_scores).mean())
    away_win = 1.0 - home_win

    spread = home_score_mean - away_score_mean
    total = home_score_mean + away_score_mean

    score_pairs = list(zip(np.round(home_scores[:6]).astype(int).tolist(), np.round(away_scores[:6]).astype(int).tolist()))
    score_simulations = [
        {"home": h, "away": a, "probability": round(1 / 6, 4)}
        for h, a in score_pairs
    ]

    return {
        "home_win": round(home_win, 4),
        "draw": None,
        "away_win": round(away_win, 4),
        "score_simulations": score_simulations,
        "predicted_home_score": round(home_score_mean, 1),
        "predicted_away_score": round(away_score_mean, 1),
        "spread": round(spread, 1),
        "total": round(total, 1),
    }


def predict_tennis(home_serve_win: float, away_serve_win: float, best_of: int = 3) -> dict:
    """
    Set-based Markov model for tennis.
    Simulates game-level probabilities up to set and match wins.
    """
    np.random.seed(None)

    def point_win_prob(server_win: float) -> float:
        return server_win

    def game_win_prob(server_pwin: float) -> float:
        p = server_pwin
        q = 1 - p
        return (p**4 * (15*q**3 + 10*q**2 + 6*q + 1) - 0) / (p**4 * (15*q**3 + 10*q**2 + 6*q + 1) + q**4 * (15*p**3 + 10*p**2 + 6*p + 1))

    def set_win_prob(server_game_win: float, receiver_game_win: float) -> float:
        s, r = server_game_win, receiver_game_win
        num = s**6 * sum([(6+k-1) / (k * (6-1)) * r**k * s**(6-1) for k in range(0, 5 + 1)] + [s**5 / (s**5 + r**5) * r**5])
        return min(0.95, max(0.05, s / (s + r)))

    pgw1 = game_win_prob(home_serve_win)
    pgw2 = game_win_prob(away_serve_win)
    p_home_set = set_win_prob(pgw1, 1 - pgw2)
    p_away_set = 1 - p_home_set

    sets_needed = (best_of + 1) // 2
    simulations = 50000
    home_sets = np.random.binomial(1, p_home_set, (simulations, best_of)).cumsum(axis=1)
    away_sets = np.arange(1, best_of + 1) - home_sets

    home_wins = int(((home_sets[:, -1] >= sets_needed)).sum())
    home_win_prob = home_wins / simulations
    away_win_prob = 1 - home_win_prob

    score_simulations = []
    for h_s in range(sets_needed, best_of + 1):
        for a_s in range(0, sets_needed):
            p = (p_home_set ** h_s) * (p_away_set ** a_s)
            score_simulations.append({"home": h_s, "away": a_s, "probability": round(p, 4)})
        if h_s != sets_needed:
            p = (p_away_set ** sets_needed) * (p_home_set ** (h_s - 1))
            score_simulations.append({"home": h_s - 1, "away": sets_needed, "probability": round(p, 4)})
    score_simulations = sorted(score_simulations, key=lambda x: -x["probability"])[:6]

    return {
        "home_win": round(home_win_prob, 4),
        "draw": None,
        "away_win": round(away_win_prob, 4),
        "score_simulations": score_simulations,
        "predicted_home_score": None,
        "predicted_away_score": None,
        "set_win_prob": round(p_home_set, 4),
    }
