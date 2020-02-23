#%% [markdown]
# ## This is Markdown
# [Interactive Python Blogpost](https://blogs.msdn.microsoft.com/pythonengineering/2018/11/08/data-science-with-python-in-visual-studio-code/)


#%%
## https://pandas.pydata.org/pandas-docs/stable/getting_started/10min.html

import pandas as pd
import numpy as np

# Read game.csv into a DataFrame, games
games = pd.read_csv('data/game.csv', header=[0], index_col=[0])
teams = pd.read_csv('data/team_info.csv', header=[0], index_col=[0])

# Join games and teams to pull in the team names
# better = pd.merge(games, teams, left_on='home_team_id', right_on='team_id')

# Sort and display 3 columns
# better.sort_values(['date_time'])[['date_time', 'shortName', 'teamName']].head(20)

# Change the index for the DataFrame to game_id
#games = games.set_index(['game_id'])

# Show the first 20 rows
#games.head(20)

# Get Games for the 20112012 season, group by the date, count them, and plot them
# games.loc[lambda g: g['season'] == 20112012, :].groupby(['date_time']).count().plot(y=['season'], figsize=(10,5), grid=True)

# Sum the goals for home and away, and plot
games.loc[lambda g: g['season'] == 20112012, :].groupby(['date_time'])['home_goals', 'away_goals'].agg('sum').sort_values(['date_time']).plot()
games.loc[lambda g: g['season'] == 20122013, :].groupby(['date_time'])['home_goals', 'away_goals'].agg('sum').sort_values(['date_time']).plot()
games.loc[lambda g: g['season'] == 20132014, :].groupby(['date_time'])['home_goals', 'away_goals'].agg('sum').sort_values(['date_time']).plot()



# %%

import pandas as pd

player_info = pd.read_csv('data/player_info.csv', header=[0], index_col=[0])

player_info.head(20)

player_info.groupby(['primaryPosition']).count().plot()


# %%
