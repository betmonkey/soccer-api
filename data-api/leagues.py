from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import team_statistics

# --- API Setup ---
API_KEY = "53671f365354459bf8177e122344ba4d"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# - "England","Scotland","France","Germany","Italy", "Croatia", "Denmark","Ireland","USA"
filter_countries = ["England", "Scotland", "France", "Germany", "Italy", "Croatia", "Denmark", "Ireland", "USA","Japan","Hungary","Finland","Norway"]


# - Get All Leagues That Are Running This Season - #
def get_leagues(season=2025):
    url = f"{BASE_URL}/leagues?season={season}&type=league&current=true"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", {})


def get_fixtures(league, date_from, season=2025):
    url = f"{BASE_URL}/fixtures?season={season}&league={league['league']['id']}&date={date_from}&timezone='Europe/London'"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", {})


def get_upcoming_weekend():
    today = datetime.now(ZoneInfo("Europe/London"))
    weekday = today.weekday()  # Monday = 0, Sunday = 6

    # Calculate days until Friday (weekday 4)
    days_until_friday = (4 - weekday) % 7
    friday = today + timedelta(days=days_until_friday)
    saturday = friday + timedelta(days=1)
    sunday = friday + timedelta(days=2)

    return {
        friday.strftime("%Y-%m-%d"),
        saturday.strftime("%Y-%m-%d"),
        sunday.strftime("%Y-%m-%d")
        # "2025-08-30",
        # "2025-08-31"
    }


# - Filter Those Leagues Based On a Particular Country - #
def filter_leagues(countries=filter_countries):
    leagues = get_leagues()
    leagues_filtered = []
    for league in leagues:
        country = league['country']['name']
        if country in countries:
            #Only Include The Leagues With Statistics
            if league['seasons'][0]['coverage']['fixtures']['statistics_fixtures'] == True:
                leagues_filtered.append(league)
    return leagues_filtered


def filter_fixtures_by_weekend(league):
    weekend = get_upcoming_weekend()
    fixtures = []
    for day in weekend:
        days = get_fixtures(league, day)
        for fixture in days:
            fixtures.append(fixture)
    return fixtures


def get_25_prediction(fixture):
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

    return over_under


def has_low_clean_sheet_rate(stats, threshold=0.5):
    """Both teams must have < threshold clean sheet rate."""
    print(f"Clean Sheet Ratio Home: {stats['home_team']['clean_sheet_home_perc']} Away :{stats['away_team']['clean_sheet_home_perc']}")
    return (
            stats["home_team"]["clean_sheet_home_perc"] < threshold and
            stats["away_team"]["clean_sheet_away_perc"] < threshold
    )


def scores_consistently(stats, threshold=0.5):
    """Both teams must fail to score in < threshold of games."""
    print(f"Teams Failed To Score Percentage Home: {stats['home_team']['failed_to_score_home_perc']} Away :{stats['away_team']['failed_to_score_away_perc']}")
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
    if not clean_sheets:
        print("Not Suitable As Not Got Clean Sheet Ratio")
    scores_consistency = scores_consistently(stats)

    if not scores_consistency:
        print("Not Suitable As Not Scoring Consistently")

    goal_activity = has_high_goal_activity(stats)
    if not goal_activity:
        print("Not Suitable As Not High Goal Activity Home Average For/Against")

    recent_over25 = recent_over_25(stats)
    if not recent_over25:
        print(f"Not Suitable Recent Over 25 Home:{stats['home_team']['over_25_last_x']} Away:{stats['away_team']["over_25_last_x"]}")

    return (
            clean_sheets and
            scores_consistency and
            goal_activity and
            recent_over25
    )


def validate_fixture_criteria(fixtures):
    betting_list = []
    for fixture in fixtures:
        try:
            print("------------------------------------------------------------------------")
            print(f"Examining Fixture....{fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
            stats = team_statistics.get_fixture_statistic(fixture)
            if qualifies_for_over25_model(stats):
                print("Suitable to Bet")
                betting_list.append(fixture)
        except ZeroDivisionError as e:
            print("Division By Zero Error")
        # betting_list.append(fixture)
    return betting_list


leagues = filter_leagues()
all_bets = []
for league in leagues:
    info = league['league']
    fixtures = filter_fixtures_by_weekend(league)
    betting_list = validate_fixture_criteria(fixtures);
    all_bets = all_bets + betting_list

print(all_bets)
