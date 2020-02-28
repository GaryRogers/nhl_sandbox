#%% [markdown]
# # NHL API Data Notebook

#%%

import pandas as pd
import json

filename = 'api_data/game_2019020001.json'

with open(filename) as json_file:
    game_data = json.load(json_file)

# Be sure to orient='index' to add sanity to the data.
df_players = pd.DataFrame.from_dict(game_data['gameData']['players'], orient='index')

values = ['fullName','link','firstName','lastName','primaryNumber','birthDate','currentAge','birthCity','birthStateProvince','birthCountry','nationality','height','weight','active','alternateCaptain','captain','rookie','shootsCatches','rosterStatus', 'currentTeam', 'primaryPosition']

df_players.head(20)



# %%
