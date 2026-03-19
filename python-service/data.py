import os
import requests
from typing import Optional

APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
API_BASE = "https://v3.football.api-sports.io"

_team_cache: dict = {}


def _headers() -> dict:
    return {"x-apisports-key": APIFOOTBALL_KEY}


def _search_team(name: str) -> Optional[dict]:
    try:
        res = requests.get(
            f"{API_BASE}/teams",
            params={"name": name},
            headers=_headers(),
            timeout=5,
        )
        teams = res.json().get("response", [])
        return teams[0] if teams else None
    except Exception:
        return None


def _get_team_league(team_id: int) -> Optional[int]:
    try:
        res = requests.get(
            f"{API_BASE}/leagues",
            params={"team": team_id, "current": "true"},
            headers=_headers(),
            timeout=5,
        )
        leagues = res.json().get("response", [])
        for entry in leagues:
            if entry.get("league", {}).get("type") == "League":
                return entry["league"]["id"]
        return leagues[0]["league"]["id"] if leagues else None
    except Exception:
        return None


def _get_avg_goals(team_id: int, league_id: int) -> float:
    try:
        res = requests.get(
            f"{API_BASE}/teams/statistics",
            params={"team": team_id, "league": league_id, "season": 2024},
            headers=_headers(),
            timeout=5,
        )
        stats = res.json().get("response", {})
        avg = (
            stats.get("goals", {})
            .get("for", {})
            .get("average", {})
            .get("total", None)
        )
        return float(avg) if avg else 1.2
    except Exception:
        return 1.2


def get_team_xg(team_name: str) -> float:
    """
    Fetch a team's average goals scored per game from API-Football (used as xG proxy).
    Results are cached in memory per session. Falls back to 1.2 if unavailable.
    """
    if team_name in _team_cache:
        return _team_cache[team_name]

    if not APIFOOTBALL_KEY:
        return 1.2

    team = _search_team(team_name)
    if not team:
        _team_cache[team_name] = 1.2
        return 1.2

    team_id = team["team"]["id"]
    league_id = _get_team_league(team_id)
    if not league_id:
        _team_cache[team_name] = 1.2
        return 1.2

    xg = _get_avg_goals(team_id, league_id)
    _team_cache[team_name] = xg
    return xg


def get_data(home_team: str = "Arsenal", away_team: str = "Chelsea") -> dict:
    """
    Return match data for both teams with xG values from API-Football.
    Falls back to sensible defaults if the API is unavailable.
    """
    home_xg = get_team_xg(home_team)
    away_xg = get_team_xg(away_team)

    return {
        "home": home_team,
        "away": away_team,
        "home_xg": home_xg,
        "away_xg": away_xg,
    }
