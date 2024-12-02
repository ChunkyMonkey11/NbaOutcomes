import pandas as pd
import datetime
import time
import requests
import urllib
import json






def get_yahoo_json(sport,date):
	url = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues='+sport+'&date='+date
	r = requests.get(url)
	j = json.loads(r.text)
	return j['service']['scoreboard']

def get_yahoo_lines(sport,date):
	j = get_yahoo_json(sport,date)
	COLUMNS = ['book_name','away_ml','home_ml','away_spread','away_line','home_spread','home_line','total','over_line','under_line','date','date_full','team','matchup','opp']
	df= pd.DataFrame(columns = COLUMNS)
	if 'games' not in j.keys():
		print("Didn't Work")
		return
	games = list(j['games'].keys())
	for game in games:
		game_info = j['games'][game]
		homeId = game_info['home_team_id']
		home_team = j['teams'][homeId]['abbr']
		awayId = game_info['away_team_id']
		away_team = j['teams'][awayId]['abbr']
		status = game_info['status_description']
		print(date,home_team,away_team,status)
		if status == 'Postponed':
			print("\n Postponed:", home_team, " vs ", away_team, '\n')
			continue
		if status == 'Pregame':
			home_points = None
			away_points = None
			#home_shootout_points = None
			#away_shootout_points = None
		else:
			try:
				home_points = game_info['total_home_points']
				away_points = game_info['total_away_points']
				#home_shootout_points = game_info['total_home_shootout_points']
				#away_shootout_points = game_info['total_away_shootout_points']
			except:
				print(game,date, " no points")
				continue
		game_odds=j['gameodds'][game]
		if type(game_odds) != dict:
			print('game_odds is missing')
			continue
		game_odds = j['gameodds'][game]
		D=pd.DataFrame.from_dict(j['gameodds'][game], orient='index').set_index("book_id",drop=True).drop(columns = 'last_update')
		D['date'] = date
		D['date_full'] = game_info['start_time']
		D['team'] = home_team
		D['matchup'] = home_team +' vs. '+away_team 
		D['opp'] = away_team
		D['points'] = home_points
		#D['shootout_points'] = home_shootout_points
		D['points_opp'] = away_points
		#D['shootout_points_opp'] = away_shootout_points
		D['gid'] = game
		D.index.name = None
		df=pd.concat((df,D))
		E=pd.DataFrame.from_dict(j['gameodds'][game], orient='index').set_index("book_id",drop=True).drop(columns = 'last_update')
		E['date'] = date
		E['date_full'] = game_info['start_time']
		E['team'] = away_team
		E['matchup'] = away_team +' @ '+home_team 
		E['opp'] = home_team
		E['points'] = away_points
		#E['shootout_points'] = away_shootout_points
		E['points_opp'] = home_points
		#E['shootout_points_opp'] = home_shootout_points
		E['gid'] = game
		E.index.name = None
		df=pd.concat((df,E))
	return df







nba ={
    '2016-17': ('2016-10-25', '2017-04-12'),
    '2017-18': ('2017-10-17', '2018-04-11'),
    '2018-19': ('2018-10-16', '2019-04-10'),
    '2020-21': ('2020-12-22', '2021-05-16'),
    '2021-22': ('2021-10-19', '2022-04-10'),
    '2022-23': ('2022-10-18', '2023-04-09'),
    '2023-24': ('2023-10-24', '2024-04-14'),
    '2024-25': ('2024-10-22', '2024-11-03')
}


#season = input("What season?\n")
#L=list(pd.date_range(nba[season][0],nba[season][1]))
#L = [str(date)[:10] for date in L]
#sport,date = 'nba',L[0]
#df = get_yahoo_lines(sport,date)
#for date in L[1:]:
#	DF = get_yahoo_lines(sport,date)
#	df = pd.concat((df,DF))
#	time.sleep(.05)
#df.to_csv("data/"+str(season)+"NBAodds.csv")








season = '2024-25'
sport = 'nba'

df = pd.read_csv("data/"+season+"NBAodds.csv",index_col=0)

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')
last_download = df['date'].iloc[-1]
new_date = last_download - pd.to_timedelta(7, unit='days')
T = df[df['date']<new_date]
T.to_csv("data/"+season+"NBAodds.csv")



import datetime
today = str(datetime.datetime.today())[:10]



L=list(pd.date_range(new_date,today))
#L=list(pd.date_range(mlb_seasons[season][0],mlb_seasons[season][1]))
L = [str(date)[:10] for date in L]




date = L[0]
df = get_yahoo_lines(sport,date)
for date in L[1:]:
	DF = get_yahoo_lines(sport,date)
	df = pd.concat((df,DF))
	time.sleep(.05)



df.to_csv("data/"+season+"NBAodds.csv",header = False, mode = 'a')





