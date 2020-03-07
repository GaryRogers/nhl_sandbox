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

# %%

# as_index=False makes groupby more sql-ish
df.groupby('player', sort=False, as_index=False) \
    .count() \
    .rename(columns={'game_id': 'count'}) \
    .sort_values('count', ascending=False) \
    .set_index('player')['count']

# %%

df.loc[df['player'] == 'Patrice Bergeron'].groupby('zone')['zone'].count()

# %%

df.loc[(df['player'] == 'Patrice Bergeron') & (df['win'])].groupby('zone')['zone'].count()

# %%
