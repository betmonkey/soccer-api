from datetime import datetime

import requests
from football_data_api import get_last_x_fixtures, get_statistics
# --- API Setup ---



def default_if_zero(x, default=1):
    return x if x != 0 else default


def check_team_over_last_x_games(team_history, over_amount, no_games=5):
    over25 = True
    if len(team_history) < no_games:
        return False
    for fixture in team_history[:no_games]:
        try:
            if fixture["goals"]["home"] + fixture["goals"]["away"] < over_amount:
                over25 = False
        except TypeError as e:
            over25 = False
    return over25


#, to_date, overs=2.5, history=2
def get_team_statistics_for_season(team_stats, overs=2.5):
    # Repeat for away team and combine features
    features = {

        "team_id": team_stats["team"]["id"],

        #Goals Scored Per Match
        "average_goals_for": team_stats["goals"]["for"]["average"]["total"],
        "average_goals_against": team_stats["goals"]["against"]["average"]["total"],

        #Goals Average Total Per Match For and Against
        "average_goals": float(team_stats["goals"]["for"]["average"]["total"]) + float(
            team_stats["goals"]["against"]["average"]["total"]),

        "average_goals_for_home": team_stats["goals"]["for"]["total"]["home"] / default_if_zero(
            team_stats["fixtures"]["played"]["home"]),

        "average_goals_for_away": team_stats["goals"]["for"]["total"]["away"] / default_if_zero(
            team_stats["fixtures"]["played"]["away"]),

        "average_goals_against_home": team_stats["goals"]["against"]["total"]["home"] / default_if_zero(
            team_stats["fixtures"]["played"]["home"]),

        "average_goals_against_away": team_stats["goals"]["against"]["total"]["away"] / default_if_zero(
            team_stats["fixtures"]["played"]["away"]),

        #Clean Sheet Percentage
        "clean_sheet_perc": team_stats["clean_sheet"]["total"] / default_if_zero(
            team_stats["fixtures"]["played"]["total"]),

        #Failed to Score Percentage
        "failed_to_score_perc": team_stats["failed_to_score"]["total"] / default_if_zero(
            team_stats["fixtures"]["played"]["total"]),

        #Failed to Score Home Percentage
        "failed_to_score_home_perc": team_stats["failed_to_score"]["home"] / default_if_zero(
            team_stats["fixtures"]["played"]["home"]),

        # Failed to Score Away Percentage
        "failed_to_score_away_perc": team_stats["failed_to_score"]["away"] / default_if_zero(
            team_stats["fixtures"]["played"]["away"]),

        # Clean Sheet Percentage
        "clean_sheet_home_perc": team_stats["clean_sheet"]["home"] / default_if_zero(
            team_stats["fixtures"]["played"]["home"]),

        # Failed to Score Percentage
        "clean_sheet_away_perc": team_stats["clean_sheet"]["away"] / default_if_zero(
            team_stats["fixtures"]["played"]["away"]),

    }

    return features


def calculate_team_statistics_for_period(team_history, overs, no_games):
    features = {
        "over_last_x": check_team_over_last_x_games(team_history, overs, no_games)
    }
    return features
