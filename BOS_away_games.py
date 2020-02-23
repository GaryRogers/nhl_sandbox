#%%

# Initial Import of data
import pandas as pd
import numpy as np
import re

games = pd.read_csv('data/game.csv', header=[0], index_col=[0])
team_info = pd.read_csv('data/team_info.csv', header=[0], index_col=[0])

#%%

# Join games to the team_info for 'nice' names
games_merged = pd.merge(games, team_info, left_on='away_team_id', right_on='team_id').sort_values(['date_time'])

# Add a 'start hour' column from a regex on the date_time_GMT
games_merged['start_hour'] = games_merged.apply(lambda g: re.search(r'\d+-\d+-\d+T(\d+)', g['date_time_GMT']).group(1), axis=1 )

# Add in an 'away_win' column to collapse the outcome string into a boolean
games_merged['away_win'] = games_merged.apply(lambda g: re.match(r'away win', g['outcome']) != None, axis=1)

# Just get the Boston away games
boston_away_games = games_merged[ (games_merged['shortName'] == 'Boston') & (games_merged['outcome'] != 'away win SO') & (games_merged['outcome'] != 'home win SO')]

# Boston Game Outcomes grouped by Timezone
bag_grouped = boston_away_games.groupby(['venue_time_zone_offset','outcome'])['outcome'].count()
bag_perc = bag_grouped.groupby(level=0).apply(lambda g:100 * g / float(g.sum()))
bag_perc


# %%

# Compare based on the hour of start.
bag_grouped_hour = boston_away_games.groupby(['start_hour', 'away_win'])['away_win'].count()
bag_hour_perc = bag_grouped_hour.groupby(level=0).apply(lambda g:100 * g / float(g.sum()))
bag_hour_perc

# %%
