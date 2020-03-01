#!/usr/bin/env python3

import pandas as pd
from pandas.io.json import json_normalize
import json
import glob
import logging

def normalize_faceoff_data(filename: str):
    logging.info('Normalizing file: {0}'.format(filename))

    with open(filename) as json_file:
        game_data = json.load(json_file)

    gameId = game_data['gamePk']

    plays = json_normalize(game_data['liveData']['plays']['allPlays'])

    plays_list = plays.loc[lambda r: r['result.event'] == 'Faceoff']

    faceoff_list = []

    for i, p in plays_list.iterrows():
        play_object = { 
            'winner': None, 
            'loser': None, 
            'gameId': gameId, 
            'period': p['about.period']
        }
        
        players_list = p['players']
        
        for player in players_list:
            if player['playerType'] == 'Winner':
                play_object['winner'] = player['player']['fullName']
            else:
                play_object['loser'] = player['player']['fullName']
            
        faceoff_list.append(play_object)

    faceoff_df = pd.DataFrame.from_dict(faceoff_list)

    select_player = 'Patrice Bergeron'

    player_faceoffs = faceoff_df.loc[lambda p: (p['winner'] == select_player) | (p['loser'] == select_player)]

    faceoff_count = player_faceoffs.groupby(['winner','period','gameId']).count()

    normalized_faceoffs = []

    for i, p in faceoff_count.iterrows():
        row = { 'Name': i[0], 'faceoff_win_count': p.values[0], 'gameId': i[2], 'period': i[1] }
        normalized_faceoffs.append(row)

    normalized_faceoffs_df = pd.DataFrame.from_dict(normalized_faceoffs)

    outfile = open("data/faceoff_normalized.csv", "a")
    outfile.write(normalized_faceoffs_df.to_csv(index=False))
    outfile.close()

files = glob.glob("api_data/game*.json")

for filename in files:
    try:
        normalize_faceoff_data(filename)
    except Exception as ex:
        logging.error(ex)