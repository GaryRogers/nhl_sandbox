#!/usr/bin/env python3

from typing import List
import pandas as pd
from pandas.io.json import json_normalize
import json
import glob
import logging
import re
import datetime
import math

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# [TODO] Get PP/PKs and times into lists for lookup.
#   allPlays['penaltyPlays']

# Faceoff Normalized
# {
#   "game_id": int,                 # g['gameData']['game']['pk']
#   "season": int,                  # g['gameData']['game']['season']
#   "game_start_time": "",          # g['gameData']['datetime']['dateTime']
#   "game_tz": "",                  # g['gameData']['teams']['home']['venue']['timeZone']['tz']
#   "play_id": int,                 # g['liveData']['plays']['allPlays'][x]['about']['eventIdx']
#   "description": "",              # g['liveData']['plays']['allPlays'][x]['result']['description']
#   "period": int,                  # g['liveData']['plays']['allPlays'][x]['about']['period']
#   "home_team": "",                # g['gameData']['teams']['home']['abbreviation']
#   "away_team": "",                # g['gameData']['teams']['away']['abbreviation']
#   "home_player": "",              # function g['liveData']['plays']['allPlays']['plays'][x]['players']
#   "away_player": "",              # function g['liveData']['plays']['allPlays']['plays'][x]['players']
#   "coordinates": [float, float],  # g['liveData']['plays']['allPlays'][x]['coordinates']['x']/['y']
#   "zone": "HOME_ATTACKING|NEUTRAL|HOME_DEFENSIVE", # function g['liveData']['plays']['allPlays'][x]['coordinates']
#   "home_score": int,              # g['liveData']['plays']['allPlays'][x]['about']['goals']['home']
#   "away_score": int,              # g['liveData']['plays']['allPlays'][x]['about']['goals']['away']
#   "power_play": "team id",        # function g['liveData]['plays']['allPlays'][x]['eventIdx']
#   "winning_player": "",           # function g['liveData']['plays']['allPlays']['plays'][x]['players']
#   "losing_player": "",            # function g['liveData']['plays']['allPlays']['plays'][x]['players']
# }

def parse_game_data(data: dict) -> dict:
    # Game Normalized
    # {
    #   "game_id": int,         # g['gameData']['game']['pk']
    #   "season": int,          # g['gameData']['game']['season']
    #   "game_start_time": "",  # g['gameData']['datetime']['dateTime']
    #   "game_tz": "",          # g['gameData']['teams']['home']['venue']['timeZone']['tz']
    #   "home_team": "",        # g['gameData']['teams']['home']['abbreviation']
    #   "away_team": "",        # g['gameData']['teams']['away']['abbreviation']
    # }
    return {
        "game_id": data['gameData']['game']['pk'],
        "season": data['gameData']['game']['season'],
        "game_start_time": data['gameData']['datetime']['dateTime'],
        "game_tz": data['gameData']['teams']['home']['venue']['timeZone']['tz'],
        "home_team": data['gameData']['teams']['home']['abbreviation'],
        "away_team": data['gameData']['teams']['away']['abbreviation']
    }
    

def parse_player_data(data: dict) -> dict:
    # Players Normalized
    # {
    #   "id": int,              # g['gameData']['players'][x]['id']
    #   "fullName": "",         # g['gameData']['players'][x]['fullName']
    #   "shootsCatches: "",     # g['gameData']['players'][x]['shootsCatches']
    #   "team": "",             # g['gameData']['players'][x]['currentTeam']['triCode']
    #   "primaryPosition: "",   # g['gameData']['players'][x]['primaryPosition']['abbreviation']
    # }

    returnList = []

    for key, player in data['gameData']['players'].items():
        returnList.append({
            "id": player['id'],
            "fullName": player['fullName'],
            "shootsCatches": player['shootsCatches'],
            "team": player['currentTeam']['triCode'],
            "primaryPosition": player['primaryPosition']['abbreviation']
        })

    return returnList


def _compute_penalty_end_seconds(penalty_minutes: int, period: int, start_time: str) -> int:
    # you can think of a game as a continum of seconds, periods are buckets.
    # a game is 3600 - 3900 seconds, depending on Overtime (normal season)
    # calculating end time is start_time + penalty seconds
    # depending on where the end_time ends determines the period
    # You can apply this if you calculate game_seconds for a play
    
    match = re.match('^(\d+):(\d+)', start_time)
    minutes = match[1]
    seconds = match[2]

    start_seconds = (int(minutes) * 60 + int(seconds)) + ( (period - 1) * 1200 )
    end_seconds = start_seconds + penalty_minutes * 60

    return end_seconds


def _seconds_to_game_time(seconds: int) -> str:
    # periods are 1200 seconds (regular season OT will still work)
    # Ceil gives us a 'round up'
    period = math.ceil(seconds/1200)

    # Subtract period from the echoch seconds so that our timedelta is correct for a period
    seconds = seconds - ((period - 1) * 1200)

    # Do some string manipulaition to chop off the hours from the time delta.
    period_time = ':'.join(str(datetime.timedelta(seconds=seconds)).split(':')[1:])

    # Return Period|Minutes:Seconds
    return '{0}|{1}'.format(period, period_time)


def parse_power_play_data(data: dict) -> dict:
    # {
    #   "eventIdx": int,
    #   "team": "",
    #   "period": int,
    #   "description": "",
    #   "penaltyMinutes": int,
    #   "start_time": "",
    #   "end_time": ""
    # }

    penalty_ids = data['liveData']['plays']['penaltyPlays']

    returnList = []

    current_pp = False
    pp_end_seconds = 0

    for play in data['liveData']['plays']['allPlays']:
        if play['result']['eventTypeId'] == 'PENALTY':
            current_pp = True
            pp_end_seconds = _compute_penalty_end_seconds(play['result']['penaltyMinutes'], play['about']['period'], play['about']['periodTime'])
            returnList.append({
                "eventIdx": play['about']['eventIdx'],
                "team": play['team']['triCode'],
                "period": play['about']['period'],
                "description": play['result']['description'],
                "penaltyMinutes": play['result']['penaltyMinutes'],
                "start_time": play['about']['periodTime'],
                "end_time": _seconds_to_game_time(pp_end_seconds)
            })
    
    return returnList


def get_zone_info(x: float, y: float, period: int) -> str:
    raise NotImplementedError

def get_player_info(id: int) -> dict:
    raise NotImplementedError

def is_power_play(id: int) -> str:
    # Return the Team TriCode that is on the PP
    # Will need to compute based on the Penalty event and time
    raise NotImplementedError

def load_game_file(filename: str) -> dict:
    logger.info('Normalizing file: {0}'.format(filename))

    with open(filename) as json_file:
        game_data = json.load(json_file)

    json_file.close()

    return game_data
   

def normalize_faceoff_data(filename: str) -> List[str]:
    logger.info('Normalizing file: {0}'.format(filename))

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

game_dict = load_game_file('api_data/game_2019020010.json')

game_data = parse_game_data(game_dict)

player_data = parse_player_data(game_dict)

pp_data = parse_power_play_data(game_dict)

print(json.dumps(pp_data, indent=2))

#files = glob.glob("api_data/game*.json")

#for filename in files:
#    try:
#        normalize_faceoff_data(filename)
#    except Exception as ex:
#        logging.error(ex)