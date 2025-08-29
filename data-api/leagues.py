from datetime import datetime, timedelta

import requests
import team_statistics

# --- API Setup ---
API_KEY = "53671f365354459bf8177e122344ba4d"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# - "England","Scotland","France","Germany","Italy", "Croatia", "Denmark","Ireland","USA"
filter_countries = ["Ireland","USA","Germany","England","Denmark","Italy"]

# - Get All Leagues That Are Running This Season - #
def get_leagues(season=2025):
        url =f"{BASE_URL}/leagues?season={season}&type=league&current=true"
        response = requests.get(url, headers=HEADERS)
        print(url)
        print (response.json())
        return response.json().get("response", {})


def get_fixtures(league, date_from, season=2025):
    url = f"{BASE_URL}/fixtures?season={season}&league={league['league']['id']}&date={date_from}"
    response = requests.get(url, headers=HEADERS)
    print(url)
    return response.json().get("response", {})


def get_upcoming_weekend():
    today = datetime.today()



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
def filter_leagues(countries=filter_countries):
    leagues = get_leagues()
    leagues_filtered =  []
    for league in leagues:
        country = league['country']['name']
        if country in countries:
                #Only Include The Leagues With Statistics
                if league['seasons'][0]['coverage']['fixtures']['statistics_fixtures']==True:
                    leagues_filtered.append(league)
    return leagues_filtered



def filter_fixtures_by_weekend(league):
    weekend = get_upcoming_weekend()
    fixtures = []
    for day in weekend:
        days = get_fixtures(league,day)
        for fixture in days:
            fixtures.append(fixture)
    return fixtures


def get_25_prediction(fixture):
    url = f"{BASE_URL}/predictions?fixture={fixture["fixture"]["id"]}"
    response = requests.get(url, headers=HEADERS)
    values = response.json().get("response", {})
    over_under=0
    try:
        if len(values)>0:
            if values[0]["predictions"]["under_over"] is not None:
                over_under = abs(float(values[0]["predictions"]["under_over"]))
    except TypeError as e:
            print(values[0]["predictions"]["under_over"])

    return over_under

def validate_fixture_criteria(fixtures):
    betting_list=[]
    for fixture in fixtures:
        # make sure both teams have a 2.5 avaregae ratio
        is25=get_25_prediction(fixture)
        if(is25>=2.5):
            betting_list.append(fixture)

            ##stats = team_statistics.get_fixture_statistic(fixture)
            ##if stats[0]["clean_sheet_perc"] < 0.4 and stats[1]["clean_sheet_perc"]<0.4:
             ##   if stats[0]["failed_to_score_perc"] < 0.4 and stats[1]["failed_to_score_perc"]<0.4:
             ##       if stats[0]["average_goals"] > 2 and stats[1]["average_goals"] > 2:
              ##          print("BAH")
              ##          betting_list.append(fixture)

    return betting_list



leagues = filter_leagues()
all_bets=[]
for league in leagues:
    info = league['league']
    print(info)
    fixtures = filter_fixtures_by_weekend(league)
    betting_list = validate_fixture_criteria(fixtures);
    all_bets = all_bets+betting_list
print(all_bets)


