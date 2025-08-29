from datetime import datetime

import requests

# --- API Setup ---
API_KEY = "53671f365354459bf8177e122344ba4d"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

def get_fixture_statistic(fixture):
    home_id = fixture["teams"]["home"]["id"]
    away_id = fixture["teams"]["away"]["id"]
    league_id = fixture["league"]["id"]
    season = fixture["league"]["season"]
    fixture_date=fixture["fixture"]["date"]
    date_obj = datetime.fromisoformat(fixture_date.replace("Z", "+00:00"))  # Handles timezone

    formatted_date = date_obj.strftime('%Y-%m-%d')
    team_features=[]
    home_feature = get_team_statistics(home_id, season, league_id,formatted_date)
    team_features.append(home_feature)
    away_feature = get_team_statistics(away_id, season, league_id,formatted_date)
    team_features.append(away_feature)
    return team_features

def get_team_statistics(team_id, season, league_id, to_date):
    stats_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&league={league_id}&season={season}&date={to_date}"
    stats_params = {
        "team": team_id,
        "season": season,
        "league": league_id
    }
    team_stats = requests.get(stats_url, headers=HEADERS).json().get("response", {})


    # Repeat for away team and combine features
    features = {

        "team_id": team_id,

        #Goals Scored Per Match
        "average_goals_for": team_stats["goals"]["for"]["average"],
        "average_goals_against": team_stats["goals"]["against"]["average"],

        #Goals Average Total Per Match For and Against
        "average_goals": float(team_stats["goals"]["for"]["average"]["total"])+float(team_stats["goals"]["against"]["average"]["total"]),


        #Clean Sheet Percentage
        "clean_sheet_perc":  team_stats["clean_sheet"]["total"] / team_stats["fixtures"]["played"]["total"],

        #Failed to Score Percentage
        "failed_to_score_perc": team_stats["failed_to_score"]["total"] / team_stats["fixtures"]["played"]["total"]

    }


    return features
