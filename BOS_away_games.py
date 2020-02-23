#%%

import pandas as pd
import numpy as np

games = pd.read_csv('data/game.csv', header=[0], index_col=[0])
team_info = pd.read_csv('data/team_info.csv', header=[0], index_col=[0])

games_merged = pd.merge(games, team_info, left_on='away_team_id', right_on='team_id').sort_values(['date_time'])

#games_merged.head(20)

boston_away_games = games_merged[ (games_merged['shortName'] == 'Boston') & (games_merged['outcome'] != 'away win SO') & (games_merged['outcome'] != 'home win SO')]

bag_grouped = boston_away_games.groupby(['venue_time_zone_offset','outcome'])['outcome'].count()
bag_perc = bag_grouped.groupby(level=0).apply(lambda g:100 * g / float(g.sum()))
bag_perc


# %%
