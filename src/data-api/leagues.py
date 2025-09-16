from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from football_data_api import *
import requests


from team_statistics import *

# - "England","Scotland","France","Germany","Italy", "Croatia", "Denmark","Ireland","USA"
filter_countries = ["England", "Scotland", "France", "Germany", "Italy", "Croatia", "Denmark", "Ireland", "USA","Japan",
                    "Hungary","Finland","Norway","Iceland","Switzerland","Spain","Netherlands", "Portugal", "Poland", "Belgium","Brazil","Turkey"]


#filter_countries = ["Finland"]



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




