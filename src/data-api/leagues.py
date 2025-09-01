from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from football_data_api import *
import requests

from team_statistics import (has_low_clean_sheet_rate, has_high_goal_activity, recent_over_25, scores_consistently,
                             qualifies_for_over25_model, get_fixture_statistic)

# - "England","Scotland","France","Germany","Italy", "Croatia", "Denmark","Ireland","USA"
filter_countries = ["England", "Scotland", "France", "Germany", "Italy", "Croatia", "Denmark", "Ireland", "USA","Japan",
                    "Hungary","Finland","Norway","Iceland","Switzerland"]


#filter_countries = ["USA"]

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
    }


# - Filter Those Leagues Based On a Particular Country - #
def filter_leagues(countries=None):
    if countries is None:
        countries = filter_countries
    leagues = get_leagues()
    leagues_filtered = []
    for league in leagues:
        country = league['country']['name']
        if country in countries:
            #Only Include The Leagues With Statistics
            if league['seasons'][0]['coverage']['fixtures']['statistics_fixtures']:
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



def validate_fixture_criteria(fixtures):
    betting_list = []
    for fixture in fixtures:
        try:
            print("------------------------------------------------------------------------")
            print(f"Examining Fixture....{fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
            stats = get_fixture_statistic(fixture)
            if qualifies_for_over25_model(stats):
                betting_list.append(fixture)
        except ZeroDivisionError as e:
            print("Division By Zero Error")
        # betting_list.append(fixture)
    return betting_list



