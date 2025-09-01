import requests

# --- API Setup ---
API_KEY = "53671f365354459bf8177e122344ba4d"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}


# - Get All Leagues That Are Running This Season - #
def get_leagues(season=2025):
    url = f"{BASE_URL}/leagues?season={season}&type=league&current=true"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", {})


def get_fixtures(league, date_from, season=2025):
    url = f"{BASE_URL}/fixtures?season={season}&league={league['league']['id']}&date={date_from}&timezone='Europe/London'"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", {})


def get_statistics(team_id, season, league_id, to_date):
    stats_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&league={league_id}&season={season}&date={to_date}"
    stats_params = {
        "team": team_id,
        "season": season,
        "league": league_id
    }
    team_stats = requests.get(stats_url, headers=HEADERS).json().get("response", {})
    return team_stats


def get_fixture_prediction(fixture):
    url = f"{BASE_URL}/predictions?fixture={fixture["fixture"]["id"]}"
    response = requests.get(url, headers=HEADERS)
    values = response.json().get("response", {})
    over_under = 0
    try:
        if len(values) > 0:
            if values[0]["predictions"]["under_over"] is not None:
                over_under = float(values[0]["predictions"]["under_over"])
    except TypeError as e:
        print(values[0]["predictions"]["under_over"])
    return values


def get_last_x_fixtures(team, num_games):
    url = f"{BASE_URL}/fixtures?team={team}&last={num_games}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", {})