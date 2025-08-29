import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- API Setup ---
API_KEY = "53671f365354459bf8177e122344ba4d"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# --- Fetch Fixtures ---
def get_fixtures(start_date="2025-08-15", end_date="2025-08-17"):
   # url = f"{BASE_URL}/fixtures?from={start_date}&to={end_date}"
   # response = requests.get(url, headers=HEADERS)
   # print(response.json())
   return
    #return response.json().get("response", [])




def get_leagues(season=2025):
        url =f"{BASE_URL}/leagues?season={season}&type=league&country=England&current=true"
        response = requests.get(url, headers=HEADERS)
        print(url)
        print (response.json())
        return response.json().get("response", {})

# --- Fetch Team Stats ---
def get_team_stats(team_id, league_id, season=2025):
    url = f"{BASE_URL}/teams/statistics?team={team_id}&league={league_id}&season={season}"

    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", {})

# --- Fetch H2H ---
def get_h2h(team1_id, team2_id):
    url = f"{BASE_URL}/fixtures/headtohead?h2h={team1_id}-{team2_id}"

    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", [])

# --- Apply Filters ---
def is_high_scoring_fixture(stats1, stats2, h2h_data):
    try:
        # Season averages
        avg_goals_1 = stats1['goals']['for']['average']['total'] + stats1['goals']['against']['average']['total']
        avg_goals_2 = stats2['goals']['for']['average']['total'] + stats2['goals']['against']['average']['total']
        if avg_goals_1 <= 2.5 or avg_goals_2 <= 2.5:
            return False

        # Goals conceded
        if stats1['goals']['against']['average']['total'] <= 1.0 or stats2['goals']['against']['average']['total'] <= 1.0:
            return False

        # Recent form (mocked as last 5 matches)
        recent_1 = stats1['fixtures']['wins']['total'] + stats1['fixtures']['loses']['total']
        recent_2 = stats2['fixtures']['wins']['total'] + stats2['fixtures']['loses']['total']
        if recent_1 < 5 or recent_2 < 5:
            return False

        # H2H over 2.5 goals
        over_2_5_count = sum(1 for match in h2h_data if match['goals']['home'] + match['goals']['away'] > 2.5)
        if len(h2h_data) >= 5 and over_2_5_count / len(h2h_data) < 0.6:
            return False

        return True
    except:
        return False

# --- Streamlit UI ---
st.title("⚽ High-Scoring Fixture Tracker")


leagues = get_leagues()
for league in leagues:
    info = league['league']
    country = league['country']['name']
    print(f"{info['name']} ({country}) — ID: {info['id']}")

#fixtures = get_fixtures()
qualified = []


df = pd.DataFrame(qualified)
st.dataframe(df)
