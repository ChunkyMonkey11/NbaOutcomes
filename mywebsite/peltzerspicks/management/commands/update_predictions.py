import nba_api.stats.endpoints as e
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime
import requests
import json
from django.core.management.base import BaseCommand
from peltzerspicks.models import Prediction  # Ensure this matches your app name


# Might be pulling the home and not away

class Command(BaseCommand):
    help = "Fetch NBA predictions and store them in the database"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching NBA predictions...")

        sport = 'nba'
        today = str(datetime.today())[:10]

        ### Step 1: Fetch Odds Data from Yahoo ###
        def get_yahoo_json(sport, date):
            """
            Retrieves the JSON response for the given sport and date from Yahoo Sports API.
            """
            url = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues=' + sport + '&date=' + date
            r = requests.get(url)
            j = json.loads(r.text)
            return j['service']['scoreboard']

        def get_yahoo_lines(sport, date):
            """
            Extracts betting lines and team matchups from Yahoo Sports API.
            """
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
                
                # Skip postponed games
                if status == 'Postponed':
                    self.stdout.write(self.style.WARNING(f"Postponed: {home_team} vs {away_team}"))
                    continue
                
                # Skip games with missing odds
                if 'gameodds' not in j or game not in j['gameodds']:
                    self.stdout.write(self.style.WARNING(f"Missing odds for: {home_team} vs {away_team}"))
                    continue
                
                game_odds = j['gameodds'][game]
                #D = pd.DataFrame.from_dict(game_odds, orient='index').drop(columns='last_update')
                D = pd.DataFrame.from_dict(game_odds, orient='index')
                D['date'] = date
                D['team'] = home_team
                D['opp'] = away_team
                D['is_home'] = True
                df = pd.concat((df, D))
                #E = pd.DataFrame.from_dict(game_odds, orient='index').drop(columns='last_update')
                E = pd.DataFrame.from_dict(game_odds, orient='index')
                E['date'] = date
                E['team'] = away_team
                E['opp'] = home_team
                E['is_home'] = False
                df = pd.concat((df, D))
            return df

        ODDS = get_yahoo_lines(sport, today)
        if ODDS is None:
            return

        ### Step 2: Fix Team Abbreviations ###
        TEAMS = teams.get_teams()
        TEAM_IDS = {team['id']: team['abbreviation'] for team in TEAMS}

        def fix_abbreviations(team):
            """
            Fixes inconsistencies in team abbreviations between Yahoo and nba_api.
            """
            TO_FIX = {'GS': "GSW", 'NY': "NYK", 'SA': "SAS", 'PHO': "PHX", 'NO': "NOP"}
            return TO_FIX.get(team, team)

        ODDS['team'] = ODDS['team'].apply(fix_abbreviations)
        ODDS['opp'] = ODDS['opp'].apply(fix_abbreviations)

        df = ODDS[['date', 'team', 'opp', 'is_home', 'total']][ODDS['is_home']]

        ### Step 3: Fetch Team Ratings from NBA API ###
        def fetch_team_ratings(location=None):
            """
            Fetches team ratings from the NBA API.
            If location is 'Home' or 'Road', retrieves home/road specific ratings.
            """
            return e.LeagueDashTeamStats(
                season="2024-25",
                measure_type_detailed_defense="Advanced",
                location_nullable=location
            ).get_data_frames()[0]

        # Fetch ratings for all, home, and road games
        BASIC_RATINGS = fetch_team_ratings()
        HOME_RATINGS = fetch_team_ratings("Home")
        ROAD_RATINGS = fetch_team_ratings("Road")

        # Select relevant columns
        for df_name, df_obj in [("BASIC_RATINGS", BASIC_RATINGS), ("HOME_RATINGS", HOME_RATINGS), ("ROAD_RATINGS", ROAD_RATINGS)]:
            df_obj['team'] = df_obj['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))
            df_obj['AVG_WIN_MARGIN'] = (df_obj['PACE'] / 100) * (df_obj['OFF_RATING'] - df_obj['DEF_RATING'])
            df_obj['AVG_TOTAL'] = (df_obj['PACE'] / 100) * (df_obj['OFF_RATING'] + df_obj['DEF_RATING'])

        ### Debugging: Check column names before merging ###
        print("Columns in df before merging:", df.columns.tolist())

        # Merge team stats into predictions DataFrame
        df = pd.merge(df, HOME_RATINGS[['team', 'AVG_WIN_MARGIN', 'AVG_TOTAL']], on='team', suffixes=['', '_home'])
        df = pd.merge(df, ROAD_RATINGS[['team', 'AVG_WIN_MARGIN', 'AVG_TOTAL']], left_on='opp', right_on='team', suffixes=['', '_road'])

        # Drop duplicate 'team' column from ROAD_RATINGS merge
        df = df.drop(columns=['team_road'])

        # Debugging: Check column names after merging
        print("Columns in df after merging:", df.columns.tolist())

        # Ensure required columns exist before calculations
        expected_columns = ['AVG_TOTAL_home', 'AVG_TOTAL_road', 'AVG_WIN_MARGIN_home', 'AVG_WIN_MARGIN_road']
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            print(f"⚠️ Error: Missing columns after merging: {missing_columns}")
            return  # Stop execution if required columns are missing

        ### Step 4: Make Predictions ###
        df['predicted_total'] = .5 * (df['AVG_TOTAL_home'] + df['AVG_TOTAL_road'])
        df['predicted_spread'] = -.5 * (df['AVG_WIN_MARGIN_home'] - df['AVG_WIN_MARGIN_road'])

        df['predicted_total'] = df['predicted_total'].apply(lambda x: round(2 * x, 0) / 2)
        df['predicted_spread'] = df['predicted_spread'].apply(lambda x: round(2 * x, 0) / 2)

        df['matchup'] = df.apply(lambda row: f"{row['team']} vs. {row['opp']}", axis=1)

        ### Step 5: Delete Old Predictions Before Inserting New Ones ###
        Prediction.objects.all().delete()

        ### Step 6: Save Predictions to Database ###
        for _, row in df.iterrows():
            print(f"Saving: {row['matchup']}, Yahoo Total: {row['total']}, Predicted Total: {row['predicted_total']}, Yahoo Spread: {row.get('team_spread', 'N/A')}, Predicted Spread: {row['predicted_spread']}")

            Prediction.objects.create(
                date=row["date"],
                matchup=row["matchup"],
                yahoo_total=row["total"],
                yahoo_spread=row["team_spread"],  
                predicted_total=row["predicted_total"],  
                predicted_spread=row["predicted_spread"],  
            )

        self.stdout.write(self.style.SUCCESS("Predictions successfully saved to the database!"))
