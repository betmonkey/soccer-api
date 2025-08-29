import streamlit as st
import requests
import pandas as pd
import datetime
import leagues


st.set_page_config(page_title="Football Fixtures > 2.5")
st.title("⚽ Upcoming Football Fixtures > 2.5")


# --------------------
# Fetch Fixtures
# --------------------
@st.cache_data
def get_fixtures(today):
    print ({"data": f"Fresh data generated on {today}"})
    leagues_list = leagues.filter_leagues()
    all_bets = []
    for current_league in leagues_list:
        info = current_league['league']
        fixtures = leagues.filter_fixtures_by_weekend(current_league)
        betting_list = leagues.validate_fixture_criteria(fixtures)
        all_bets = all_bets + betting_list
    return all_bets

# Get today's date (string is better than datetime to avoid time granularity issues)
today_str = datetime.date.today().isoformat()
fixtures_data = get_fixtures(today_str)



import streamlit as st
from datetime import datetime

# ✅ Sort fixtures by date/time
fixtures_data = sorted(
    fixtures_data,
    key=lambda x: datetime.fromisoformat(x["fixture"]["date"].replace("Z", "+00:00"))
)

# Add CSS for grid layout once
st.markdown("""
<style>
.fixtures-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

    # Parse datetime
    kickoff_dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
    kickoff_date = kickoff_dt.strftime("%A, %d %B %Y")  # e.g. Friday, 29 August 2025
    kickoff_time = kickoff_dt.strftime("%H:%M")

    # ✅ Add new date header
    if current_date != kickoff_date:
        st.markdown(f'<div class="date-header">{kickoff_date}</div>', unsafe_allow_html=True)
        current_date = kickoff_date
        current_league = None  # reset league for new day

    # ✅ Add new league header inside the date
    if current_league != league['name']:
        st.markdown(f'<div class="league-title">{league["name"]} - {league["round"]}</div>', unsafe_allow_html=True)
        current_league = league['name']

    # Fixture card
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

# Close grid
st.markdown('</div>', unsafe_allow_html=True)