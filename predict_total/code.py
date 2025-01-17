import nba_api.stats.endpoints as e
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime
import time
import requests
import urllib
import json



pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.options.display.width = 0
pd.options.display.max_colwidth = 20

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
		return
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



def update_csv_files():	
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
	
	
	
	
	###
	### Get Basic offensive and defensive ratings
	###
	
	
	BASIC_RATINGS = e.LeagueDashTeamStats(season="2024-25",measure_type_detailed_defense="Advanced").get_data_frames()[0]
	BASIC_RATINGS = BASIC_RATINGS.loc[:,['TEAM_ID','OFF_RATING','DEF_RATING','PACE']]
	BASIC_RATINGS['team'] = BASIC_RATINGS['TEAM_ID'].apply(lambda x: TEAM_IDS[x])
	BASIC_RATINGS['AVG_WIN_MARGIN'] = (BASIC_RATINGS['PACE']/100)*(BASIC_RATINGS['OFF_RATING']-BASIC_RATINGS['DEF_RATING'])
	BASIC_RATINGS['AVG_TOTAL'] = (BASIC_RATINGS['PACE']/100)*(BASIC_RATINGS['OFF_RATING']+BASIC_RATINGS['DEF_RATING'])
	
	###
	### END Get Basic offensive and defensive ratings
	###
	
	
	
	
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
	
	
	
	###
	### Make BASIC Predictions
	###
	
	
	df = pd.merge(df,BASIC_RATINGS.loc[:,['team','AVG_WIN_MARGIN','AVG_TOTAL']], on = 'team', suffixes = ['','_team'])
	df = pd.merge(df,BASIC_RATINGS.loc[:,['team','AVG_WIN_MARGIN','AVG_TOTAL']], left_on = 'opp', right_on = 'team', suffixes = ['','_opp'])
	df = df.drop(columns = ['team_opp'])
	
	
	
	df['predicted_total'] = .5*(df['AVG_TOTAL']+df['AVG_TOTAL_opp'])
	df['predicted_spread'] = -.5*(df['AVG_WIN_MARGIN']-df['AVG_WIN_MARGIN_opp'])
	
	
	# round up to the nearest half point
	df['predicted_total'] = df['predicted_total'].apply(lambda x: round(2*x,0)/2)
	df['predicted_spread'] = df['predicted_spread'].apply(lambda x: round(2*x,0)/2)
	
	
	###
	### END Make BASIC Predictions
	###
	
	###
	### Make Home/Away Adjusted Predictions
	###
	
	
	df = pd.merge(df,HOME_RATINGS.loc[:,['team','AVG_WIN_MARGIN','AVG_TOTAL']], on = 'team', suffixes = ['','_home_away_adjusted'])
	df = pd.merge(df,ROAD_RATINGS.loc[:,['team','AVG_WIN_MARGIN','AVG_TOTAL']], left_on = 'opp', right_on = 'team', suffixes = ['','_home_away_adjusted_opp'])
	df = df.drop(columns = ['team_home_away_adjusted_opp'])
	
	
	
	df['predicted_total_home_away_adjusted'] = .5*(df['AVG_TOTAL_home_away_adjusted']+df['AVG_TOTAL_home_away_adjusted_opp'])
	df['predicted_spread_home_away_adjusted'] = -.5*(df['AVG_WIN_MARGIN_home_away_adjusted']-df['AVG_WIN_MARGIN_home_away_adjusted_opp'])
	
	
	
	
	df['predicted_total_home_away_adjusted'] = df['predicted_total_home_away_adjusted'].apply(lambda x: round(2*x,0)/2)
	df['predicted_spread_home_away_adjusted'] = df['predicted_spread_home_away_adjusted'].apply(lambda x: round(2*x,0)/2)
	
	
	###
	### END Make Home/Away Adjusted Predictions
	###
	
	
	
	
	
	
	
	def make_matchup_col(row):
		if row['is_home']:
			return row['team'] + ' vs. ' + row['opp']
		else:
			return row['team'] + ' @ ' + row['opp']
	
	df['matchup'] = df.apply(make_matchup_col, axis = 1)
	
	
	
	
	
	
	
	
	
	
	###
	###
	### Print data to User
	###
	###
	
	PREDICTIONS1 = df.loc[:,['date','matchup','total','team_spread','predicted_total','predicted_spread','is_home']].sort_values(['is_home']).set_index('date').drop(columns = 'is_home').copy()
	PREDICTIONS1 = PREDICTIONS1.rename(columns = {'total':'yahoo_total','team_spread':'yahoo_spread'})
	
	PREDICTIONS2 = df.loc[:,['date','matchup','total','team_spread','predicted_total_home_away_adjusted','predicted_spread_home_away_adjusted','is_home']].sort_values(['is_home']).set_index('date').drop(columns = 'is_home').copy()
	PREDICTIONS2 = PREDICTIONS2.rename(columns = {'total':'yahoo_total','team_spread':'yahoo_spread'})
	
	
	T1 = PREDICTIONS1
	T2 = PREDICTIONS2
	
	T2.columns = ['matchup','yahoo_total','yahoo_spread','predicted_total','predicted_spread']
	
	
	print("Basic predictions:")
	print(T1)
	
	print("\n\n Home/Road Adjusted:")
	print(T2)
	
	
	###
	###
	### END Print data to User
	###
	###
	
	
	
	T1.to_csv("Predictions_Basic.csv",index=False)
	T2.to_csv("Predictions_Home_Road_adjusted.csv",index=False)
	



update_csv_files()








