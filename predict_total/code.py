# %%
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.options.display.width = 0
pd.options.display.max_colwidth = 100



print("Gathering odds data")
	
season = '2016-17'
df = pd.read_csv("data/"+season+"NBAodds.csv",index_col = 0)
df['season'] = season
seasons = ['2017-18','2018-19','2020-21','2021-22','2022-23','2023-24','2024-25']
for season in seasons:
	DF = pd.read_csv("data/"+season+"NBAodds.csv",index_col = 0)
	DF['season'] = season
	df = pd.concat([df,DF])


df = df.rename(columns = {'points':'pts','points_opp':'pts_opp'})


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
 'POR',
 'SA',
 'SAS',
 'SAC',
 'TOR',
 'UTA',
 'WAS']

df = df[df['team'].isin(teams)]


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

df['team'] = df['team'].apply(lambda x: teams_dict_fix[x])


# get regular season data from nba_api
R = pd.read_csv("regular_season_data/2016_get_regular_Reg.csv")
cols = [c for c in R.columns.tolist() if 'RANK' not in c]
R = R.loc[:,cols]
R = R.rename(columns = {'TEAM_ABBREVIATION':"team",'GAME_DATE':"date",'DAYS_REST':'rest'})
R = R.drop(columns = ['TEAM_ID','TEAM_NAME'])

for season in ['2017','2018','2019','2020','2021','2022','2023','2024']:
	RR = pd.read_csv("regular_season_data/"+season+"_get_regular_Reg.csv")
	cols = [c for c in RR.columns.tolist() if 'RANK' not in c]
	RR = RR.loc[:,cols]
	RR = RR.rename(columns = {'TEAM_ABBREVIATION':"team",'GAME_DATE':"date",'DAYS_REST':'rest'})
	RR = RR.drop(columns = ['TEAM_ID','TEAM_NAME'])
	R = pd.concat([R,RR])

R = R.drop(columns = ['AVAILABLE_FLAG'])
R = R.rename(columns = {"rest":"DAYS_REST"})
R['date'] = pd.to_datetime(R['date'])
df['date'] = pd.to_datetime(df['date'])
P = pd.merge(df,R, on = ['date','team'], how = 'outer')
df = P

df = df.sort_values('date')

df.loc[df['MATCHUP'].isna(),'MATCHUP']=df.loc[df['MATCHUP'].isna(),'matchup']
df['opp'] = df['MATCHUP'].apply(lambda x: x.split(' ')[-1])

df['opp'] = df['opp'].apply(lambda x: teams_dict_fix[x])

df['is_home'] = df['MATCHUP'].str.contains("vs.")


def get_df(df):
	
	# %%
	df['date_full'] = pd.to_datetime(df['date_full'])
	#df = df.drop(columns = ['hits','errors','errors_opp','hits_opp'])
	df['win'] = (df['pts']-df['pts_opp'])>0
	df['total_pts'] = df['pts']+df['pts_opp']
	#df['is_home_prev'] = df.groupby('team')['is_home'].shift()
	
	# %%
	timezones = {
		'ATL': 'EST',  # Atlanta Hawks
		'BOS': 'EST',  # Boston Celtics
		'BKN': 'EST',  # Brooklyn Nets
		'CHA': 'EST',  # Charlotte Hornets
		'CHI': 'CST',  # Chicago Bulls
		'CLE': 'EST',  # Cleveland Cavaliers
		'DAL': 'CST',  # Dallas Mavericks
		'DEN': 'MST',  # Denver Nuggets
		'DET': 'EST',  # Detroit Pistons
		'GSW': 'PST',  # Golden State Warriors
		'HOU': 'CST',  # Houston Rockets
		'IND': 'EST',  # Indiana Pacers
		'LAC': 'PST',  # Los Angeles Clippers
		'LAL': 'PST',  # Los Angeles Lakers
		'MEM': 'CST',  # Memphis Grizzlies
		'MIA': 'EST',  # Miami Heat
		'MIL': 'CST',  # Milwaukee Bucks
		'MIN': 'CST',  # Minnesota Timberwolves
		'NJN': 'EST',  # New Jersey Nets
		'NOP': 'CST',  # New Orleans Pelicans
		'NYK': 'EST',  # New York Knicks
		'OKC': 'CST',  # Oklahoma City Thunder
		'ORL': 'EST',  # Orlando Magic
		'PHI': 'EST',  # Philadelphia 76ers
		'PHX': 'MST',  # Phoenix Suns
		'PHO': 'MST',  # Phoenix Suns
		'POR': 'PST',  # Portland Trail Blazers
		'SAC': 'PST',  # Sacramento Kings
		'SEA': 'PST',  # Seattle Supersonics
		'SAS': 'CST',  # San Antonio Spurs
		'TOR': 'EST',  # Toronto Raptors
		'UTA': 'MST',  # Utah Jazz
		'WAS': 'EST'   # Washington Wizards
	}
	
	teams = list(timezones.keys())
	df = df[df['team'].isin(teams)]
	#df = df[df['opp']!='ALS']
	
	
	# %%
	def do(s):
		team,opp = s['team'], s['opp']
		if s['is_home']:
			return timezones[team]
		else:
			return timezones[opp]
	df['game_timezone'] = df.apply(do,axis = 1)
	
	
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


df = get_df(df)






df['away_spread'] = df.groupby(['date','team','opp'])['away_spread'].transform(lambda x: x.ffill())
df['home_spread'] = df.groupby(['date','team','opp'])['home_spread'].transform(lambda x: x.ffill())
df['home_ml'] = df.groupby(['date','team','opp'])['home_ml'].transform(lambda x: x.ffill())
df['away_ml'] = df.groupby(['date','team','opp'])['away_ml'].transform(lambda x: x.ffill())
df['away_line'] = df.groupby(['date','team','opp'])['away_line'].transform(lambda x: x.ffill())
df['home_line'] = df.groupby(['date','team','opp'])['home_line'].transform(lambda x: x.ffill())
df['over_line'] = df.groupby(['date','team','opp'])['over_line'].transform(lambda x: x.ffill())
df['under_line'] = df.groupby(['date','team','opp'])['under_line'].transform(lambda x: x.ffill())
df['total'] = df.groupby(['date','team','opp'])['total'].transform(lambda x: x.ffill())

#
#
# WRANGLING
#
#

df['away_spread'] = df.groupby(['date','team','opp'])['away_spread'].transform(lambda x: x.bfill())
df['home_spread'] = df.groupby(['date','team','opp'])['home_spread'].transform(lambda x: x.bfill())
df['home_ml'] = df.groupby(['date','team','opp'])['home_ml'].transform(lambda x: x.bfill())
df['away_ml'] = df.groupby(['date','team','opp'])['away_ml'].transform(lambda x: x.bfill())
df['away_line'] = df.groupby(['date','team','opp'])['away_line'].transform(lambda x: x.bfill())
df['home_line'] = df.groupby(['date','team','opp'])['home_line'].transform(lambda x: x.bfill())
df['over_line'] = df.groupby(['date','team','opp'])['over_line'].transform(lambda x: x.bfill())
df['under_line'] = df.groupby(['date','team','opp'])['under_line'].transform(lambda x: x.bfill())
df['total'] = df.groupby(['date','team','opp'])['total'].transform(lambda x: x.bfill())


#
#
# END WRANGLING
#
#




#df = df.drop_duplicates(subset = ['date','team'])



# Fix this shit!



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







# NEW METHOD

#M = df.copy()
#A = ~M['home_ml'].isna()
#M = M.loc[A].groupby(['date','team']).first()
#M = M.reset_index()


























df['date_est'] = df['date_full'].dt.tz_convert(tz='US/Eastern')
df['date_pst'] = df['date_full'].dt.tz_convert(tz='US/Pacific')
df['date_cst'] = df['date_full'].dt.tz_convert(tz='US/Central')
df['date_mst'] = df['date_full'].dt.tz_convert(tz='US/Mountain')


df = df.drop_duplicates(subset = ['team','gid'])


def wrangle(df):
	# %%
	df = df.sort_values('date_full')
	
	# %%
	df['game_timezone_prev'] = df.groupby(['season','team'])['game_timezone'].shift()
	df['game_timezone_next'] = df.groupby(['season','team'])['game_timezone'].shift(-1)
	
	
	# %%
	df['rest'] = df.groupby(['season','team'])['date'].diff()
	df['rest_exact'] = df.groupby(['season','team'])['date_full'].diff()
	
	
	# %%
	df['is_home_prev'] = df.groupby(['season','team'])['is_home'].shift()
	df['change'] = df['is_home']!=df['is_home_prev']
	df['grouper'] = df.groupby(['season','team'])['change'].cumsum()
	df['t'] = 1
	df['streak'] = df.groupby(['season','team','grouper'])['t'].cumsum()
	df['opp_prev'] = df.groupby(['season','team'])['opp'].shift()
	
	# %%
	df.loc[~df['is_home'],('streak',)] = -df.loc[~df['is_home'],('streak',)]
	
	# %%
	df['streak_prev'] = df.groupby(['season','team'])['streak'].shift()
	df['streak_next'] = df.groupby(['season','team'])['streak'].shift(-1)
	
	return df




df = wrangle(df)


H = df[df['is_home']]
A = df[~df['is_home']]
P = pd.merge(H,A.loc[:,['gid','opp','rest','game_timezone_prev']],left_on = ['gid','team'],right_on = ['gid','opp'],suffixes = ['','_opp'])
Q = pd.merge(A,H.loc[:,['gid','opp','rest','game_timezone_prev']],left_on = ['gid','team'],right_on = ['gid','opp'],suffixes = ['','_opp'])
PP = pd.concat([P,Q]).sort_values('date')
PP = PP.drop(columns = ['opp_opp'])
df = PP



df['timeMST'] = df['date_mst'].dt.time
df['timeCST'] = df['date_cst'].dt.time
df['timeEST'] = df['date_est'].dt.time
df['timePST'] = df['date_pst'].dt.time

def do(s):
    timezone = s['game_timezone']
    return s['time'+timezone]

df['local_time'] = df.apply(do,axis = 1)

df['local_time_hours'] = df['local_time'].apply(lambda x :x.hour)+df['local_time'].apply(lambda x :x.minute)/60
df['game_type'] = pd.cut(df['local_time_hours'],bins = [0,12,18,24],labels = ['morning','afternoon','evening'])


timezones = {
		'ATL': 'EST',  # Atlanta Hawks
		'BOS': 'EST',  # Boston Celtics
		'BKN': 'EST',  # Brooklyn Nets
		'CHA': 'EST',  # Charlotte Hornets
		'CHI': 'CST',  # Chicago Bulls
		'CLE': 'EST',  # Cleveland Cavaliers
		'DAL': 'CST',  # Dallas Mavericks
		'DEN': 'MST',  # Denver Nuggets
		'DET': 'EST',  # Detroit Pistons
		'GSW': 'PST',  # Golden State Warriors
		'GS' : 'PST',
		'HOU': 'CST',  # Houston Rockets
		'IND': 'EST',  # Indiana Pacers
		'LAC': 'PST',  # Los Angeles Clippers
		'LAL': 'PST',  # Los Angeles Lakers
		'MEM': 'CST',  # Memphis Grizzlies
		'MIA': 'EST',  # Miami Heat
		'MIL': 'CST',  # Milwaukee Bucks
		'MIN': 'CST',  # Minnesota Timberwolves
		'NJN': 'EST',  # New Jersey Nets
		'NOP': 'CST',  # New Orleans Pelicans
		'NO': 'CST',
		'NYK': 'EST',  # New York Knicks
		'NY': 'EST',  # New York Knicks
		'OKC': 'CST',  # Oklahoma City Thunder
		'ORL': 'EST',  # Orlando Magic
		'PHI': 'EST',  # Philadelphia 76ers
		'PHX': 'MST',  # Phoenix Suns
		'PHO': 'MST',  # Phoenix Suns
		'POR': 'PST',  # Portland Trail Blazers
		'SAC': 'PST',  # Sacramento Kings
		'SEA': 'PST',  # Seattle Supersonics
		'SAS': 'CST',  # San Antonio Spurs
		'SA':"CST",
		'TOR': 'EST',  # Toronto Raptors
		'UTA': 'MST',  # Utah Jazz
		'WAS': 'EST'   # Washington Wizards
	}


df['team_local_timezone'] = df['team'].apply(lambda x: timezones[x])
df['opp_local_timezone'] = df['opp'].apply(lambda x: timezones[x])

















from datetime import time
comparison_time = time(12, 0)  # 12:00:00
c2 = time(14, 0)  # 12:00:00
c1 = time(12, 0)  # 12:00:00
df['before_noon'] = df['timePST'] < comparison_time
df['afternoon'] = (df['timePST']>c1)&(df['timePST']<c2)
df['primetime'] = df['timePST']>time(14,0)
df['time_type'] = None
df.loc[df['before_noon'],'time_type'] = 'morning'
df.loc[df['afternoon'],'time_type'] = 'afternoon'
df.loc[df['primetime'],'time_type'] = 'primetime'


df['weekday'] = df['date'].apply(lambda x: x.weekday())
df['month'] = df['date'].apply(lambda x: x.month)


















print("..making columns and cleaning the data...")






df = df.sort_values('date')







df['win'] = df['pts']>df['pts_opp']
df['lose'] = (df['pts']<df['pts_opp']).astype(int)
df['win'] = (df['pts']>df['pts_opp']).astype(int)


df['hundred_ml_LAST3'] = df.groupby(['season','team'])['hundred_ml'].transform(lambda x: x.rolling(3).mean().shift())
df['hundred_ml_LAST5'] = df.groupby(['season','team'])['hundred_ml'].transform(lambda x: x.rolling(5).mean().shift())





df['hundred_under_cumulative'] = df.groupby(['season','team'])['hundred_under'].transform(lambda x: x.cumsum().shift())
df['hundred_over_cumulative'] = df.groupby(['season','team'])['hundred_over'].transform(lambda x: x.cumsum().shift())
df['hundred_ml_cumulative'] = df.groupby(['season','team'])['hundred_ml'].transform(lambda x: x.cumsum().shift())
df['hundred_ml_fade_cumulative'] = df.groupby(['season','team'])['hundred_ml_fade'].transform(lambda x: x.cumsum().shift())




df['win_prev'] = df.groupby(['season','team'])['win'].shift()



timezones = {'PST':0,'MST':1,'CST':2,'EST':3}
df['gtcode'] = df['game_timezone'].apply(lambda x: timezones[x])

df['game_timezone_prev'] = df['game_timezone_prev'].fillna('')
timezones = {'PST':0,'MST':1,'CST':2,'EST':3,'':None}
df['gtcode_prev'] = df['game_timezone_prev'].apply(lambda x: timezones[x])
df['timezone_change'] = df['gtcode_prev']-df['gtcode']
H = df[df['is_home']]
A = df[~df['is_home']]
P = pd.merge(H,A.loc[:,['gid','opp','timezone_change','streak','win_prev']],left_on = ['gid','team'],right_on = ['gid','opp'],suffixes = ['','_opp'])
Q = pd.merge(A,H.loc[:,['gid','opp','timezone_change','streak','win_prev']],left_on = ['gid','team'],right_on = ['gid','opp'],suffixes = ['','_opp'])
PP = pd.concat([P,Q]).sort_values('date')
PP = PP.drop(columns = ['opp_opp'])
df = PP


df = df.sort_values('date')




df['pts_diff'] = df['pts'] - df['pts_opp']
df['pts_diff_prev'] = df.groupby(['season','team'])['pts_diff'].shift()
df['pts_diff_prev2'] = df.groupby(['season','team'])['pts_diff'].shift(2)
df['pts_diff_L2'] = df['pts_diff_prev'] + df['pts_diff_prev2']





df['pts_diff_bins_L2'] = pd.cut(df['pts_diff_L2'], bins = [-30,-6,0,6,30])


def do(s):
    if s['is_home']:
        if s['home_ml']<-110:
            return True
        elif s['home_ml']>0:
            return False
    else:
        if s['away_ml']<-110:
            return True
        elif s['away_ml']>0:
            return False
    return None
df['is_fav'] = df.apply(do, axis = 1)





def do(s):
    if s['is_home']:
        return s['PLUS_MINUS']+s['home_spread']
    else:
        return s['PLUS_MINUS']+s['away_spread']
df['DIFF'] = df.apply(do,axis = 1)






def do(ss):
    s = ss['cover_diff']
    if s == 0:
        return 0
    elif s > 0:
        return -100
    elif pd.isna(s) or (s == None):
        return None
    else:
        if ss['is_home']:
            line = ss['away_line']
        else:
            line = ss['home_line']
        if line > 0:
            return line
        else:
            return 100**2/(abs(line))
df['hundred_spread_fade'] = df.apply(do,axis = 1)






df = df.rename(columns = {'timezone_change':'tz_change'})
df = df.rename(columns = {'timezone_change_opp':'tz_change_opp'})































## NEW NEW 2024-12-01


def do(s):
    if s['is_home']:
        spread= s['home_spread']
    else:
        spread = s['away_spread']
    return spread

df['spread'] = df.apply(do,axis = 1)

def do(s):
    if s['is_home']:
        spread= s['home_spread']
    else:
        spread = s['away_spread']
    p = s['pts_diff']
    diff = p +spread
    if diff>0:
        return 1
    elif diff == 0:
        return 0
    elif diff < 0 :
        return -1
    else:
        return None

df['cover'] = df.apply(do,axis =1)

def do(s):
    total = s['total']
    points_scored = s['total_pts']
    diff = points_scored - total
    if diff>0:
        return 1
    elif diff == 0:
        return 0
    elif diff < 0 :
        return -1
    else:
        return None

df['oup_ats'] = df.apply(do, axis =1)

df['coverL2'] = df.groupby(['season','team'])['cover'].transform(lambda x: x.rolling(2).mean().shift())
df['coverL3'] = df.groupby(['season','team'])['cover'].transform(lambda x: x.rolling(3).mean().shift())
df['coverL5'] = df.groupby(['season','team'])['cover'].transform(lambda x: x.rolling(5).mean().shift())
df['coverL6'] = df.groupby(['season','team'])['cover'].transform(lambda x: x.rolling(6).mean().shift())
df['coverL7'] = df.groupby(['season','team'])['cover'].transform(lambda x: x.rolling(7).mean().shift())
df['cover_prev'] = df.groupby(['season','team'])['cover'].shift()




df['OVERL2'] = df.groupby(['season','team'])['oup_ats'].transform(lambda x: x.rolling(2).mean().shift())
df['OVERL3'] = df.groupby(['season','team'])['oup_ats'].transform(lambda x: x.rolling(3).mean().shift())
df['OVERL4'] = df.groupby(['season','team'])['oup_ats'].transform(lambda x: x.rolling(4).mean().shift())
df['OVERL5'] = df.groupby(['season','team'])['oup_ats'].transform(lambda x: x.rolling(5).mean().shift())


H = df[df['is_home']]
A = df[~df['is_home']]
P = pd.merge(H,A.loc[:,['date','opp','OVERL5','coverL2','coverL3','coverL5']],how = 'left',left_on = ['date','team'],right_on = ['date','opp'],suffixes = ['','_opp'])
Q = pd.merge(A,H.loc[:,['date','opp','OVERL5','coverL2','coverL3','coverL5']],how = 'left',left_on = ['date','team'],right_on = ['date','opp'],suffixes = ['','_opp'])
PP = pd.concat([P,Q]).sort_values('date')
PP = PP.drop(columns = 'opp_opp')

df = PP

df['date_str'] = df['date'].apply(lambda x: str(x)[:10])

df['tz_change'] = df['tz_change'].fillna(0).astype(int)
df['tz_change_opp'] = df['tz_change_opp'].fillna(0).astype(int)


df['streak'] = df['streak'].fillna(0).astype(int)
df['streak_prev'] = df['streak_prev'].fillna(0).astype(int)



#TODAY = df[df['date_str'] == '2024-12-01']
#print("TODAY has the following data")
#print(TODAY.loc[:,['date','team','MATCHUP','matchup','streak','streak_prev','tz_change','tz_change_opp','is_home']].sort_values(['is_home','streak','streak_prev']).set_index('date'))
#print(TODAY.loc[:,['date','team','MATCHUP','matchup','OVERL5','OVERL5_opp','is_home']].sort_values(['is_home','OVERL5','OVERL5_opp']).set_index('date'))






















### EXTRA
print("\n\n","now working on the totals prediction columns ...")


import nba_api.stats.endpoints as e

import time
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

seasons = ['2016-17','2017-18','2018-19','2020-21','2021-22','2022-23','2023-24','2024-25']
season = seasons[0]
T = e.TeamGameLogs(season_nullable = season,measure_type_player_game_logs_nullable="Advanced").get_data_frames()[0]
T = T.loc[:,cols]
T['opp'] = T['MATCHUP'].apply(lambda x: x.split(' ')[-1])
R = e.TeamGameLogs(season_nullable=season).get_data_frames()[0]
P = pd.merge(T,R.loc[:,['TEAM_ID','GAME_ID','PTS']], on = ['TEAM_ID','GAME_ID'])
P = pd.merge(P,R.loc[:,['TEAM_ABBREVIATION','GAME_ID','PTS']], left_on = ['opp','GAME_ID'],right_on = ['TEAM_ABBREVIATION','GAME_ID'], suffixes = ['','_opp'])
P['GAME_DATE']= pd.to_datetime(P['GAME_DATE'])
P = P.sort_values("GAME_DATE")
P = P.loc[:,['SEASON_YEAR','TEAM_ABBREVIATION','GAME_ID','GAME_DATE','MIN','OFF_RATING','DEF_RATING','PACE','POSS','PTS','PTS_opp']]
P['pts_cum'] = P.groupby("TEAM_ABBREVIATION")['PTS'].cumsum()
P['pts_opp_cum'] = P.groupby("TEAM_ABBREVIATION")['PTS_opp'].cumsum()
P['poss_cum'] = P.groupby("TEAM_ABBREVIATION")['POSS'].cumsum()
P['MIN_cum'] = P.groupby("TEAM_ABBREVIATION")['MIN'].cumsum()
P['ORTG'] = 100*P['pts_cum']/P['poss_cum']
P['DRTG'] = 100*P['pts_opp_cum']/P['poss_cum']

for season in seasons[1:]:
	print(season)
	T = e.TeamGameLogs(season_nullable = season,measure_type_player_game_logs_nullable="Advanced").get_data_frames()[0]
	T = T.loc[:,cols]
	T['opp'] = T['MATCHUP'].apply(lambda x: x.split(' ')[-1])
	R = e.TeamGameLogs(season_nullable=season).get_data_frames()[0]
	PP = pd.merge(T,R.loc[:,['TEAM_ID','GAME_ID','PTS']], on = ['TEAM_ID','GAME_ID'])
	PP = pd.merge(PP,R.loc[:,['TEAM_ABBREVIATION','GAME_ID','PTS']], left_on = ['opp','GAME_ID'],right_on = ['TEAM_ABBREVIATION','GAME_ID'], suffixes = ['','_opp'])
	PP['GAME_DATE']= pd.to_datetime(PP['GAME_DATE'])
	PP = PP.sort_values("GAME_DATE")
	PP = PP.loc[:,['SEASON_YEAR','TEAM_ABBREVIATION','GAME_ID','GAME_DATE','MIN','OFF_RATING','DEF_RATING','PACE','POSS','PTS','PTS_opp']]
	PP['pts_cum'] = PP.groupby("TEAM_ABBREVIATION")['PTS'].cumsum()
	PP['pts_opp_cum'] = PP.groupby("TEAM_ABBREVIATION")['PTS_opp'].cumsum()
	PP['poss_cum'] = PP.groupby("TEAM_ABBREVIATION")['POSS'].cumsum()
	PP['MIN_cum'] = PP.groupby("TEAM_ABBREVIATION")['MIN'].cumsum()
	PP['ORTG'] = 100*PP['pts_cum']/PP['poss_cum']
	PP['DRTG'] = 100*PP['pts_opp_cum']/PP['poss_cum']
	P = pd.concat([P,PP])
	time.sleep(0.4)





P['PACE'] = 48*P['poss_cum']/P['MIN_cum']
P['GAME_DATE'] = pd.to_datetime(P['GAME_DATE'])

P['date_str'] = P['GAME_DATE'].apply(lambda x: str(x)[:10])

PP = P.loc[:,['date_str','TEAM_ABBREVIATION','ORTG','DRTG','PACE']].copy()

PP = PP.rename(columns = {"TEAM_ABBREVIATION":"team"})




df['date'] = pd.to_datetime(df['date'])
df['date_str'] = df['date'].apply(lambda x: str(x)[:10])

X = pd.merge(df,PP, on = ['team','date_str'],how ='left')

df = X


df['PACE'] = df.groupby(['season','team'])['PACE'].shift()
df['ORTG'] = df.groupby(['season','team'])['ORTG'].shift()
df['DRTG'] = df.groupby(['season','team'])['DRTG'].shift()




df['date'] = pd.to_datetime(df['date'])
H = df[df['is_home']]
A = df[~df['is_home']]
P = pd.merge(H,A.loc[:,['date','opp','ORTG','DRTG','PACE']],left_on = ['date','team'],right_on = ['date','opp'],suffixes = ['','_opp'])
Q = pd.merge(A,H.loc[:,['date','opp','ORTG','DRTG','PACE']],left_on = ['date','team'],right_on = ['date','opp'],suffixes = ['','_opp'])
PP = pd.concat([P,Q]).sort_values('date')
PP = PP.drop(columns = ['opp_opp'])
df = PP



def do(s):
    #T1,T2 = A.loc[A.TEAM_NAME==m[0]],A.loc[A.TEAM_NAME==m[1]]
    ortg1,ortg2,drtg1,drtg2,pace1,pace2 = s.ORTG,s.ORTG_opp,s.DRTG,s.DRTG_opp,s.PACE,s.PACE_opp
    pace = (pace1+pace2)/2
    guess = (pace/100)*((ortg1+drtg2)/2+(ortg2+drtg1)/2)
    return round(guess,4)
df['total_guess'] = df.apply(do,axis = 1)



df['total_guess'] = df['total_guess'].apply(lambda x: round(2*x,0)/2)



import datetime
today = str(datetime.datetime.today())[:10]

TODAY = df[df['date_str'] == today]
#print(TODAY.loc[:,['date','team','MATCHUP','matchup','OVERL5','OVERL5_opp','total','total_guess','is_home']].sort_values(['is_home','OVERL5','OVERL5_opp']).set_index('date'))

T = TODAY.loc[:,['date','matchup','total','total_guess','is_home']].sort_values(['is_home']).set_index('date').drop(columns = 'is_home')
T = T.copy()
T = T.rename(columns = {'total':'yahoo_total','total_guess':'predicted_total'})

print(T)