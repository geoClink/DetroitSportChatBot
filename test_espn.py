"""
Pytest tests for sports_tools.py.
Run with: python -m pytest test_espn.py -v
"""
import pytest
from sports_tools import (
    get_nfl_scores,
    get_nba_scores,
    get_mlb_scores,
    get_nhl_scores,
    get_standings,
    get_schedule,
    run_tool,
)


# --- Score functions ---

def test_nfl_scores_returns_list():
    assert isinstance(get_nfl_scores(), list)

def test_nba_scores_returns_list():
    assert isinstance(get_nba_scores(), list)

def test_mlb_scores_returns_list():
    assert isinstance(get_mlb_scores(), list)

def test_nhl_scores_returns_list():
    assert isinstance(get_nhl_scores(), list)

def test_score_game_has_required_keys():
    games = get_nfl_scores()
    # If there are games and no API error, each game must have these keys
    for game in games:
        if "error" not in game:
            assert "home" in game
            assert "away" in game
            assert "home_score" in game
            assert "away_score" in game
            assert "status" in game
            break  # one clean game is enough to confirm the shape


# --- run_tool dispatch ---

def test_run_tool_scores_dispatch():
    for tool_name in ["get_nfl_scores", "get_nba_scores", "get_mlb_scores", "get_nhl_scores"]:
        result = run_tool(tool_name)
        assert isinstance(result, list), f"{tool_name} should return a list"

def test_run_tool_unknown_returns_empty_list():
    assert run_tool("this_tool_does_not_exist") == []

def test_run_tool_standings_nfl():
    result = run_tool("get_standings", {"sport": "nfl"})
    assert isinstance(result, list)

def test_run_tool_schedule_mlb():
    result = run_tool("get_schedule", {"sport": "mlb"})
    assert isinstance(result, list)


# --- Standings shape ---

def test_standings_entry_has_required_keys():
    standings = get_standings("nfl")
    for entry in standings:
        if "error" not in entry:
            assert "team" in entry
            assert "wins" in entry
            assert "losses" in entry
            assert "is_detroit" in entry
            break


# --- Schedule shape ---

def test_schedule_entry_has_required_keys():
    schedule = get_schedule("nfl")
    for game in schedule:
        if "error" not in game and "message" not in game:
            assert "date" in game
            assert "home" in game
            assert "away" in game
            break
