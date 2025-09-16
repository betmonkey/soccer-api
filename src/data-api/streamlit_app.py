import datetime
import time
from typing import List
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import date_helper as dh

import leagues
from fixture import Fixture
from fixturefactory import FixtureFactory
import matplotlib.pyplot as plt
from fixture_filter import FilterFilter




# --------------------
# Fetch Fixtures
# --------------------
@st.cache_data
def get_fixtures(today):
    print({"data": f"Fresh data generated on {today}"})
    all_bets = []
    #Reset Singleton Every Day
    factory = FixtureFactory()
    #factory.reset()
    leagues_list = leagues.filter_leagues()
    complete_fixtures: List[Fixture] = []
    fixtures = None
    for current_league in leagues_list:
        #Gets Current Fixture List
        days = dh.get_upcoming_weekend()
        factory = FixtureFactory()
        print(f"Loading League Fixtures: {current_league["league"]["name"]}")
        fixtures = factory.get_fixtures_for_league(current_league, days)
        for day in fixtures:
            complete_fixtures.append(day)

    return complete_fixtures






# Get today's date (string is better than datetime to avoid time granularity issues)
today_str = datetime.date.today().strftime("%A, %d %B %Y")
chooser = FilterFilter()

#Got through each day and build up fixrurelist
fixtures_data = []
fixturesWithStats = get_fixtures(today_str)

# Add CSS for grid layout once
st.markdown("""
<style>
.fixture-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 12px 0;
    background: #fff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    font-family: Arial, sans-serif;
}

.fixture-card .team {
    display: flex;
    flex-direction: column;
    max-width: 40%;
}

/* Smaller font for mobile screens */
@media (max-width: 600px) {
    .fixture-card .team span {
        font-size: 10px; /* smaller size on mobile */
    }
}
.fixture-card .team img {
    vertical-align: middle;
    margin: 0 6px;
}

.fixture-card .team-results {
    font-size: 8px;
    color: #666;
    margin-top: 4px;
    line-height: 1.3em;
}

.fixture-card .time {
    font-size: 13px;
    font-weight: bold;
    color: #333;
    padding: 0 10px;
    white-space: nowrap;
}


.percentage-container {
    width: 60px; /* max width */
    background-color: #e0e0e0;
    border-radius: 12px;
    overflow: hidden;
}

.percentage-box {
    height: 18px;
    line-height: 18px;
    background-color: #4caf50;
    color: white;
    text-align: center;
    font-size: 10px;
    font-weight: bold;
    transition: width 0.3s ease-in-out;
}


</style>
""", unsafe_allow_html=True)



#Sliders for filter criteria

with st.sidebar.expander("⚙️ Filter Criteria", expanded=False):
    goals_consistency = st.slider(
        "Goals Consistency", min_value=0.0, max_value=1.0, value=0.5, step=0.1
    )

    clean_sheet_ratio = st.slider(
        "Clean Sheet Ratio", min_value=0.0, max_value=1.0, value=0.5, step=0.1
    )

    over_goal_per_game = st.slider(
        "Over Goals Per Game", min_value=0.0, max_value=5.0, value=2.5, step=0.5
    )

    game_history = st.slider(
        "Game History", min_value=1, max_value=10, value=2, step=1)



#Get Filrered
for fixforDay in fixturesWithStats:
    print(clean_sheet_ratio)
    for fix in fixforDay:
        fix.recalculate_fixture_statistics_period(over_goal_per_game, game_history)

    filturedFixures = chooser.filterFixtures(
        fixforDay,
        goals_consistency=goals_consistency,
        clean_sheet_ratio=clean_sheet_ratio,
        over_goal_per_game=over_goal_per_game

    )

    if len(filturedFixures) > 0:
        fixtures_data.extend(filturedFixures)

# ✅ Sort fixtures by date/time
fixtures_data = sorted(
    fixtures_data,
    key=lambda x: x.date_obj)



st.markdown(f'''
<div style="text-align:center; font-size:24px; font-weight:bold;">
Weekend Fixtures > {over_goal_per_game}
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div style="text-align:left; font-size:10px; font-weight:bold;">
Total Weekend Fixtures: {len(fixturesWithStats)}
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div style="text-align:left; font-size:10px; font-weight:bold;">
Total Selected: {len(fixtures_data)}
</div>
''', unsafe_allow_html=True)


st.markdown(f'''
<div style="text-align:left; font-size:10px; font-weight:bold;">
Leagues In Play: {leagues.filter_countries}
</div>
''', unsafe_allow_html=True)

current_date = None
current_league = None



current_date = None
current_league = None

current_date = None
current_league = None

# Helper to build results as HTML inside the card
def build_results_html(history, team_type="home"):
    results = []
    for f in history:
        home_team = f['teams']['home']['name']
        away_team = f['teams']['away']['name']
        home_goals = f['goals']['home']
        away_goals = f['goals']['away']

        if team_type == "home":
            indicator = "🟢" if home_goals > away_goals else "🔴" if home_goals < away_goals else "⚪"
        else:
            indicator = "🟢" if away_goals > home_goals else "🔴" if away_goals < home_goals else "⚪"

        # Use <b> for bold goals
        results.append(f"{indicator} {home_team} <b>{home_goals}</b> - {away_team} <b>{away_goals}</b>")

    return "<br>".join(results)

# Loop through fixtures
for fix in fixtures_data:
    fixture = fix.fixture["fixture"]
    teams = fix.fixture["teams"]
    league = fix.fixture["league"]

    home = teams['home']
    away = teams['away']
    time = fixture["date"]

    home_history = fix.home_team_history[:game_history]
    away_history = fix.away_team_history[:game_history]

    home_result_html = build_results_html(home_history)
    away_result_html = build_results_html(away_history, team_type="away")

    kickoff_dt = datetime.datetime.fromisoformat(time.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/London"))
    kickoff_date = kickoff_dt.strftime("%A, %d %B %Y")
    kickoff_time = kickoff_dt.strftime("%H:%M")

    # Render date header if new
    if current_date != kickoff_date:
        #if current_date is not None:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f'<div class="date-header"><b>{kickoff_date}</b></div>', unsafe_allow_html=True)
        current_date = kickoff_date
        current_league = None

    # Render league header if new
    if current_league != league['name']:

        st.markdown(
            f'<div class="league-title"><img src="{league["flag"]}" width="20" style="vertical-align:middle;"> {league["country"]} : {league["name"]} - {league["round"]}</div>',
            unsafe_allow_html=True
        )
        current_league = league['name']

    # Build and render full fixture card
    card_html = f"""
    <div class="fixture-card">
        <!-- Home team -->
        <div class="team">
            <div style="display:flex; align-items:center; gap:6px;">
                <img src="{home['logo']}" width="22">
                <span>{home['name']}</span>
                 <div class="percentage-container">
                    <div class="percentage-box" style="width:{fix.stats['home_team']['total_perc_of_over_x']:.0f}%;">
                        {fix.stats["home_team"]["total_perc_of_over_x"]:.0f}%
                    </div>
                </div>
            </div>
            <div class="team-results">{home_result_html}</div>
        </div>
        <!-- Kickoff time -->
        <div class="time">{kickoff_time}</div>
        <!-- Away team -->
        <div class="team" style="text-align:right;">
            <div style="display:flex; justify-content:flex-end; align-items:center; gap:6px;">
                <div class="percentage-container">
                    <div class="percentage-box" style="width:{fix.stats['away_team']['total_perc_of_over_x']:.0f}%;">
                        {fix.stats["away_team"]["total_perc_of_over_x"]:.0f}%
                    </div>
                </div>
                <span>{away['name']}</span>
                <img src="{away['logo']}" width="22">
            </div>
            <div class="team-results" style="text-align:right;">{away_result_html}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)