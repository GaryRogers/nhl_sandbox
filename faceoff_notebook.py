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

#df = pd.read_json('data/faceoff_20192020020010.json')
#df = pd.read_json('data/faceoff_20192020020027.json')
df = pd.read_json('data/faceoff_20192020020043.json')

df.head(20)

# %%

def faceoff_stats(df: object, player: str) -> object:
    return_object = {
        'player': player,
        'game': {
            'wins': None,
            'taken': None,
            'percentage': None
        },
        'period': {
            '1': {
                'wins': None,
                'taken': None,
                'percentage': None
            },
            '2': {
                'wins': None,
                'taken': None,
                'percentage': None
            },
            '3': {
                'wins': None,
                'taken': None,
                'percentage': None
            }
        },
        'zone': {
            'ATTACKING_ZONE': {
                'wins': None,
                'taken': None,
                'percentage': None
            },
            'DEFENDING_ZONE': {
                'wins': None,
                'taken': None,
                'percentage': None
            },
            'NEUTRAL_ZONE': {
                'wins': None,
                'taken': None,
                'percentage': None
            }
        },
        'power_play': {
            'wins': None,
            'taken': None,
            'percentage': None
        },
        'penalty_kill': {
            'wins': None,
            'taken': None,
            'percentage': None
        }
    }

    first_row = df.loc[(df['home_player'] == player) | (df['away_player'] == player)].head(1)

    home_team = str(first_row.get('home_team').item())
    away_team = str(first_row.get('away_team').item())

    return_object['home_team'] = home_team
    return_object['away_team'] = away_team

    if player == str(first_row.get('home_player').item()):
        home_player = True
        power_play_team = home_team
    else:
        home_player = False
        power_play_team = away_team
    
    # Game Stats
    return_object['game']['wins'] = df.loc[df['winning_player'] == player]['winning_player'].count()
    return_object['game']['taken'] = df.loc[(df['winning_player'] == player) | (df['losing_player'] == player)]['home_player'].count()
    return_object['game']['percentage'] = "{0:.2f}".format((return_object['game']['wins'] / return_object['game']['taken'] * 100))

    # By Period
    for period in range(1, df['period'].max() + 1):
        return_object['period'][str(period)]['wins'] = df.loc[(df['winning_player'] == player) & (df['period'] == period)]['winning_player'].count()
        return_object['period'][str(period)]['taken'] = df.loc[( (df['winning_player'] == player) | (df['losing_player'] == player ) ) & (df['period'] == period)]['winning_player'].count()
        return_object['period'][str(period)]['percentage'] = "{0:.2f}".format((return_object['period'][str(period)]['wins'] / return_object['period'][str(period)]['taken'] * 100))

    # Power Play
    return_object['power_play']['wins'] = df.loc[(df['power_play'] == power_play_team) & ( df['winning_player'] == player)]['winning_player'].count()
    return_object['power_play']['taken'] = df.loc[(df['power_play'] == power_play_team) & ( ( df['winning_player'] == player) | ( df['losing_player'] == player) )]['winning_player'].count()
    return_object['power_play']['percentage'] = "{0:.2f}".format(( return_object['power_play']['wins'] / return_object['power_play']['taken']) * 100)

    # Penalty Kill
    return_object['penalty_kill']['wins'] = df.loc[(df['power_play'] != power_play_team) & ( df['winning_player'] == player)]['winning_player'].count()
    return_object['penalty_kill']['taken'] = df.loc[(df['power_play'] != power_play_team) & ( ( df['winning_player'] == player) | ( df['losing_player'] == player) )]['winning_player'].count()
    return_object['penalty_kill']['percentage'] = "{0:.2f}".format(( return_object['penalty_kill']['wins'] / return_object['penalty_kill']['taken']) * 100)

    # By Zone
    for zone in ['ATTACKING_ZONE', 'DEFENDING_ZONE', 'NEUTRAL_ZONE']:
        return_object['zone'][zone]['wins'] = df.loc[(df['winning_player'] == player) & (df['zone'] == zone)]['winning_player'].count()
        return_object['zone'][zone]['taken'] = df.loc[( (df['winning_player'] == player) | (df['losing_player'] == player ) ) & (df['zone'] == zone)]['winning_player'].count()
        return_object['zone'][zone]['percentage'] = "{0:.2f}".format((return_object['zone'][zone]['wins'] / return_object['zone'][zone]['taken'] * 100))
    

    return return_object

#faceoff_stats(df, 'Patrice Bergeron')
#faceoff_stats(df, 'Charlie Coyle')
faceoff_stats(df, 'David Krejci')

#print(json.dumps(bergy_stats))

# %%
