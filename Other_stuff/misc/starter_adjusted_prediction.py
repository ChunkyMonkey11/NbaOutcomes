""""
Example code to get predictions data

	Indiana versus Boston on 2024-12-27:

""""

import nba_api.stats.endpoints as e
import pandas as pd
import time

GAME_ID = "0022400420"
INDIANA_ID = 1610612754
BOSTON_ID = 1610612738

# Find out who started the game
BOXSCORE = e.BoxScoreTraditionalV2(game_id=GAME_ID).get_data_frames()[0]
time.sleep(0.5)
STARTERS = BOXSCORE[BOXSCORE['START_POSITION']!='']

indiana_starters = STARTERS[STARTERS['TEAM_ID'] == INDIANA_ID]['PLAYER_ID'].values.tolist()
boston_starters = STARTERS[STARTERS['TEAM_ID'] == BOSTON_ID]['PLAYER_ID'].values.tolist()

# get the prediction metrics for each team
IND_ONOFF = e.TeamPlayerOnOffDetails(team_id=INDIANA_ID,measure_type_detailed_defense="Advanced",location_nullable="Road").get_data_frames()
time.sleep(0.5)
BOS_ONOFF = e.TeamPlayerOnOffDetails(team_id=BOSTON_ID,measure_type_detailed_defense="Advanced",location_nullable="Home").get_data_frames()




# calculate indiana predictions for spread and total
E = IND_ONOFF
E = pd.concat([E[1],E[2]])
E = E[E['VS_PLAYER_ID'].isin(indiana_starters)].loc[:,['COURT_STATUS','VS_PLAYER_ID','OFF_RATING','DEF_RATING','PACE','MIN','GP']]
E['PREDICT_TOTAL'] = (E['PACE']/100)*(E['OFF_RATING']+E['DEF_RATING'])
E['PREDICT_spread'] = (E['PACE']/100)*(E['OFF_RATING']-E['DEF_RATING'])
E['MPG'] = E['MIN']/E['GP']
ON = E[E['COURT_STATUS'] == 'On']
OFF = E[E['COURT_STATUS'] == 'Off']
O = pd.merge(ON,OFF.loc[:,['VS_PLAYER_ID','PREDICT_TOTAL','PREDICT_spread']],on = 'VS_PLAYER_ID',suffixes = ['_ON','_OFF'])
O['predict_total'] = ((O['PREDICT_TOTAL_ON']*O['MPG']+(O['PREDICT_TOTAL_OFF']*(48-O['MPG']))))/48
O['predict_spread'] = ((O['PREDICT_spread_ON']*O['MPG']+(O['PREDICT_spread_OFF']*(48-O['MPG']))))/48
indiana_prediction_total =  (O['MPG']*O['predict_total']).sum()/O['MPG'].sum()
indiana_spread_prediction = (O['MPG']*O['predict_spread']).sum()/O['MPG'].sum()






# calculate boston predictions for spread and total
E = BOS_ONOFF
E = pd.concat([E[1],E[2]])
E = E[E['VS_PLAYER_ID'].isin(boston_starters)].loc[:,['COURT_STATUS','VS_PLAYER_ID','OFF_RATING','DEF_RATING','PACE','MIN','GP']]
E['PREDICT_TOTAL'] = (E['PACE']/100)*(E['OFF_RATING']+E['DEF_RATING'])
E['PREDICT_spread'] = (E['PACE']/100)*(E['OFF_RATING']-E['DEF_RATING'])
E['MPG'] = E['MIN']/E['GP']
ON = E[E['COURT_STATUS'] == 'On']
OFF = E[E['COURT_STATUS'] == 'Off']
O = pd.merge(ON,OFF.loc[:,['VS_PLAYER_ID','PREDICT_TOTAL','PREDICT_spread']],on = 'VS_PLAYER_ID',suffixes = ['_ON','_OFF'])
O['predict_total'] = ((O['PREDICT_TOTAL_ON']*O['MPG']+(O['PREDICT_TOTAL_OFF']*(48-O['MPG']))))/48
O['predict_spread'] = ((O['PREDICT_spread_ON']*O['MPG']+(O['PREDICT_spread_OFF']*(48-O['MPG']))))/48
boston_prediction_total = (O['MPG']*O['predict_total']).sum()/O['MPG'].sum()
boston_spread_prediction = (O['MPG']*O['predict_spread']).sum()/O['MPG'].sum()



# calculate spread and total final predictions
s = (boston_spread_prediction - indiana_spread_prediction)/2
t = (boston_prediction_total + indiana_prediction_total)/2

print("Predicted spread:")
print("The home team (Boston) by", round(s,2))
print("Predicted total:",round(t,2))