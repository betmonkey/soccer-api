from datetime import datetime

import requests
from football_data_api import get_last_x_fixtures, get_statistics
# --- API Setup ---

from stats_store import StatsStore


def get_fixture_statistic(fixture):
    home_id = fixture["teams"]["home"]["id"]
    away_id = fixture["teams"]["away"]["id"]
    league_id = fixture["league"]["id"]
    season = fixture["league"]["season"]
    fixture_date = fixture["fixture"]["date"]
    date_obj = datetime.fromisoformat(fixture_date.replace("Z", "+00:00"))  # Handles timezone

    formatted_date = date_obj.strftime('%Y-%m-%d')
    team_features = {}
    home_feature = get_team_statistics(home_id, season, league_id, formatted_date)
    team_features["home_team"] = home_feature
    away_feature = get_team_statistics(away_id, season, league_id, formatted_date)
    team_features["away_team"] = away_feature
    return team_features


def default_if_zero(x, default=1):
    return x if x != 0 else default


def get_team_last_x_game_statistics(team_id, num_games):
    last_games = get_last_x_fixtures(team_id, num_games)
    return last_games


def check_team_over25_lasy_x_games(team_id, num_games):
    games = get_team_last_x_game_statistics(team_id, num_games)
    over25 = True
    for game in games:
        try:
            if game["goals"]["home"] + game["goals"]["away"] < 2.5:
                over25 = False
        except TypeError as e:
            over25 = False
    return over25


def get_team_statistics(team_id, season, league_id, to_date):
    team_stats = get_statistics(team_id, season, league_id, to_date)
    over25 = check_team_over25_lasy_x_games(team_id, 2)

    # Repeat for away team and combine features
    features = {

        "team_id": team_id,

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

        "over_25_last_x": over25
    }

    return features


def has_low_clean_sheet_rate(stats, threshold=0.5):
    """Both teams must have < threshold clean sheet rate."""
    print(
        f"Clean Sheet Ratio Home: {stats['home_team']['clean_sheet_home_perc']} Away :{stats['away_team']['clean_sheet_home_perc']}")
    return (
            stats["home_team"]["clean_sheet_home_perc"] < threshold and
            stats["away_team"]["clean_sheet_away_perc"] < threshold
    )


def scores_consistently(stats, threshold=0.5):
    """Both teams must fail to score in < threshold of games."""
    print(
        f"Teams Failed To Score Percentage Home: {stats['home_team']['failed_to_score_home_perc']} Away :{stats['away_team']['failed_to_score_away_perc']}")
    return (
            stats["home_team"]["failed_to_score_home_perc"] < threshold and
            stats["away_team"]["failed_to_score_away_perc"] < threshold
    )


def has_high_goal_activity(stats, threshold=2.5):
    """Both teams must have combined goals for/against > threshold."""
    home_total = stats["home_team"]["average_goals_for_home"] + stats["home_team"]["average_goals_against_home"]
    away_total = stats["away_team"]["average_goals_for_away"] + stats["away_team"]["average_goals_against_away"]
    print(f"Home Average Goals :{home_total} Away Average Goals:{away_total}")
    return home_total >= threshold and away_total >= threshold


def recent_over_25(stats):
    """Both teams must have recent over 2.5 goal trend flagged."""

    return stats["home_team"].get("over_25_last_x") and stats["away_team"].get("over_25_last_x")


def qualifies_for_over25_model(stats):
    """Composite filter for high-scoring fixture candidates."""
    clean_sheets = has_low_clean_sheet_rate(stats)
    store = StatsStore()
    if not clean_sheets:
        print("Not Suitable As Has Had Too Many Clean Sheets")
        store.increment("Too Many Clean Sheets")
        return False
    scores_consistency = scores_consistently(stats)

    if not scores_consistency:
        print("Not Suitable As Not Scoring Consistently in Each Game")
        store.increment("Inconsistent Scoring")
        return False

    goal_activity = has_high_goal_activity(stats)
    if not goal_activity:
        print("Not Suitable As Not High Goal Activity Home Average For/Against")
        store.increment("Low Average Goals")
        return False
    recent_over25 = recent_over_25(stats)
    #
    if not recent_over25:
        store.increment("Not 2 Prev 25")
        print(
            f"Not Suitable Recent Over 25 Home:{stats['home_team']['over_25_last_x']} Away:{stats['away_team']["over_25_last_x"]}")
        return False
    if clean_sheets and scores_consistency and goal_activity and recent_over25:
        print("Betted")
        store.increment("Successfull Bet")

    return (
            clean_sheets and
            scores_consistency and
            goal_activity and
            recent_over25
    )
