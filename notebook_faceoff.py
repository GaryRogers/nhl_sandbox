# %%
# What are the questions I'm trying to answer?
# - Does Bergy take more faceoffs when the team is losing?
# - Are there differences in win % in different zones?
# - Are there differences in faceoofs taken by zone?
#
# - This needs to even flatter data
# - Something closer to olap

import pandas as pd
import json

df = pd.read_csv('data/faceoff_data.csv')

df.tail(20)

player = 'Patrice Bergeron'

# %%
# Bruins games faceoff counts

# as_index=False makes groupby more sql-ish
overall_df = df.groupby('player', sort=False, as_index=False) \
    .agg({ 'game_id': 'count', 'win': 'sum' }) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('player')

overall_df['percent'] = ( overall_df['win'] / overall_df['count']) * 100

overall_df \
    .round({'percent': 2}) \
    .sort_values('count', ascending=False) \
    .head(30)

# %%
# Faceoff Stats by Opponent

pb_df = df.loc[df['player'] == player]

oppo_df = pb_df \
    .groupby('opponent', sort=False, as_index=False) \
    .agg({ 'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('opponent')

oppo_df['percent'] = (oppo_df['win'] / oppo_df['count']) * 100

oppo_df.round({'percent': 2}) \
    .sort_values('count', ascending=False) \
    .head(30)

# %% 
# Faceoff Stats by Zone

zone_df = df.loc[df['player'] == player] \
    .groupby('zone', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('zone')

zone_df['percent'] = ( zone_df['win'] / zone_df['count']) * 100

zone_df.round({'percent': 2})

# %%
# Faceoff stats by period

period_df = df.loc[df['player'] == player] \
    .groupby('period', sort=False, as_index=False) \
    .agg({'game_id': 'count', 'win': 'sum'}) \
    .rename(columns={'game_id': 'count'}) \
    .set_index('period')

period_df['percent'] = ( period_df['win'] / period_df['count'] ) * 100

period_df.round({'percent': 2})


# %%
