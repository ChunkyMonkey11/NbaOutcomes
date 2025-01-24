import nba_api.stats.endpoints as e
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime
import requests
import json
import time
import urllib
from django.core.management.base import BaseCommand
from peltzerspicks.models import Prediction  # Ensure this matches your app name






class Command(BaseCommand):
    help = "Fetch NBA predictions and store them in the database"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching NBA predictions...")
        
        
        ###
        
        ### Get Odds Data from yahoo
        
        ###
        
        
        
        def get_yahoo_json(sport,date):
            url = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues='+sport+'&date='+date
            r = requests.get(url)
            j = json.loads(r.text)
            return j['service']['scoreboard']
        
        def get_yahoo_lines(sport,date):
            j = get_yahoo_json(sport,date)
            #COLUMNS = ['book_name','away_ml','home_ml','away_spread','away_line','home_spread','home_line','total','over_line','under_line','date','date_full','team','opp']
            COLUMNS = ['book_name','away_ml','home_ml','away_spread','away_line','home_spread','home_line','total','over_line','under_line','date','team','opp']
            df= pd.DataFrame(columns = COLUMNS)
            if 'games' not in j.keys():
                print(date,": no games today")
                return None
            games = list(j['games'].keys())
            for game in games:
                # parse the json file for the relevant data
                game_info = j['games'][game]
                homeId = game_info['home_team_id']
                awayId = game_info['away_team_id']
                home_team = j['teams'][homeId]['abbr']
                away_team = j['teams'][awayId]['abbr']
                status = game_info['status_description']
                if status == 'Postponed':
                    print("\n Postponed:", home_team, " vs ", away_team, '\n')
                    continue
                game_odds=j['gameodds'][game]
                if type(game_odds) != dict:
                    print('game_odds is missing')
                    continue
                game_odds = j['gameodds'][game]
                D=pd.DataFrame.from_dict(j['gameodds'][game], orient='index').set_index("book_id",drop=True).drop(columns = 'last_update')
                D['date'] = date
                #D['date_full'] = game_info['start_time']
                D['team'] = home_team
                D['opp'] = away_team
                D['is_home'] = True
                D.index.name = None
                df=pd.concat((df,D))
                E=pd.DataFrame.from_dict(j['gameodds'][game], orient='index').set_index("book_id",drop=True).drop(columns = 'last_update')
                E['date'] = date
                #E['date_full'] = game_info['start_time']
                E['team'] = away_team
                E['opp'] = home_team
                E['is_home'] = False
                E.index.name = None
                df=pd.concat((df,E))
            return df
        
        
        
        def make_predictions():	
            sport = 'nba'
            today = str(datetime.today())[:10]
            ODDS = get_yahoo_lines(sport,today)
            
            
            ###
            
            ### END Get Odds Data from yahoo
            
            ###
            
            
            
            
            
            
            
            
            
            
            
            
            ###
            
            ### Merge Odds and Stats, Create Columns, and Predict Total
            
            ###
            
            
            
            
            # Fix Team Abbreviation Discrepancies between Yahoo and nba_api
            
            TEAMS = teams.get_teams()
            TEAM_ABBREVS = [team['abbreviation'] for team in TEAMS]
            
            TEAM_IDS = {}
            for team in TEAMS:
                TEAM_IDS[team['id']] = team['abbreviation']
            
            
            
            
            
            
            def fix_abbreviations(team):
                TO_FIX={'GS' :"GSW",
                        'NY' :"NYK",
                        'SA' :"SAS",
                        'PHO':"PHX",
                        'NO' :"NOP"}
                if team in TO_FIX.keys():
                    return TO_FIX[team]
                else:
                    return team
            
            ODDS['team'] = ODDS['team'].apply(fix_abbreviations)
            ODDS['opp'] = ODDS['opp'].apply(fix_abbreviations)
            ODDS = ODDS[ODDS['team'].isin(TEAM_ABBREVS)]
            
            
            def get_team_spread(s):
                if s['is_home']:
                    return s['home_spread']
                else:
                    return s['away_spread']
            ODDS['team_spread'] = ODDS.apply(get_team_spread,axis = 1)
            def get_team_ml(s):
                if s['is_home']:
                    return s['home_ml']
                else:
                    return s['away_ml']
            ODDS['team_ml'] = ODDS.apply(get_team_ml,axis=1)
            
            
            
            
            # Only take HOME data and certain columns
            df = ODDS.loc[:,['date','team','opp','is_home','team_ml','team_spread','total']]
            df = df[df['is_home']]
            
            df['matchup'] = df['team'] + ' vs. ' + df['opp']
            
            
            ###
            ### Get home/away offensive and defensive ratings
            ###
            
            
            HOME_RATINGS = e.LeagueDashTeamStats(season="2024-25",measure_type_detailed_defense="Advanced",location_nullable="Home").get_data_frames()[0]
            HOME_RATINGS = HOME_RATINGS.loc[:,['TEAM_ID','OFF_RATING','DEF_RATING','PACE']]
            HOME_RATINGS['team'] = HOME_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS[x])
            HOME_RATINGS['AVG_WIN_MARGIN'] = (HOME_RATINGS['PACE']/100)*(HOME_RATINGS['OFF_RATING']-HOME_RATINGS['DEF_RATING'])
            HOME_RATINGS['AVG_TOTAL'] = (HOME_RATINGS['PACE']/100)*(HOME_RATINGS['OFF_RATING']+HOME_RATINGS['DEF_RATING'])
            
            
            ROAD_RATINGS = e.LeagueDashTeamStats(season="2024-25",measure_type_detailed_defense="Advanced",location_nullable="Road").get_data_frames()[0]
            ROAD_RATINGS = ROAD_RATINGS.loc[:,['TEAM_ID','OFF_RATING','DEF_RATING','PACE']]
            ROAD_RATINGS['team'] = ROAD_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS[x])
            ROAD_RATINGS['AVG_WIN_MARGIN'] = (ROAD_RATINGS['PACE']/100)*(ROAD_RATINGS['OFF_RATING']-ROAD_RATINGS['DEF_RATING'])
            ROAD_RATINGS['AVG_TOTAL'] = (ROAD_RATINGS['PACE']/100)*(ROAD_RATINGS['OFF_RATING']+ROAD_RATINGS['DEF_RATING'])
            
            
            
            ###
            ### END Get home/away offensive and defensive ratings
            ###
            
            
            
            ### Make Home/Away Adjusted Predictions
            df = pd.merge(df,HOME_RATINGS.loc[:,['team','AVG_WIN_MARGIN','AVG_TOTAL']], on = 'team', suffixes = ['','_home_away_adjusted'])
            df = pd.merge(df,ROAD_RATINGS.loc[:,['team','AVG_WIN_MARGIN','AVG_TOTAL']], left_on = 'opp', right_on = 'team', suffixes = ['','_home_away_adjusted_opp'])
            df = df.drop(columns = ['team_home_away_adjusted_opp'])
            df['predicted_total_home_away_adjusted'] = .5*(df['AVG_TOTAL_home_away_adjusted']+df['AVG_TOTAL_home_away_adjusted_opp'])
            df['predicted_spread_home_away_adjusted'] = -.5*(df['AVG_WIN_MARGIN_home_away_adjusted']-df['AVG_WIN_MARGIN_home_away_adjusted_opp'])
            df['predicted_total_home_away_adjusted'] = df['predicted_total_home_away_adjusted'].apply(lambda x: round(2*x,0)/2)
            df['predicted_spread_home_away_adjusted'] = df['predicted_spread_home_away_adjusted'].apply(lambda x: round(2*x,0)/2)
            
            
            PREDICTIONS = df.loc[:,['date','matchup','total','team_spread','predicted_total_home_away_adjusted','predicted_spread_home_away_adjusted','is_home']].sort_values(['is_home']).set_index('date').drop(columns = 'is_home').copy()
            PREDICTIONS = PREDICTIONS.rename(columns = {'total':'yahoo_total','team_spread':'yahoo_spread'})
            PREDICTIONS.columns = ['matchup','yahoo_total','yahoo_spread','predicted_total','predicted_spread']
            PREDICTIONS.to_csv("Predictions_Home_Road_adjusted.csv",index=False)
            
            
            return PREDICTIONS


        ### Step 7: Delete Old Predictions Before Inserting New Ones ###
        Prediction.objects.all().delete()

        PREDICTIONS = make_predictions()
        ### Step 8: Save Predictions to Database ###
        for _, row in PREDICTIONS.iterrows():
            print(f"Saving: {row['matchup']}, Yahoo Total: {row['yahoo_total']}, Predicted Total: {row['predicted_total']}, Predicted Spread: {row['predicted_spread']}")

            Prediction.objects.create(
                date=row["date"],
                matchup=row["matchup"],
                yahoo_total=row["yahoo_total"],
                predicted_total=row["predicted_total"],
                predicted_spread=row["predicted_spread"],
            )

        self.stdout.write(self.style.SUCCESS("Predictions successfully saved to the database!"))




