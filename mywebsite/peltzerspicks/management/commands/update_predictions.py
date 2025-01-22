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

        TEAMS = teams.get_teams()
        TEAM_IDS = {team['id']: team['abbreviation'] for team in TEAMS}

        def fix_abbreviations(team):
            TO_FIX = {'GS': "GSW", 'NY': "NYK", 'SA': "SAS", 'PHO': "PHX", 'NO': "NOP"}
            return TO_FIX.get(team, team)

        ODDS['team'] = ODDS['team'].apply(fix_abbreviations)
        ODDS['opp'] = ODDS['opp'].apply(fix_abbreviations)

        df = ODDS[['date', 'team', 'opp', 'is_home', 'total']][ODDS['is_home']]

        BASIC_RATINGS = e.LeagueDashTeamStats(season="2024-25", measure_type_detailed_defense="Advanced").get_data_frames()[0]
        BASIC_RATINGS['team'] = BASIC_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))

        HOME_RATINGS = e.LeagueDashTeamStats(season="2024-25", measure_type_detailed_defense="Advanced",
                                             location_nullable="Home").get_data_frames()[0]
        HOME_RATINGS['team'] = HOME_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))

        ROAD_RATINGS = e.LeagueDashTeamStats(season="2024-25", measure_type_detailed_defense="Advanced",
                                             location_nullable="Road").get_data_frames()[0]
        ROAD_RATINGS['team'] = ROAD_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS.get(x, 'Unknown'))

        df = pd.merge(df, HOME_RATINGS[['team', 'OFF_RATING', 'DEF_RATING', 'PACE']], on='team')
        df = pd.merge(df, ROAD_RATINGS[['team', 'OFF_RATING', 'DEF_RATING', 'PACE']], left_on='opp', right_on='team',
                      suffixes=['', '_opp'])
        df = df.drop(columns=['team_opp'])

        df['predicted_total'] = 0.5 * (df['OFF_RATING'] + df['OFF_RATING_opp'])
        df['predicted_spread'] = -0.5 * (df['DEF_RATING'] - df['DEF_RATING_opp'])
        df['predicted_total'] = df['predicted_total'].apply(lambda x: round(2 * x, 0) / 2)
        df['predicted_spread'] = df['predicted_spread'].apply(lambda x: round(2 * x, 0) / 2)
        df['matchup'] = df.apply(lambda row: f"{row['team']} vs. {row['opp']}", axis=1)

        for _, row in df.iterrows():
            Prediction.objects.create(
                date=row["date"],
                matchup=row["matchup"],
                yahoo_total=row["total"],
                yahoo_spread=None,  # Adjust if needed
                predicted_total=row["predicted_total"],
                predicted_spread=row["predicted_spread"],
                favored_team=None
            )

        self.stdout.write(self.style.SUCCESS("Predictions successfully saved to the database!"))
