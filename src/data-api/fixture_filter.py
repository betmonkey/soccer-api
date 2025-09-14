from typing import List

from fixture import Fixture


class FilterFilter():
    def filterFixtures(self, fixtures: List[Fixture], goals_consistency=0.5, clean_sheet_ratio=0.5,
                       over_goal_per_game=2.5):
        filteredFixtures = []
        for fix in fixtures:
            print(f"Examining Fixture: {fix.fixture['teams']['home']['name']} vs {fix.fixture['teams']['away']['name']}")
            if self._qualifies_for_over_model(fix, goals_consistency, clean_sheet_ratio, over_goal_per_game):
                filteredFixtures.append(fix)
                print("Bet........")
        return filteredFixtures

    def _qualifies_for_over_model(self, fixture, goals_consistency=0.5, clean_sheet_ratio=0.5, over_goal_per_game=2.5):
        return (
                self._has_low_clean_sheet_rate(fixture, clean_sheet_ratio) and
                self._scores_consistently(fixture, goals_consistency) and
                self._has_high_goal_activity(fixture, over_goal_per_game) and
                self._recent_over(fixture)
        )

    def _has_low_clean_sheet_rate(self, fixture, threshold):
        home = fixture.stats["home_team"]["clean_sheet_home_perc"]
        away = fixture.stats["away_team"]["clean_sheet_away_perc"]
        print(f"Clean Sheet Ratio Home: {home} Away: {away} Threshold {threshold}")
        return home < threshold and away < threshold

    def _scores_consistently(self, fixture, threshold):
        home = fixture.stats["home_team"]["failed_to_score_home_perc"]
        away = fixture.stats["away_team"]["failed_to_score_away_perc"]
        print(f"Failed to Score % Home: {home} Away: {away}")
        return home < threshold and away < threshold

    def _has_high_goal_activity(self, fixture, threshold):
        home = fixture.stats["home_team"]["average_goals_for_home"] + fixture.stats["home_team"][
            "average_goals_against_home"]
        away = fixture.stats["away_team"]["average_goals_for_away"] + fixture.stats["away_team"][
            "average_goals_against_away"]
        print(f"Home Avg Goals: {home} Away Avg Goals: {away}")
        return home >= threshold and away >= threshold

    def _recent_over(self, fixture):
        home_flag = fixture.stats["home_team"].get("over_last_x")
        away_flag = fixture.stats["away_team"].get("over_last_x")
        print(f"Recent Over Home: {home_flag} Away: {away_flag}")
        return home_flag and away_flag
