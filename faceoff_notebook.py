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

df1 = pd.read_json('data/faceoff_20192020020010.json')
df2 = pd.read_json('data/faceoff_20192020020027.json')
df3 = pd.read_json('data/faceoff_20192020020043.json')

df = df1
df = df.append(df2, ignore_index=True)
df = df.append(df3, ignore_index=True)

df.tail(20)

# %%

df.loc[df['player'] == 'Patrice Bergeron'].groupby('zone')['zone'].count()


# %%

df.loc[(df['player'] == 'Patrice Bergeron') & (df['win'])].groupby('zone')['zone'].count()

# %%
