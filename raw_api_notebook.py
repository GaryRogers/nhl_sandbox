#%% [markdown]
# # NHL API Data Notebook

# %% [markdown]
# ## NHL Raw Game Data Playground
#
# Looking to poke at the NHL game data you can get from the api.
#
# In this case I'm working with a json file saved locally after download from the api
# so that I'm not pulling fresh data all the time.
#
# My primary question is who does Patrice Bergeron lose Faceoffs to the most?
# I'm starting with a different team, but will get into Bruins games once I've got the bugs worked out.

# %%
import pandas as pd
from pandas.io.json import json_normalize
import json

filename = 'api_data/game_2019020010.json'

with open(filename) as json_file:
    game_data = json.load(json_file)

# %% [markdown]
# # Players
#
# Pull in the players data for the game
# %%

# Be sure to orient='index' to add sanity to the data.
df_players = pd.DataFrame.from_dict(game_data['gameData']['players'], orient='index')
df_players.set_index('id', inplace=True)

df_players.head(5)

# %% [markdown]
# # Faceoffs
#
# Pull in the allPlays data and massage it to get a list of faceoffs for the game

# %% [code]

plays = json_normalize(game_data['liveData']['plays']['allPlays'])

players_list = plays.loc[lambda r: r['result.event'] == 'Faceoff']['players']

faceoff_list = []

for i, p in players_list.items():
    play_object = { 'winner': None, 'loser': None }
    for pi in p:
        if pi['playerType'] == 'Winner':
            play_object['winner'] = pi['player']['fullName']
        else:
            play_object['loser'] = pi['player']['fullName']
        
    faceoff_list.append(play_object)

faceoff_df = pd.DataFrame.from_dict(faceoff_list)

faceoff_df.head(5)

# %% [markdown]
# Filter things down to a particular player

# %% [code]

select_player = 'Patrice Bergeron'

player_faceoffs_df = faceoff_df.loc[lambda p: (p['winner'] == select_player) | (p['loser'] == select_player)]

player_faceoffs_df.head(20)

# %%

player_faceoffs_df.groupby(['winner']).count()

# %%