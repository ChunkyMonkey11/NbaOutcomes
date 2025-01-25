import requests
import time
import nba_api.stats.endpoints as e
from datetime import datetime
from nba_api.stats.static import teams

current_month_name = datetime.now().strftime("%B")

TEAMS = teams.get_teams()
team_ids = {}
for team in TEAMS:
    team_ids[team['abbreviation']] = team['id']



# URL for the NBA JSON data
url = "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2024/league/00_full_schedule.json"
# Fetch the JSON data from the website
response = requests.get(url)
schedule_data = response.json()


L = schedule_data['lscd']

for l in L:
	if l['mscd']['mon'] == current_month_name:
		M = l['mscd']

if not 'M' in locals():
	print("Mistaake!")


today = str(datetime.today())[:10]
TODAY = [m for m in M['g'] if m['gdte'] == today]

todays_games = {}
for game in TODAY:
    gid = game['gid']
    visit_id = game['v']['tid']
    home_id = game['h']['tid']
    visit = game['v']['ta']
    home = game['h']['ta']
    todays_games[gid] = [visit,visit_id,home,home_id,home+' vs. '+visit]


games = todays_games



def get_active_player_ids(visit,v_id,home,h_id,matchup):
	#
	# Returns a dictionary of player ids with minutes per game for each active player
	#
	# relevant column names
	cols = ['PLAYER_ID','PLAYER_NAME','GP','MIN','POSS']
	#
	# VISITOR
	#
	V = e.TeamPlayerDashboard(team_id=v_id,measure_type_detailed_defense="Advanced").get_data_frames()[1]
	V = V.loc[:,cols]
	V['MPG'] = V['MIN']/V['GP']
	V['POSS_PG'] = V['POSS']/V['GP']
	print("For today's game: "+matchup)
	print("Here is the roster for the visiting team "+visit+"'s current roster: \n")
	print(V)
	print('\n\n')
	visit_user_input_whos_out = input("Who's listed as OUT today for "+visit+"? Separate the player IDS by commas\n\n")
	OUT_VISIT = visit_user_input_whos_out.split(',')
	OUT_VISIT += [int(o) for o in OUT_VISIT]
	# SLICE OUT THE PLAYERS THAT ARE OUT
	V_ACTIVE_PLAYERS = V[~V['PLAYER_ID'].isin(OUT_VISIT)]
	# SAVE ONLY THE MINUTES PER GAME FOR EACH ACTIVE PLAYER
	#VISIT = V_ACTIVE_PLAYERS.set_index("PLAYER_ID")['MPG'].to_dict()
	VISIT = V_ACTIVE_PLAYERS.set_index("PLAYER_ID")['POSS_PG'].to_dict()
	#
	# HOME
	#
	H = e.TeamPlayerDashboard(team_id=h_id,measure_type_detailed_defense="Advanced").get_data_frames()[1]
	H = H.loc[:,cols]
	H['MPG'] = H['MIN']/H['GP']
	H['POSS_PG'] = H['POSS']/H['GP']
	print("Here is the roster for the visiting team "+home+"'s current roster: \n")
	print(H)
	print('\n\n')
	home_user_input_whos_out = input("Who's listed as OUT today for "+home+"? separate players by commas\n\n")
	print("making predictions...\n")
	OUT_HOME = home_user_input_whos_out.split(',')
	OUT_HOME += [int(o) for o in OUT_HOME]
	# SLICE OUT THE PLAYERS THAT ARE OUT
	H_ACTIVE_PLAYERS = H[~H['PLAYER_ID'].isin(OUT_HOME)]
	# SAVE ONLY THE MINUTES PER GAME FOR EACH ACTIVE PLAYER
	#HOME = H_ACTIVE_PLAYERS.set_index("PLAYER_ID")['MPG'].to_dict()
	HOME = H_ACTIVE_PLAYERS.set_index("PLAYER_ID")['POSS_PG'].to_dict()
	return VISIT,HOME








def get_prediction(v_id,h_id,VISIT,HOME):
	"""
	Returns a prediction based on who is actually playing. The weights are the sum of the minutes per game for each of the five man lineups
	
			e.g. lineup
	"""
	V_IDS = list(VISIT.keys())
	H_IDS = list(HOME.keys())
	V_ID_STRINGS = [str(v) for v in V_IDS]
	H_ID_STRINGS = [str(hh) for hh in H_IDS]
	#
	# VISIT
	#
	LINEUP_VISIT = e.TeamDashLineups(team_id=v_id,measure_type_detailed_defense="Advanced").get_data_frames()[1]
	LINEUP_VISIT = LINEUP_VISIT.loc[:,['GROUP_ID','GROUP_NAME','MIN','POSS','OFF_RATING','DEF_RATING','PACE']]
	def dodo(s):
		s = s.split('-')[1:-1]
		return set(s) <= set(V_ID_STRINGS)
	LINEUP_VISIT = LINEUP_VISIT[LINEUP_VISIT['GROUP_ID'].apply(dodo)]
	##
	## Only take data from lineups that have played at least 10 minutes together
	##
	LINEUP_VISIT = LINEUP_VISIT[LINEUP_VISIT['MIN']>=10]
	LINEUP_VISIT = LINEUP_VISIT.loc[:,['GROUP_ID','MIN','POSS','OFF_RATING','DEF_RATING','PACE']]
	LINEUP_VISIT['spread_predict'] = (LINEUP_VISIT['PACE']/100)*(LINEUP_VISIT['OFF_RATING']-LINEUP_VISIT['DEF_RATING'])
	LINEUP_VISIT['pts_predict'] = (LINEUP_VISIT['PACE']/100)*(LINEUP_VISIT['OFF_RATING']+LINEUP_VISIT['DEF_RATING'])
	#
	#
	def get_lineup_player_ids(s):
		return s.split('-')[1:-1]
	LINEUP_VISIT['player_ids'] = LINEUP_VISIT["GROUP_ID"].apply(get_lineup_player_ids)
	#
	#
	def get_lineup_MPG_sum(s):
		return sum([VISIT[int(p_id)] for p_id in s])
	LINEUP_VISIT['weights'] = LINEUP_VISIT['player_ids'].apply(get_lineup_MPG_sum)
	LINEUP_VISIT['weights'] = LINEUP_VISIT['weights']/LINEUP_VISIT['weights'].sum()
	#
	#
	SPREAD_VISIT = (LINEUP_VISIT['spread_predict']*LINEUP_VISIT['weights']).sum()
	POINTS_VISIT = (LINEUP_VISIT['pts_predict']*LINEUP_VISIT['weights']).sum()
	#
	# HOME
	#
	LINEUP_HOME = e.TeamDashLineups(team_id=h_id,measure_type_detailed_defense="Advanced").get_data_frames()[1]
	LINEUP_HOME = LINEUP_HOME.loc[:,['GROUP_ID','GROUP_NAME','MIN','POSS','OFF_RATING','DEF_RATING','PACE']]
	def dodo(s):
		s = s.split('-')[1:-1]
		return set(s) <= set(H_ID_STRINGS)
	LINEUP_HOME = LINEUP_HOME[LINEUP_HOME['GROUP_ID'].apply(dodo)]
	##
	## Only take data from lineups that have played at least 10 minutes together
	##
	LINEUP_HOME = LINEUP_HOME[LINEUP_HOME['MIN']>=10]
	LINEUP_HOME = LINEUP_HOME.loc[:,['GROUP_ID','MIN','POSS','OFF_RATING','DEF_RATING','PACE']]
	LINEUP_HOME['spread_predict'] = (LINEUP_HOME['PACE']/100)*(LINEUP_HOME['OFF_RATING']-LINEUP_HOME['DEF_RATING'])
	LINEUP_HOME['pts_predict'] = (LINEUP_HOME['PACE']/100)*(LINEUP_HOME['OFF_RATING']+LINEUP_HOME['DEF_RATING'])
	#
	#
	LINEUP_HOME['player_ids'] = LINEUP_HOME["GROUP_ID"].apply(get_lineup_player_ids)
	#
	#
	def get_lineup_MPG_sum(s):
		return sum([HOME[int(p_id)] for p_id in s])
	LINEUP_HOME['weights'] = LINEUP_HOME['player_ids'].apply(get_lineup_MPG_sum)
	LINEUP_HOME['weights'] = LINEUP_HOME['weights']/LINEUP_HOME['weights'].sum()
	#
	#
	SPREAD_HOME = (LINEUP_HOME['spread_predict']*LINEUP_HOME['weights']).sum()
	POINTS_HOME = (LINEUP_HOME['pts_predict']*LINEUP_HOME['weights']).sum()
	return SPREAD_HOME,SPREAD_VISIT,POINTS_HOME,POINTS_VISIT









def print_predictions(game):
	visit,v_id,home,h_id,matchup = game[0],game[1],game[2],game[3],game[4]
	VISIT,HOME = get_active_player_ids(visit,v_id,home,h_id,matchup)
	SPREAD_HOME,SPREAD_VISIT,POINTS_HOME,POINTS_VISIT = get_prediction(v_id,h_id,VISIT,HOME)
	s1,s2,p1,p2 = SPREAD_HOME,SPREAD_VISIT,POINTS_HOME,POINTS_VISIT
	ss = .5*(s1-s2)
	pp = .5*(p1+p2)
	if ss<0:
		print(matchup, ":",round(-2*ss,0)/2,round(2*pp,0)/2)
	else:
		print(matchup, ": ",round(2*ss,0)/2,round(2*pp,0)/2)



print("\nThese are today's games:\n")
for game in games.keys():
	print(game,":",games[game])
game_id = input("\nWhich game id do you want info for?\n\n")
game = games[game_id]

print_predictions(game)




