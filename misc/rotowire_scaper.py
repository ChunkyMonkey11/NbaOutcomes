import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import nba_api.stats.endpoints as e
from nba_api.stats.static import players



date = str(datetime.datetime.today())[:10]

# URL of the NBA lineups page
url = 'https://www.rotowire.com/basketball/nba-lineups.php'

# Send a GET request to the URL
response = requests.get(url)
response.raise_for_status()  # Raise an error for bad status codes

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize a list to store the lineup data
lineup_data = []

# Find all game containers on the page
games = soup.find_all('div', class_='lineup__teams')
lineups = soup.find_all('div', class_='lineup__main')






def get_game_info(game,lineup_container):
	# get team names
	away_team_info = game.find('a', class_='lineup__team is-visit')
	away_team_name = away_team_info.find("div").text
	home_team_info = game.find('a', class_='lineup__team is-home')
	home_team_name = home_team_info.find("div").text
	away_matchup = away_team_name + " @ " + home_team_name
	home_matchup = home_team_name + " vs. " + away_team_name
	# create team containers
	away_team_container = lineup_container.find("ul",class_ ="lineup__list is-visit")
	home_team_container = lineup_container.find("ul",class_ ="lineup__list is-home")
	# get lineup statuses (expected or confirmed lineup)
	away_status = away_team_container.find("li").text.strip()
	home_status = home_team_container.find("li").text.strip()
	# get player containers
	away_players_container = away_team_container.find_all("li", class_=lambda value: value and value.startswith("lineup__player"))
	home_players_container = home_team_container.find_all("li", class_=lambda value: value and value.startswith("lineup__player"))
	# fill up data
	data = []	
	for player in away_players_container:
		position = player.find("div", class_ = "lineup__pos").text
		name = player.find("a").text
		injury = player.find("span", class_ = "lineup__inj")
		if injury:
			injury = injury.text
		else:
			injury = ""
		data.append([date,away_matchup,away_team_name, away_status,name,position,injury])	
	for player in home_players_container:
		position = player.find("div", class_ = "lineup__pos").text
		name = player.find("a").text
		injury = player.find("span", class_ = "lineup__inj")
		if injury:
			injury = injury.text
		else:
			injury = ""
		data.append([date,home_matchup,home_team_name, home_status,name,position,injury])
	return data





full_data = []

num_games = len(games)
for i in range(num_games):
	# Extract the team names
	game = games[i]
	lineup_container = lineups[i]
	data = get_game_info(game,lineup_container)
	full_data += data


# Create a DataFrame from the collected data
df = pd.DataFrame(full_data, columns=['date', 'matchup','team','status', 'player_name','player_position','player_injury'])

# Display the DataFrame
print(df)













		



active_players = players.get_active_players()

def do(s):
	team = s['team']
	p_name = s['player_name']
	def by_partial_name(first_initial, last_name):
		matches = []
		for player in active_players:
			first_name = player['first_name'].lower()
			last_name_candidate = player['last_name'].lower()
			if first_name.startswith(first_initial) and ((last_name in last_name_candidate) or (last_name_candidate in last_name)):
					matches.append({'id': player['id'], 'full_name': player['full_name']})
		return matches
	if '.' not in p_name:
		for player in active_players:
			if player['full_name'].lower() == p_name.lower():
				return player['id']
		return None
	else:
		name = p_name.split('. ')
		first_initial = name[0].lower()
		last_name = name[-1].lower()
		matching_players = by_partial_name(first_initial, last_name)
		if len(matching_players) == 0:
			return None
		elif len(matching_players)==1:
			player = matching_players[0]
			return player['id']
		else:
			for player in matching_players:
				p_id = player['id']
				E = e.PlayerProfileV2(player_id=p_id).get_data_frames()[0]
				t = E[E['SEASON_ID'] == '2024-25']['TEAM_ABBREVIATION'].iloc[0]
				if t == team:
					return int(p_id)
			return None


#df['nba_api_id'] = df.apply(do,axis = 1)














