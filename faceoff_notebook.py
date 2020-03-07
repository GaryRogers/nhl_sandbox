# %%

import pandas as pd

df = pd.read_json('data/faceoff_2019020010.json')

df.head(20)

# %%

df[['description', 'game_id']].groupby('description').count()

# %%
