import nba_api.stats.endpoints as e
import pandas as pd

"""

PACE = POSSESSIONS / 48 MINUTES

OFF_RATING = POINTS SCORED / 100 POSSESSIONS
DEF_RATING = POINTS GIVEN UP / 100 POSSESSIONS

Total Points Predicted = .5*(OFF_RATING + OPPONENT DEF RATING)* 100 / PACE

"""

# get team IDS (nba_api specific)
LAL = 1610612747
ORL = 1610612753
teams = [ORL,LAL]


# Get Orlando Road data
A = e.TeamPlayerOnOffDetails(season = '2024-25',team_id = ORL,measure_type_detailed_defense="Advanced",date_from_nullable = "2024-10-31",date_to_nullable = "2024-11-21",location_nullable = "Road").get_data_frames()
#A=e.TeamPlayerOnOffDetails(season = '2024-25',team_id = ORL,measure_type_detailed_defense="Advanced",location_nullable="Road").get_data_frames()
O = pd.concat([A[1],A[2]])

# Look only at data with/without Kentavious Caldwell Pope (since he's out tonight)
POPE = O['VS_PLAYER_NAME'].str.contains("Pope")
O = O.loc[POPE]
print(O.loc[:,['TEAM_ABBREVIATION','COURT_STATUS','MIN','OFF_RATING','DEF_RATING','NET_RATING','PACE']])




# Get Lakers data
# Look only at Home Data
A = e.LeagueDashTeamStats(season="2024-25",measure_type_detailed_defense="Advanced",location_nullable="Home").get_data_frames()[0]
print(A[A['TEAM_ID'].isin(teams)].loc[:,['TEAM_NAME','GP','W','L','MIN','OFF_RATING','DEF_RATING','NET_RATING','PACE']].set_index("TEAM_NAME"))



# make estimates

ORL_DATA = O[O['COURT_STATUS'] == 'Off']
LAL_DATA = A[A['TEAM_ID'] == LAL] 

ORL_DATA = ORL_DATA.loc[:,['OFF_RATING','DEF_RATING','PACE']]
LAL_DATA = LAL_DATA.loc[:,['OFF_RATING','DEF_RATING','PACE']]

o1 = LAL_DATA['OFF_RATING'].values[0]
o2 = ORL_DATA['OFF_RATING'].values[0]

d1 = LAL_DATA['DEF_RATING'].values[0]
d2 = ORL_DATA['DEF_RATING'].values[0]

p1 = LAL_DATA['PACE'].values[0]
p2 = ORL_DATA['PACE'].values[0]

pace_estimate = (p1+p2)/2
PACE = pace_estimate

lakers_points_estimate = .5*(o1+d2)*100 / PACE
orlando_points_estimate = .5*(o2+d1)*100 / PACE

l = lakers_points_estimate
o = orlando_points_estimate

estimator = l+o

ot_estimator = .94*estimator +.06*(53/48)*estimator
print("Total Points: ", round(ot_estimator,2))

print("Lakers by: ",l-o)
