import nba_api.stats.endpoints as e
import pandas as pd

def get_regular(season = "2024-25",loc = None,season_type="Regular Season",game_segment = None):
	filepath_string="regular_season_data/"+season[:4]+"_get_regular_"+season_type[:3]+".csv"
	R=e.TeamGameLogs(season_nullable=season,location_nullable=loc,season_type_nullable=season_type,game_segment_nullable = game_segment).get_data_frames()[0]
	R = R.rename(columns = {"GAME_DATE":"date",'TEAM_ABBREVIATION':'team'})
	R['date'] = pd.to_datetime(R['date'])
	R=R.sort_values("date")
	R['rest'] = R.groupby("team")['date'].transform(lambda x: x.diff())
	R.to_csv(filepath_string,index=False)
	return R


get_regular()


