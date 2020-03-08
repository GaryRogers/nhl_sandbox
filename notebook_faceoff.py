# %%
# What are the questions I'm trying to answer?
# - Does Bergy take more faceoffs when the team is losing?
# - Are there differences in win % in different zones?
# - Are there differences in faceoofs taken by zone?
#
# - This needs to even flatter data
# - Something closer to olap

import pandas as pd
import matplotlib.pyplot as plt

player = 'Auston Matthews'

faceoff_data = pd.read_csv('data/faceoff_data.csv')

faceoff_data.tail(20)

# %%
# Faceoff stats

# as_index=False makes groupby more sql-ish
temp_df = faceoff_data.groupby('player', sort=False, as_index=False) \
    .agg({ 'game_id': 'count', 'win': 'sum' }) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('player')

temp_df['percent'] = ( temp_df['win'] / temp_df['count']) * 100

temp_df \
    .round({'percent': 2}) \
    .sort_values('count', ascending=False) \
    .head(30)

# %%
# Faceoff Stats by Opponent

temp_df = faceoff_data.loc[faceoff_data['player'] == player] \
    .groupby('opponent', sort=False, as_index=False) \
    .agg({ 'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('opponent')

temp_df['percent'] = (temp_df['win'] / temp_df['count']) * 100

temp_df.round({'percent': 2}).sort_values('count', ascending=False).head(30)
#temp_df.round({'percent': 2}).sort_values('count', ascending=False).plot()

# %% 
# Faceoff Stats by Zone

temp_df = faceoff_data.loc[faceoff_data['player'] == player] \
    .groupby('zone', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('zone')

temp_df['percent'] = ( temp_df['win'] / temp_df['count']) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# Faceoff stats by period

temp_df = faceoff_data.loc[faceoff_data['player'] == player] \
    .groupby('period', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('period')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# Faceoff stats by Timezone

temp_df = faceoff_data.loc[faceoff_data['player'] == player] \
    .groupby('game_tz', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('game_tz')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# Faceoff stats by opp_team

temp_df = faceoff_data.loc[faceoff_data['player'] == player] \
    .groupby('opposing_team', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('opposing_team')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# Power Play Stats

temp_df = faceoff_data.loc[(faceoff_data['player'] == player) & ( faceoff_data['power_play'] == True ) ] \
    .groupby('power_play', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('power_play')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# Penalty Kill Stats

temp_df = faceoff_data.loc[(faceoff_data['player'] == player) & ( faceoff_data['penelty_kill'] == True ) ] \
    .groupby('penelty_kill', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('penelty_kill')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# 5 on 5 Stats

temp_df = faceoff_data.loc[(faceoff_data['player'] == player) & ( faceoff_data['penelty_kill'] == False ) & ( faceoff_data['power_play'] == False ) ] \
    .groupby('season', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('season')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)

# %%
# Home Ice Stats

temp_df = faceoff_data.loc[(faceoff_data['player'] == player) & ( faceoff_data['home_ice'] == True ) ] \
    .groupby('home_ice', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('home_ice')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('percent', ascending=False)


# %%
# Score Diff Stats

temp_df = faceoff_data.loc[faceoff_data['player'] == player] \
    .groupby('score_diff', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('score_diff')

temp_df['percent'] = ( temp_df['win'] / temp_df['count'] ) * 100

temp_df.round({'percent': 2}).sort_values('score_diff', ascending=False)


# %%
