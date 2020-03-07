#%% [markdown]
# # NHL 2019-2020 Season data notebook
#
# Notebook for exploring the NHL API season API data

#%% [code]

import pandas as pd
from pandas.io.json import json_normalize
import json

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

for i, d in dates.iterrows():
    for g in d['games']:
        tempObject = { "date": i, "game_id": g['gamePk'] }
        tempObject['away_team'] = g['teams']['away']['team']['name']
        tempObject['home_team'] = g['teams']['home']['team']['name']
        flat_games.append(tempObject)
        
flat_games_df = pd.DataFrame.from_dict(flat_games)
flat_games_df.set_index('game_id', inplace=True)

flat_games_df.head(20)

# %% [markdown]
# Get Bruins games

# %% [code]
bruins_games = flat_games_df.loc[lambda g: (g['away_team'] == 'Boston Bruins') | (g['home_team'] == 'Boston Bruins')]

bruins_games.head(20)

#bruins_games.index.tolist()


# %%
