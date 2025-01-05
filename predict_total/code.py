import nba_api.stats.endpoints as e
import pandas as pd
import datetime
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
		#print(date,home_team,away_team,status)
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









# Regular season start / end dates

nba ={
	'2016-17': ('2016-10-25', '2017-04-12'),
	'2017-18': ('2017-10-17', '2018-04-11'),
	'2018-19': ('2018-10-16', '2019-04-10'),
	'2020-21': ('2020-12-22', '2021-05-16'),
	'2021-22': ('2021-10-19', '2022-04-10'),
	'2022-23': ('2022-10-18', '2023-04-09'),
	'2023-24': ('2023-10-24', '2024-04-14'),
	'2024-25': ('2024-10-22', '2025-04-13')
}




# UNCOMMENT the code below to pull ALL odds for a particular PAST full season


#season = input("What season?\n")
#L=list(pd.date_range(nba[season][0],nba[season][1]))
#L = [str(date)[:10] for date in L]
#sport,date = 'nba',L[0]
#ODDS = get_yahoo_lines(sport,date)
#for date in L[1:]:
#	DF = get_yahoo_lines(sport,date)
#	ODDS = pd.concat((ODDS,DF))
#	time.sleep(.05)
#ODDS.to_csv("data/"+str(season)+"NBAodds.csv")





# UPDATE odds data for this season


season = '2024-25'
sport = 'nba'


# get data that was already previously pulled

ODDS = pd.read_csv("data/"+season+"NBAodds.csv",index_col=0)

ODDS['date'] = pd.to_datetime(ODDS['date'])
ODDS = ODDS.sort_values('date')

# delete the last few days from last download
last_download = ODDS['date'].iloc[-1]
new_date = last_download - pd.to_timedelta(3, unit='days')
T = ODDS[ODDS['date']<new_date]
T.to_csv("data/"+season+"NBAodds.csv")


# Get most recent odds data and update the csv file containing the odds



#tomorrow = datetime.datetime.today()+datetime.timedelta(days=1)
#tomorrow = str(tomorrow)[:10]
#L=list(pd.date_range(new_date,tomorrow))

today = str(datetime.datetime.today())[:10]
L=list(pd.date_range(new_date,today))
L = [str(date)[:10] for date in L]
date = L[0]
ODDS = get_yahoo_lines(sport,date)
for date in L[1:]:
	DF = get_yahoo_lines(sport,date)
	ODDS = pd.concat((ODDS,DF))
	time.sleep(.05)

# append the new data to  old csv file
ODDS.to_csv("data/"+season+"NBAodds.csv",header = False, mode = 'a')





###

### END Get Odds Data from yahoo

###































###

### Merge Odds and Stats, Create Columns, and Predict Total

###




print("Gathering odds data")
	
season = '2024-25'
ODDS = pd.read_csv("data/"+season+"NBAodds.csv",index_col = 0)
ODDS['season'] = season
ODDS = ODDS.rename(columns = {'points':'pts','points_opp':'pts_opp'})



# Fix Team Abbreviation Discrepancies between Yahoo and nba_api
teams = ['ATL',
 'BKN',
 'BOS',
 'CHA',
 'CHI',
 'CLE',
 'DAL',
 'DEN',
 'DET',
 'GS',
 'GSW',
 'HOU',
 'IND',
 'LAC',
 'LAL',
 'MEM',
 'MIA',
 'MIL',
 'MIN',
 'NO',
 'NOP',
 'NYK',
 'NY',
 'OKC',
 'ORL',
 'PHI',
 'PHO',
 'PHX',
 'POR',
 'SA',
 'SAS',
 'SAC',
 'TOR',
 'UTA',
 'WAS']

ODDS = ODDS[ODDS['team'].isin(teams)]


teams_dict_fix={'CLE':"CLE",
	 'POR':"POR",
	 'GS' :"GSW",
	 "GSW":"GSW",
	 'NY' :"NYK",
	 'UTA':"UTA",
	 'SA' :"SAS",
	 'SAS' :"SAS",
	 'PHI':"PHI",
	 'MEM':"MEM",
	 'MIL':'MIL',
	 'PHO':"PHX",
	 'PHX':'PHX',
	 'NO' :"NOP",
	 'NOP' :"NOP",
	 'NY':'NYK',
	 'NYK':"NYK",
	 'IND':'IND',
	 'ORL':'ORL',
	 'TOR':'TOR',
	 'BOS':'BOS',
	 'LAL':"LAL",
	 'DEN':"DEN",
	 'DET':"DET",
	 'OKC':"OKC",
	 'BKN':"BKN",
	 'MIA':"MIA",
	 'DAL':"DAL",
	 'HOU':"HOU",
	 'SAC':"SAC",
	 'CHA':"CHA",
	 'MIN':"MIN",
	 'ATL':"ATL",
	 'CHI':"CHI",
	 'WAS':"WAS",
	 'LAC':"LAC"}

ODDS['team'] = ODDS['team'].apply(lambda x: teams_dict_fix[x])











###

### Get 2024-25 GAME LOGS (e.g. Team PTS, AST, STL , etc)

###
season = '2024-25'
STATS = e.TeamGameLogs(season_nullable=season).get_data_frames()[0]
time.sleep(0.5)
IST_STATS = e.TeamGameLogs(season_nullable=season,season_type_nullable='IST').get_data_frames()[0]
STATS = pd.concat([STATS,IST_STATS])
STATS = STATS.rename(columns = {"GAME_DATE":"date",'TEAM_ABBREVIATION':'team'})
STATS['date'] = pd.to_datetime(STATS['date'])
STATS=STATS.sort_values("date")
STATS = STATS.reset_index(drop=True)
STATS = STATS.drop_duplicates(subset = ['GAME_ID','team'])
STATS['rest'] = STATS.groupby("team")['date'].transform(lambda x: x.diff())
cols = [c for c in STATS.columns.tolist() if 'RANK' not in c]
STATS = STATS.loc[:,cols]
STATS = STATS.rename(columns = {'TEAM_ABBREVIATION':"team",'GAME_DATE':"date",'DAYS_REST':'rest'})
STATS = STATS.drop(columns = ['TEAM_ID','TEAM_NAME','AVAILABLE_FLAG','rest'])



###

### END Get 2024-25 GAME LOGS (e.g. Team PTS, AST, STL , etc)

###








###

### MERGE ODDS and STATS DataFrame

###


# Make sure columns have same data type before MERGE
STATS['date'] = pd.to_datetime(STATS['date'])
ODDS['date'] = pd.to_datetime(ODDS['date'])  # set the data type 
MERGED = pd.merge(ODDS,STATS, on = ['date','team'], how = 'outer')

#rename it to df
df = MERGED

df = df.sort_values('date')


###

### END MERGE ODDS and STATS DataFrame

###







# Fix Matchup column issue
df.loc[df['MATCHUP'].isna(),'MATCHUP']=df.loc[df['MATCHUP'].isna(),'matchup']


# make an opponent column and fill it with the team abbreviation
df['opp'] = df['MATCHUP'].apply(lambda x: x.split(' ')[-1])

df['opp'] = df['opp'].apply(lambda x: teams_dict_fix[x])

# make a Boolean is_home column
df['is_home'] = df['MATCHUP'].str.contains("vs.")



# make a boolean win/loss column
df['win'] = df['PLUS_MINUS']>0

# make a total points column
df['total_pts'] = df['pts']+df['pts_opp']


print("..making columns and cleaning the data...")

















###

### MAKE PROFIT WIN/LOSS COLUMNS

###


"""
The function below will make the following columns


- hundred_ml :	 profit/loss from a 100$ wager on the moneyline on this team
- hundred_spread : profit/loss from a 100$ wager on the spread on this team

- hundred_ml_fade :	 profit/loss from a 100$ wager on the moneyline on the OPPONENT
- hundred_spread_fade : profit/loss from a 100$ wager on the spread on the OPPONENT

- hundred_over :  profit/loss from a 100$ wager on the OVER for the total points
- hundred_under : profit/loss from a 100$ wager on the UNDER for the total points

"""

def make_profit_win_loss_columns(df):
	# %%
	df = df.sort_values('date')
	
	# %%
	def hundred_ml(s):
		if s['is_home']:
			ml = s['home_ml']
		else:
			ml = s['away_ml']
		if pd.isna(ml):
			return 0
		if s['win']:
			if ml<0:
				return 100*(100/abs(ml))
			else:
				return ml
		else:
			return -100
	df['hundred_ml'] = df.apply(hundred_ml,axis = 1)
	
	# %%
	def hundred_ml_fade(s):
		if s['is_home']:
			ml = s['away_ml']
		else:
			ml = s['home_ml']
		if pd.isna(ml):
			return 0
		if not s['win']:
			if ml<0:
				return 100*(100/abs(ml))
			else:
				return ml
		else:
			return -100
	df['hundred_ml_fade'] = df.apply(hundred_ml_fade,axis = 1)
	
	def hundred_under(s):
		line = s['under_line']
		total = s['total']
		pts = s['total_pts']
		if (pd.isna(total)) or (pd.isna(pts)):
			return 0
		diff = pts - total
		if diff == 0:
			return 0
		elif diff > 0:
			return -100
		else:
			if line < 0:
				return 100*100/(abs(line))
			else:
				return line
	df['hundred_under'] = df.apply(hundred_under,axis = 1)
	
	
	
	def hundred_over(s):
		line = s['over_line']
		total = s['total']
		pts = s['total_pts']
		if (pd.isna(total)) or (pd.isna(pts)):
			return 0
		diff = pts - total
		if diff == 0:
			return 0
		elif diff < 0:
			return -100
		else:
			if line < 0:
				return 100*100/(abs(line))
			else:
				return line
	df['hundred_over'] = df.apply(hundred_over,axis = 1)
	
	df['pts_diff'] = df['pts'] - df['pts_opp']
	df.loc[df['is_home'],'cover_diff'] = df.loc[df['is_home'],'pts_diff']+df.loc[df['is_home'],'home_spread']
	df.loc[~df['is_home'],'cover_diff'] = df.loc[~df['is_home'],'pts_diff']+df.loc[~df['is_home'],'away_spread']
	def do(ss):
		s = ss['cover_diff']
		if s == 0:
			return 0
		elif s < 0:
			return -100
		elif pd.isna(s) or (s == None):
			return None
		else:
			if ss['is_home']:
				line = ss['home_line']
			else:
				line = ss['away_line']
			if line > 0:
				return line
			else:
				return 100**2/(abs(line))
	df['hundred_spread'] = df.apply(do,axis = 1)
	return df	




df = make_profit_win_loss_columns(df)



###

### END MAKE PROFIT WIN/LOSS COLUMNS

###























#
#
# MISCELLANEOUS WRANGLING
#
#


# Fix Columns that have missing Data by filling them in with odds source from another Row (a little MESSY)
# THE GOAL IS TO HAVE EXACTLY ONE ROW PER TEAM PER GAME IN THE DATASET
# THIS IS ONE WAY TO FILL IN MISSING ODDS DATA
# WOULD BE GOOD TO THINK OF A BETTER SOLUTION HERE

df['away_spread'] = df.groupby(['date','team','opp'])['away_spread'].transform(lambda x: x.ffill())
df['home_spread'] = df.groupby(['date','team','opp'])['home_spread'].transform(lambda x: x.ffill())
df['home_ml'] = df.groupby(['date','team','opp'])['home_ml'].transform(lambda x: x.ffill())
df['away_ml'] = df.groupby(['date','team','opp'])['away_ml'].transform(lambda x: x.ffill())
df['away_line'] = df.groupby(['date','team','opp'])['away_line'].transform(lambda x: x.ffill())
df['home_line'] = df.groupby(['date','team','opp'])['home_line'].transform(lambda x: x.ffill())
df['over_line'] = df.groupby(['date','team','opp'])['over_line'].transform(lambda x: x.ffill())
df['under_line'] = df.groupby(['date','team','opp'])['under_line'].transform(lambda x: x.ffill())
df['total'] = df.groupby(['date','team','opp'])['total'].transform(lambda x: x.ffill())



df['away_spread'] = df.groupby(['date','team','opp'])['away_spread'].transform(lambda x: x.bfill())
df['home_spread'] = df.groupby(['date','team','opp'])['home_spread'].transform(lambda x: x.bfill())
df['home_ml'] = df.groupby(['date','team','opp'])['home_ml'].transform(lambda x: x.bfill())
df['away_ml'] = df.groupby(['date','team','opp'])['away_ml'].transform(lambda x: x.bfill())
df['away_line'] = df.groupby(['date','team','opp'])['away_line'].transform(lambda x: x.bfill())
df['home_line'] = df.groupby(['date','team','opp'])['home_line'].transform(lambda x: x.bfill())
df['over_line'] = df.groupby(['date','team','opp'])['over_line'].transform(lambda x: x.bfill())
df['under_line'] = df.groupby(['date','team','opp'])['under_line'].transform(lambda x: x.bfill())
df['total'] = df.groupby(['date','team','opp'])['total'].transform(lambda x: x.bfill())





#df = df.drop_duplicates(subset = ['date','team'])



# Fix this shit!
# NOT SURE WHAT I'M DOING HERE ANYMORE


df.loc[df['SEASON_YEAR'].isna(),'SEASON_YEAR'] = df.loc[df['SEASON_YEAR'].isna(),'season']

# OLD METHOD
book_dict = {'2016-17':'BOVADA.LV','2017-18':'BOVADA.LV','2019-20':"COVID",'2018-19':'BOVADA.LV','2020-21':'Stats, LLC','2021-22':'BetMGM','2022-23':'BetMGM','2023-24':'BetMGM','2024-25':'BetMGM'}
#book_dict = {2016:'5dimes.eu',2017:'BOVADA.LV',2018:'BOVADA.LV',2019:'Stats, LLC',2022:'BetMGM',2023:'BetMGM',2024:'BetMGM'}
def do(s):
	book,year = s['book_name'],s['SEASON_YEAR']
	if (book_dict[year] == book) or (book == 'Missing') or (book_dict[year] == "COVID"):
		return True
	else:
		return False
N = df.copy()
N['to_use'] = N.apply(do,axis = 1)
N = N[N['to_use']]
N = N.drop(columns = ['to_use'])



#
#
# END MISCELLANEOUS WRANGLING
#
#





df = df.drop_duplicates(subset = ['team','gid'])


df = df.sort_values('date')


df['date_str'] = df['date'].apply(lambda x: str(x)[:10])













###
###
### GET ADVANCED STATS (OFFENSIVE RATING, DEFENSIVE RATING, PACE)
###
###

cols = ['SEASON_YEAR',
	 'MATCHUP',
	 'TEAM_ID',
	 'TEAM_ABBREVIATION',
	 'TEAM_NAME',
	 'GAME_ID',
	 'GAME_DATE',
	 'OFF_RATING',
	 'DEF_RATING',
	 'PACE',
	 'POSS',
	 'MIN']

seasons = ['2024-25']
season = seasons[0]
T = e.TeamGameLogs(season_nullable = season,measure_type_player_game_logs_nullable="Advanced").get_data_frames()[0]
TT = e.TeamGameLogs(season_nullable = season,season_type_nullable='IST',measure_type_player_game_logs_nullable="Advanced").get_data_frames()[0]
T = pd.concat([T,TT])
T = T.drop_duplicates(subset = ["GAME_ID","TEAM_ABBREVIATION"])


T = T.loc[:,cols]
T['opp'] = T['MATCHUP'].apply(lambda x: x.split(' ')[-1])
T['is_home'] = T['MATCHUP'].str.contains("vs.")

R = e.TeamGameLogs(season_nullable=season).get_data_frames()[0]
RR = e.TeamGameLogs(season_nullable=season,season_type_nullable='IST').get_data_frames()[0]
R = pd.concat([R,RR])

R = R.drop_duplicates(subset = ["GAME_ID","TEAM_ABBREVIATION"])

P = pd.merge(T,R.loc[:,['TEAM_ID','GAME_ID','PTS']], on = ['TEAM_ID','GAME_ID'])
P = pd.merge(P,R.loc[:,['TEAM_ABBREVIATION','GAME_ID','PTS']], left_on = ['opp','GAME_ID'],right_on = ['TEAM_ABBREVIATION','GAME_ID'], suffixes = ['','_opp'])

P['GAME_DATE']= pd.to_datetime(P['GAME_DATE'])
P = P.sort_values("GAME_DATE")
P = P.loc[:,['SEASON_YEAR','TEAM_ABBREVIATION','GAME_ID','GAME_DATE','is_home','MIN','OFF_RATING','DEF_RATING','PACE','POSS','PTS','PTS_opp']]



# Make cumulative sums columns for each team
P['pts_cumsum'] = P.groupby("TEAM_ABBREVIATION")['PTS'].cumsum()
P['pts_opp_cumsum'] = P.groupby("TEAM_ABBREVIATION")['PTS_opp'].cumsum()
P['poss_cumsum'] = P.groupby("TEAM_ABBREVIATION")['POSS'].cumsum()
P['MIN_cumsum'] = P.groupby("TEAM_ABBREVIATION")['MIN'].cumsum()






### HOME vs ROAD ADJUSTMENTS

# Make cumulative sums columns for each team adjusted for HOME/AWAY
P['pts_home_away_cumsum'] = P.groupby(["TEAM_ABBREVIATION",'is_home'])['PTS'].cumsum()
P['pts_home_away_opp_cumsum'] = P.groupby(["TEAM_ABBREVIATION",'is_home'])['PTS_opp'].cumsum()
P['poss_home_away_cumsum'] = P.groupby(["TEAM_ABBREVIATION",'is_home'])['POSS'].cumsum()
P['MIN_home_away_cumsum'] = P.groupby(["TEAM_ABBREVIATION",'is_home'])['MIN'].cumsum()


P['ORTG_home_away_running_avg'] = 100*P['pts_home_away_cumsum']/P['poss_home_away_cumsum']
P['DRTG_home_away_running_avg'] = 100*P['pts_home_away_opp_cumsum']/P['poss_home_away_cumsum']
P['PACE_home_away_running_avg'] = 48*P['poss_home_away_cumsum']/P['MIN_home_away_cumsum']

### END HOME vs ROAD ADJUSTMENTS




# Compute running averages
P['ORTG_running_avg'] = 100*P['pts_cumsum']/P['poss_cumsum']
P['DRTG_running_avg'] = 100*P['pts_opp_cumsum']/P['poss_cumsum']
P['PACE_running_avg'] = 48*P['poss_cumsum']/P['MIN_cumsum']



# fix date data type before merge
P['GAME_DATE'] = pd.to_datetime(P['GAME_DATE'])

P['date_str'] = P['GAME_DATE'].apply(lambda x: str(x)[:10])

# only take necessary columns
P = P.loc[:,['date_str','TEAM_ABBREVIATION','ORTG_running_avg','DRTG_running_avg','PACE_running_avg','ORTG_home_away_running_avg','DRTG_home_away_running_avg','PACE_home_away_running_avg']]
P = P.rename(columns = {"TEAM_ABBREVIATION":"team"})

ADVANCED_STATS = P.copy()



###
###
### END GET ADVANCED STATS (OFFENSIVE RATING, DEFENSIVE RATING, PACE)
###
###




###
###
### Merge with other data
###
###


df['date'] = pd.to_datetime(df['date'])
df['date_str'] = df['date'].apply(lambda x: str(x)[:10])

df = pd.merge(df,ADVANCED_STATS, on = ['team','date_str'],how ='left')


## IMPORTANT !!! 
## THESE ARE CUMULATIVE AVERAGES
# MUST BE SHIFTED TO AVOID DATA LEAKAGE!!!
df['PACE_running_avg'] = df.groupby(['season','team'])['PACE_running_avg'].shift()
df['ORTG_running_avg'] = df.groupby(['season','team'])['ORTG_running_avg'].shift()
df['DRTG_running_avg'] = df.groupby(['season','team'])['DRTG_running_avg'].shift()

# Home/Road Adjusted:
df['PACE_home_away_running_avg'] = df.groupby(['season','team','is_home'])['PACE_home_away_running_avg'].shift()
df['ORTG_home_away_running_avg'] = df.groupby(['season','team','is_home'])['ORTG_home_away_running_avg'].shift()
df['DRTG_home_away_running_avg'] = df.groupby(['season','team','is_home'])['DRTG_home_away_running_avg'].shift()



# fix date data type before merge
df['date'] = pd.to_datetime(df['date'])
H = df[df['is_home']]
A = df[~df['is_home']]
# get opponent averages
P = pd.merge(H,A.loc[:,['date','opp','ORTG_running_avg','DRTG_running_avg','PACE_running_avg','ORTG_home_away_running_avg','DRTG_home_away_running_avg','PACE_home_away_running_avg']],left_on = ['date','team'],right_on = ['date','opp'],suffixes = ['','_opp'])
Q = pd.merge(A,H.loc[:,['date','opp','ORTG_running_avg','DRTG_running_avg','PACE_running_avg','ORTG_home_away_running_avg','DRTG_home_away_running_avg','PACE_home_away_running_avg']],left_on = ['date','team'],right_on = ['date','opp'],suffixes = ['','_opp'])
PP = pd.concat([P,Q]).sort_values('date')
PP = PP.drop(columns = ['opp_opp'])
df = PP



###
###
### END Merge with other data
###
###
























print("\n\n","now working on the totals prediction columns ...")


###
###
### MAKE PREDICTIONS
###
###




def make_prediction(s):
	# make estimates
	ortg1,drtg1,pace1 = s['ORTG_running_avg'],s['DRTG_running_avg'],s['PACE_running_avg']
	ortg2,drtg2,pace2 = s['ORTG_running_avg_opp'],s['DRTG_running_avg_opp'],s['PACE_running_avg_opp']
	pace = (pace1+pace2)/2
	spread_1 = (pace/100)*(ortg1-drtg1) 
	spread_2 = (pace/100)*(ortg2-drtg2) 
	total_1 = (pace/100)*(ortg1+drtg1) 
	total_2 = (pace/100)*(ortg2+drtg2) 
	spread_guess = .5*(spread_1-spread_2)
	over_under_guess = .5*(total_1+total_2)
	return (-spread_guess,over_under_guess)

df['predictions'] = df.apply(make_prediction,axis = 1)
df['predicted_spread'] = df['predictions'].apply(lambda x: x[0])
df['predicted_total'] = df['predictions'].apply(lambda x: x[1])
df = df.drop(columns = 'predictions')
df['predicted_total'] = df['predicted_total'].apply(lambda x: round(2*x,0)/2)
df['predicted_spread'] = df['predicted_spread'].apply(lambda x: round(2*x,0)/2)


###
###
### END MAKE PREDICTIONS
###
###



















###
###
### MAKE HOME vs ROAD ADJUSTED PREDICTIONS
###
###

def make_prediction(s):
	# make estimates
	ortg1,drtg1,pace1 = s['ORTG_home_away_running_avg'],s['DRTG_home_away_running_avg'],s['PACE_home_away_running_avg']
	ortg2,drtg2,pace2 = s['ORTG_home_away_running_avg_opp'],s['DRTG_home_away_running_avg_opp'],s['PACE_home_away_running_avg_opp']
	pace = (pace1+pace2)/2
	spread_1 = (pace/100)*(ortg1-drtg1) 
	spread_2 = (pace/100)*(ortg2-drtg2) 
	total_1 = (pace/100)*(ortg1+drtg1) 
	total_2 = (pace/100)*(ortg2+drtg2) 
	spread_guess = .5*(spread_1-spread_2)
	over_under_guess = .5*(total_1+total_2)
	return (-spread_guess,over_under_guess)

df['predictions_home_away'] = df.apply(make_prediction,axis = 1)
df['predicted_spread_home_away_adjusted'] = df['predictions_home_away'].apply(lambda x: x[0])
df['predicted_total_home_away_adjusted'] = df['predictions_home_away'].apply(lambda x: x[1])
df = df.drop(columns = 'predictions_home_away')
df['predicted_total_home_away_adjusted'] = df['predicted_total_home_away_adjusted'].apply(lambda x: round(2*x,0)/2)
df['predicted_spread_home_away_adjusted'] = df['predicted_spread_home_away_adjusted'].apply(lambda x: round(2*x,0)/2)


###
###
### END MAKE HOME vs ROAD ADJUSTED PREDICTIONS
###
###
























###
###
### Make team_spread column
###
###



def return_spread(row):
    away_spread = row['away_spread']
    home_spread = row['home_spread']
    if row['is_home'] == True:
        return home_spread
    else:
        return away_spread
df['team_spread'] = df.apply(return_spread, axis = 1)


###
###
### END Make team_spread column
###
###



###
###
### Make favored_team column
###
###
def determine_favored_team(row):
    """
    Determines the favored team based on the spread.
    Negative spread means the team is favored.
    """
    if row['team_spread'] < 0:
        return row['team']
    elif row['team_spread'] > 0:
        return row['opp']
    else:
        return "Neither"

df['favored_team'] = df.apply(determine_favored_team, axis=1)







###
###
### Print data to User
###
###



print("Predictions:")

today = str(datetime.datetime.today())[:10]

TODAY = df[df['date_str'] == today]

TODAY = TODAY[TODAY['is_home']]



PREDICTIONS1 = TODAY.loc[:,['date','matchup','total','team_spread','predicted_total','predicted_spread','is_home','favored_team']].sort_values(['is_home']).set_index('date').drop(columns = 'is_home')
PREDICTIONS1 = PREDICTIONS1.copy()
PREDICTIONS1 = PREDICTIONS1.rename(columns = {'total':'yahoo_total','team_spread':'yahoo_spread'})
#print(PREDICTIONS1)



print("Predictions home / road adjusted predictions:")

PREDICTIONS2 = TODAY.loc[:,['date','matchup','total','team_spread','predicted_total_home_away_adjusted','predicted_spread_home_away_adjusted','is_home','favored_team']].sort_values(['is_home']).set_index('date').drop(columns = 'is_home')
PREDICTIONS2 = PREDICTIONS2.copy()
PREDICTIONS2 = PREDICTIONS2.rename(columns = {'total':'yahoo_total','team_spread':'yahoo_spread'})
#print(PREDICTIONS2)



T1 = PREDICTIONS1
T2 = PREDICTIONS2
T2.columns = ['matchup','yahoo_total','yahoo_spread','predicted_total','predicted_spread','favored_team']


print("Basic predictions:")
print(T1)

print("\n\n Home/Road Adjusted:")
print(T2)

###
###
### END Print data to User
###
###

# Create CSV Files for website to pull from
T1.to_csv("Predictions_Basic.csv",index=False)
T2.to_csv("Predictions_Home_Road_adjusted.csv",index=False)

