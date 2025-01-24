import nba_api.stats.endpoints as e
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime
import requests
import json
from django.core.management.base import BaseCommand
from peltzerspicks.models import Prediction  # Ensure this matches your app name


class Command(BaseCommand):
    help = "Fetch NBA predictions and store them in the database"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching NBA predictions...")

        sport = 'nba'
        today = str(datetime.today())[:10]

        ### Get Odds Data from Yahoo ###
        def get_yahoo_json(sport, date):
            url = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues=' + sport + '&date=' + date
            r = requests.get(url)
            j = json.loads(r.text)
            return j['service']['scoreboard']

        def get_yahoo_lines(sport, date):
            j = get_yahoo_json(sport, date)
            if 'games' not in j.keys():
                self.stdout.write(self.style.WARNING(f"{date}: No games today"))
                return None
            df = pd.DataFrame()
            for game in j['games']:
                game_info = j['games'][game]
                home_team = j['teams'][game_info['home_team_id']]['abbr']
                away_team = j['teams'][game_info['away_team_id']]['abbr']
                status = game_info['status_description']
                if status == 'Postponed':
                    self.stdout.write(self.style.WARNING(f"Postponed: {home_team} vs {away_team}"))
                    continue
                if 'gameodds' not in j or game not in j['gameodds']:
                    self.stdout.write(self.style.WARNING(f"Missing odds for: {home_team} vs {away_team}"))
                    continue
                game_odds = j['gameodds'][game]
                D = pd.DataFrame.from_dict(game_odds, orient='index').drop(columns='last_update')
                D['date'] = date
                D['team'] = home_team
                D['opp'] = away_team
                D['is_home'] = True
                df = pd.concat((df, D))
            return df

        ODDS = get_yahoo_lines(sport, today)
        if ODDS is None:
            return

        ### Fix Team Abbreviations ###
        TEAMS = teams.get_teams()
        TEAM_IDS = {team['id']: team['abbreviation'] for team in TEAMS}

        def fix_abbreviations(team):
            TO_FIX = {'GS': "GSW", 'NY': "NYK", 'SA': "SAS", 'PHO': "PHX", 'NO': "NOP"}
            return TO_FIX.get(team, team)

        ODDS['team'] = ODDS['team'].apply(fix_abbreviations)
        ODDS['opp'] = ODDS['opp'].apply(fix_abbreviations)

        df = ODDS[['date', 'team', 'opp', 'is_home', 'total']][ODDS['is_home']]

        ### Get Basic Team Ratings ###
        BASIC_RATINGS = e.LeagueDashTeamStats(season="2024-25", measure_type_detailed_defense="Advanced").get_data_frames()[0]
        BASIC_RATINGS = BASIC_RATINGS.loc[:, ['TEAM_ID', 'OFF_RATING', 'DEF_RATING', 'PACE']]
        BASIC_RATINGS['team'] = BASIC_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))
        BASIC_RATINGS['AVG_WIN_MARGIN'] = (BASIC_RATINGS['PACE'] / 100) * (BASIC_RATINGS['OFF_RATING'] - BASIC_RATINGS['DEF_RATING'])
        BASIC_RATINGS['AVG_TOTAL'] = (BASIC_RATINGS['PACE'] / 100) * (BASIC_RATINGS['OFF_RATING'] + BASIC_RATINGS['DEF_RATING'])

        ### Get Home and Road Ratings ###
        HOME_RATINGS = e.LeagueDashTeamStats(season="2024-25", measure_type_detailed_defense="Advanced", location_nullable="Home").get_data_frames()[0]
        HOME_RATINGS = HOME_RATINGS.loc[:, ['TEAM_ID', 'OFF_RATING', 'DEF_RATING', 'PACE']]
        HOME_RATINGS['team'] = HOME_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))
        HOME_RATINGS['AVG_WIN_MARGIN'] = (HOME_RATINGS['PACE'] / 100) * (HOME_RATINGS['OFF_RATING'] - HOME_RATINGS['DEF_RATING'])
        HOME_RATINGS['AVG_TOTAL'] = (HOME_RATINGS['PACE'] / 100) * (HOME_RATINGS['OFF_RATING'] + HOME_RATINGS['DEF_RATING'])

        ROAD_RATINGS = e.LeagueDashTeamStats(season="2024-25", measure_type_detailed_defense="Advanced", location_nullable="Road").get_data_frames()[0]
        ROAD_RATINGS = ROAD_RATINGS.loc[:, ['TEAM_ID', 'OFF_RATING', 'DEF_RATING', 'PACE']]
        ROAD_RATINGS['team'] = ROAD_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))
        ROAD_RATINGS['AVG_WIN_MARGIN'] = (ROAD_RATINGS['PACE'] / 100) * (ROAD_RATINGS['OFF_RATING'] - ROAD_RATINGS['DEF_RATING'])
        ROAD_RATINGS['AVG_TOTAL'] = (ROAD_RATINGS['PACE'] / 100) * (ROAD_RATINGS['OFF_RATING'] + ROAD_RATINGS['DEF_RATING'])

        ### Merge Data ###
        df = pd.merge(df, HOME_RATINGS[['team', 'AVG_WIN_MARGIN', 'AVG_TOTAL']], on='team', suffixes=['', '_home_away_adjusted'])
        df = pd.merge(df, ROAD_RATINGS[['team', 'AVG_WIN_MARGIN', 'AVG_TOTAL']], left_on='opp', right_on='team', suffixes=['', '_home_away_adjusted_opp'])
        df = df.drop(columns=['team_home_away_adjusted_opp'])

        ### Make Predictions ###
        df['predicted_total'] = .5 * (df['AVG_TOTAL_home_away_adjusted'] + df['AVG_TOTAL_home_away_adjusted_opp'])
        df['predicted_spread'] = -.5 * (df['AVG_WIN_MARGIN_home_away_adjusted'] - df['AVG_WIN_MARGIN_home_away_adjusted_opp'])
        
        df['predicted_total'] = df['predicted_total'].apply(lambda x: round(2 * x, 0) / 2)
        df['predicted_spread'] = df['predicted_spread'].apply(lambda x: round(2 * x, 0) / 2)

        df['matchup'] = df.apply(lambda row: f"{row['team']} vs. {row['opp']}", axis=1)

        ### Delete Old Predictions Before Inserting New Ones ###
        Prediction.objects.all().delete()

        ### Save Predictions to Database ###
        for _, row in df.iterrows():
            print(f"Saving: {row['matchup']}, Yahoo Total: {row['total']}, Predicted Total: {row['predicted_total']}, Yahoo Spread: {row.get('team_spread', 'N/A')}, Predicted Spread: {row['predicted_spread']}")

            Prediction.objects.create(
                date=row["date"],
                matchup=row["matchup"],
                yahoo_total=row["total"],
                yahoo_spread=row.get("team_spread", None),  
                predicted_total=row["predicted_total"],  
                predicted_spread=row["predicted_spread"],  
            )

        self.stdout.write(self.style.SUCCESS("Predictions successfully saved to the database!"))
