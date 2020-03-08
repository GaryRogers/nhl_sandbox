#%% [markdown]
# # NHL 2019-2020 Season data notebook
#
# Notebook for exploring the NHL API season API data

#%% [code]

import pandas as pd
from pandas.io.json import json_normalize
import json
from typing import List

filename = 'api_data/season_20192020.json'

with open(filename) as json_file:
    season_data = json.load(json_file)

# %% [markdown]
# Initial load of season dates

#%% [code]

dates = pd.DataFrame.from_dict(season_data['dates'])
dates.set_index('date', inplace=True)

dates.head(20)

# %% [markdown]
# Flatten dates/games into a simple table

# %%

flat_games = []
teams = []

for i, d in dates.iterrows():
    for g in d['games']:
        tempObject = { "date": i, "game_id": g['gamePk'] }
        tempObject['away_team'] = g['teams']['away']['team']['name']
        tempObject['home_team'] = g['teams']['home']['team']['name']
        if not tempObject['away_team'] in teams:
            teams.append(tempObject['away_team'])
        flat_games.append(tempObject)
        
flat_games_df = pd.DataFrame.from_dict(flat_games)
flat_games_df.set_index('game_id', inplace=True)

#flat_games_df.head(20)

print(teams)

# %% [markdown]
# Get Bruins games

# %% [code]

def get_team_games(team: str) -> List[str]:
    return flat_games_df.loc[lambda g: (g['away_team'] == team) | (g['home_team'] == team)].index.tolist()

# %%

print(get_team_games('Boston Bruins'))

# %%

print(get_team_games('Pittsburgh Penguins'))

# %%

print(get_team_games('Washington Capitals'))

# %%

print(get_team_games('Toronto Maple Leafs'))

# %%
