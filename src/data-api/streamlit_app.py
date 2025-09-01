import datetime
import time
from zoneinfo import ZoneInfo
import pandas as pd

import streamlit as st


import leagues
from stats_store import StatsStore
import matplotlib.pyplot as plt

def get_stats_df():
    raw = StatsStore().all()
    return pd.DataFrame(list(raw.items()), columns=["Label", "Value"])


# --------------------
# Fetch Fixtures
# --------------------
@st.cache_data
def get_fixtures(today):
    print({"data": f"Fresh data generated on {today}"})
    all_bets = []
    leagues_list = leagues.filter_leagues()
    all_bets = []
    for current_league in leagues_list:
        fixtures = leagues.filter_fixtures_by_weekend(current_league)
        betting_list = leagues.validate_fixture_criteria(fixtures)
        all_bets = all_bets + betting_list
        #time.sleep(30)

    return all_bets


# Get today's date (string is better than datetime to avoid time granularity issues)
today_str = datetime.date.today().strftime("%A, %d %B %Y")
if datetime.date.today().weekday() in [4, 5, 6]:
    today_str = "Weekend"


fixtures_data = get_fixtures(today_str)

# ✅ Sort fixtures by date/time
fixtures_data = sorted(
    fixtures_data,
    key=lambda x: datetime.datetime.fromisoformat(x["fixture"]["date"].replace("Z", "+00:00"))
)

# Add CSS for grid layout once
st.markdown("""
<style>
.fixtures-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
    gap: 16px;
    margin-top: 10px;
}
.fixture-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 12px 16px;
    background: #fff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    font-family: Arial, sans-serif;
}
.fixture-card .team {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
}
.fixture-card .time {
    font-weight: bold;
    font-size: 14px;
    color: #333;
}
.date-header {
    grid-column: 1 / -1;
    font-size: 16px;
    font-weight: 700;
    color: #222;
    margin: 16px 0 4px 0;
    padding-top: 10px;
    border-top: 2px solid #ddd;
}
.league-title {
    grid-column: 1 / -1;
    font-size: 14px;
    font-weight: 600;
    color: #555;
    margin: 6px 0 2px 0;
}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="Football Fixtures > 2.5")
st.title("⚽  Football Fixtures > 2.5")
st.markdown(f'<div class="league-title">{leagues.filter_countries}</div>', unsafe_allow_html=True)


# Start grid container
st.markdown('<div class="fixtures-grid">', unsafe_allow_html=True)

current_date = None
current_league = None

# Create two columns: left for fixtures, right for chart
left_col, right_col = st.columns([2, 1])  # Wider left column for grid

with left_col:
    # Start grid container
    st.markdown('<div class="fixtures-grid">', unsafe_allow_html=True)

    current_date = None
    current_league = None

    for fix in fixtures_data:
        fixture = fix["fixture"]
        teams = fix["teams"]
        league = fix["league"]

        home = teams['home']
        away = teams['away']
        time = fixture["date"]

        kickoff_dt = datetime.datetime.fromisoformat(time.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/London"))
        kickoff_date = kickoff_dt.strftime("%A, %d %B %Y")
        kickoff_time = kickoff_dt.strftime("%H:%M")

        if current_date != kickoff_date:
            st.markdown(f'<div class="date-header">{kickoff_date}</div>', unsafe_allow_html=True)
            current_date = kickoff_date
            current_league = None

        if current_league != league['name']:
            st.markdown(f'<div class="league-title">{league["name"]} - {league["round"]}</div>', unsafe_allow_html=True)
            current_league = league['name']

        card_html = f"""
        <div class="fixture-card">
            <div class="team">
                <img src="{home['logo']}" width="22"> {home['name']}
            </div>
            <div class="time">{kickoff_time}</div>
            <div class="team" style="justify-content: flex-end;">
                {away['name']} <img src="{away['logo']}" width="22">
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

df = get_stats_df()
with right_col:
    st.markdown('<div>', unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.bar(df["Label"], df["Value"], color="cornflowerblue")
    ax.set_ylabel("Value")
    ax.tick_params(axis='x', labelrotation=45)

    ax.set_title("Reasons")
    st.pyplot(fig)

    st.markdown('</div>', unsafe_allow_html=True)
