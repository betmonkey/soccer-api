from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from football_data_api import get_fixtures
from team_statistics import get_team_statistics_for_season, calculate_team_statistics_for_period


class Fixture:
    def __init__(self, fixture_data):
        self.fixture = fixture_data
        self.home_id = fixture_data["teams"]["home"]["id"]
        self.away_id = fixture_data["teams"]["away"]["id"]
        self.league_id = fixture_data["league"]["id"]
        self.season = fixture_data["league"]["season"]
        self.date_str = fixture_data["fixture"]["date"]
        self.date_obj = datetime.fromisoformat(self.date_str.replace("Z", "+00:00")).astimezone(
            ZoneInfo("Europe/London"))
        self.formatted_date = self.date_obj.strftime('%Y-%m-%d')
        self.stats = None
        self.home_team_history = None
        self.away_team_history = None

    def set_stats(self, stats):
        self.stats = stats

    def recalculate_fixture_statistics_period(self, overs=2.5, no_games=5):
        home_team = self.home_team_history
        away_team = self.away_team_history

        home_team_stats = calculate_team_statistics_for_period(home_team, overs, no_games)
        away_team_stats = calculate_team_statistics_for_period(away_team, overs, no_games)

        for k in home_team_stats.keys():
            self.stats["home_team"][k] = home_team_stats[k]

        for k in away_team_stats.keys():
            self.stats["away_team"][k] = home_team_stats[k]



    #@classmethod
    #def filter_high_scoring_candidates(cls, league):
    #    candidates = []
    #    fixtures = cls.get_weekend_fixtures(league)
    #    for fixture in fixtures:
    #        try:
    #            print("------------------------------------------------------------------------")
    #            print(f"Examining Fixture: {fixture.fixture['teams']['home']['name']} vs {fixture.fixture['teams']['away']['name']}")
    #            if fixture.qualifies_for_over_model():
    #                candidates.append(fixture.fixture)
    #        except ZeroDivisionError:
    #            print("Division By Zero Error")
    #    return candidates
