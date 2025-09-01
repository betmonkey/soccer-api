from football_data_api import get_leagues, get_fixture_prediction, get_fixtures, get_statistics, get_last_x_fixtures
from unittest.mock import patch
import pytest


# --- Happy path tests ---


@patch("requests.get")
def test_get_leagues(mock_get):
    mock_get.return_value.json.return_value = {
        "response": [
            {
                "league": {"id": 39, "name": "Premier League", "type": "League",
                           "logo": "https://media.api-sports.io/football/leagues/39.png"},
                "country": {"name": "England", "code": "GB", "flag": "https://media.api-sports.io/flags/gb.svg"},
                "season": {"year": 2019, "current": True}
            }
        ]
    }
    result = get_leagues(season=2019)
    assert isinstance(result, list)
    assert result[0]["league"]["name"] == "Premier League"


@patch("requests.get")
def test_get_fixtures(mock_get):
    league = {"league": {"id": 39}}
    mock_get.return_value.json.return_value = {
        "response": [
            {
                "fixture": {"id": 215662, "date": "2019-08-11T15:30:00+00:00", "timestamp": 1565537400,
                            "venue": {"id": 556, "name": "Old Trafford", "city": "Manchester"},
                            "status": {"long": "Match Finished", "short": "FT", "elapsed": 90}},
                "teams": {"home": {"id": 33, "name": "Manchester United"}, "away": {"id": 51, "name": "Chelsea"}},
                "goals": {"home": 4, "away": 0},
                "league": {"id": 39, "name": "Premier League"}
            }
        ]
    }
    result = get_fixtures(league, "2019-08-11")
    assert isinstance(result, list)
    assert result[0]["fixture"]["id"] == 215662


@patch("requests.get")
def test_get_statistics(mock_get):
    mock_get.return_value.json.return_value = {
        "get": "teams/statistics",
        "parameters": {"league": "39", "season": "2019", "team": "33"},
        "errors": [],
        "results": 11,
        "paging": {"current": 1, "total": 1},
        "response": {
            "league": {"id": 39, "name": "Premier League"},
            "team": {"id": 33, "name": "Manchester United"},
            "fixtures": {"played": {"home": 19, "away": 19, "total": 38}},
            "goals": {"for": {"total": {"home": 40, "away": 26, "total": 66}}},
            "clean_sheet": {"home": 7, "away": 6, "total": 13}
        }
    }
    result = get_statistics(team_id=33, season=2019, league_id=39, to_date="2020-05-30")
    assert isinstance(result, dict)
    assert result["team"]["name"] == "Manchester United"
    assert result["fixtures"]["played"]["total"] == 38


@patch("requests.get")
def test_get_fixture_prediction(mock_get):
    fixture = {"fixture": {"id": 215662}}
    mock_get.return_value.json.return_value = {
        "response": [
            {"predictions": {"winner": {"id": 33, "name": "Manchester United"}, "under_over": "2.5"},
             "teams": {"home": {"id": 33}, "away": {"id": 51}}}
        ]
    }
    result = get_fixture_prediction(fixture)
    assert isinstance(result, list)
    assert result[0]["predictions"]["winner"]["name"] == "Manchester United"


@patch("requests.get")
def test_get_last_x_fixtures(mock_get):
    mock_get.return_value.json.return_value = {
        "response": [
            {
                "fixture": {"id": 12345, "date": "2023-08-20T15:00:00+00:00", "timestamp": 1692543600,
                            "venue": {"name": "Old Trafford", "city": "Manchester"},
                            "status": {"long": "Match Finished", "short": "FT", "elapsed": 90}},
                "teams": {"home": {"id": 33, "name": "Manchester United"},
                          "away": {"id": 50, "name": "Manchester City"}},
                "goals": {"home": 2, "away": 1},
                "league": {"id": 39, "name": "Premier League"}
            }
        ]
    }
    result = get_last_x_fixtures(team=33, num_games=5)
    assert isinstance(result, list)
    assert result[0]["teams"]["home"]["name"] == "Manchester United"


# --- Edge case tests ---


@patch("requests.get")
def test_get_leagues_empty(mock_get):
    mock_get.return_value.json.return_value = {"response": []}
    result = get_leagues(season=2025)
    assert result == []


@patch("requests.get")
def test_get_fixtures_no_data(mock_get):
    league = {"league": {"id": 999}}
    mock_get.return_value.json.return_value = {"response": []}
    result = get_fixtures(league, "2025-09-01")
    assert result == []


@patch("requests.get")
def test_get_statistics_error(mock_get):
    mock_get.return_value.json.return_value = {"errors": ["Invalid team"], "response": {}}
    result = get_statistics(team_id=0, season=2025, league_id=39, to_date="2025-09-01")
    assert result == {}


@patch("requests.get")
def test_get_fixture_prediction_empty(mock_get):
    fixture = {"fixture": {"id": 999999}}
    mock_get.return_value.json.return_value = {"response": []}
    result = get_fixture_prediction(fixture)
    assert result == []
