from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from football_data_api import get_season_historical_fixtures, get_last_x_fixtures
from fixture import *
from football_data_api import get_fixtures, get_statistics
from fixture_filter import FilterFilter
from team_statistics import calculate_team_statistics_for_period


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FixtureFactory(metaclass=SingletonMeta):
    def __init__(self):
        self._cache = {}

    def get_fixtures_for_league(self, league, days):
        fixtures = []
        for day in days:
            key = f"{league['league']['id']}_{day}"
            if key in self._cache:
                print("FOUND IN CACHE")

            if key not in self._cache:
                base_fixtures = get_fixtures(league, day)
                fixturelist = []
                for base_fixture in base_fixtures:
                    fixture = Fixture(base_fixture)
                    fixture.home_team_history = self.__fetch_fixture_team_history(fixture.home_id, fixture.league_id,
                                                                                  fixture.season)
                    fixture.away_team_history = self.__fetch_fixture_team_history(fixture.away_id, fixture.league_id,
                                                                                  fixture.season)
                    # fixture.home_team_history = self.__fetch_last_x_games(fixture.home_id,2)
                    # fixture.away_team_history = self.__fetch_last_x_games(fixture.away_id,2)
                    stats = self.__fetch_statistics(fixture)
                    fixture.set_stats(stats)
                    fixture.recalculate_fixture_statistics_period()
                    fixturelist.append(fixture)
                self._cache[key] = fixturelist
            fixtures.append(self._cache[key])
        return fixtures

    def __fetch_fixture_team_history(self, team_id, league, season):
        return get_season_historical_fixtures(team_id, league, season)

    def __fetch_last_x_games(self, team_id, no_games):
        return get_last_x_fixtures(team_id, no_games)

    def __fetch_statistics(self, fixture: Fixture):
        #Get the base statistics for home and away and calculate others

        home_team_stats = get_statistics(fixture.home_id, fixture.season, fixture.league_id, fixture.formatted_date)
        away_team_stats = get_statistics(fixture.away_id, fixture.season, fixture.league_id, fixture.formatted_date)

        enriched_home_team_stats = get_team_statistics_for_season(home_team_stats)
        enriched_away_team_stats = get_team_statistics_for_season(away_team_stats)

        return {'home_team': enriched_home_team_stats,
                'away_team': enriched_away_team_stats}


