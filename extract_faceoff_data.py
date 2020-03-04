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

game_data = {
    "game_id": None,
    "season": None,
    "game_start_time": None,
    "game_tz": None,
    "home_team": None,
    "away_team": None,
}

penalty_array = []


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
    global game_data

    game_data = {
        "game_id": data['gameData']['game']['pk'],
        "season": data['gameData']['game']['season'],
        "game_start_time": data['gameData']['datetime']['dateTime'],
        "game_tz": data['gameData']['teams']['home']['venue']['timeZone']['tz'],
        "home_team": data['gameData']['teams']['home']['abbreviation'],
        "away_team": data['gameData']['teams']['away']['abbreviation']
    }

    return game_data
    

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
    
    match = re.match(r'^(\d+):(\d+)', start_time)
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


def _game_time_to_seconds(period: int, game_time: str) -> int:
    match = re.match(r'^(\d+):(\d+)', game_time)
    minutes = match[1]
    seconds = match[2]

    period_seconds = (period - 1) * 1200
    minute_seconds = int(minutes) * 60

    return int(period_seconds) + int(minute_seconds) + int(seconds)


def _invert_team(team: str) -> str:
    if team == game_data['home_team']:
        return game_data['away_team']

    if team == game_data['away_team']:
        return game_data['home_team']


def _on_powerplay(game_seconds: int, play_type: str) -> str:
    global penalty_array

    for play in penalty_array:
        if game_seconds >= play['start_time'] and game_seconds <= play['end_time']:
            if play_type == 'GOAL' and play['penaltySeverity'] == 'Minor':
                play['end_time'] = game_seconds

            return _invert_team(play['team'])

    return None


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
    global penalty_array

    returnList = []

    for play in data['liveData']['plays']['allPlays']:
        if play['result']['eventTypeId'] == 'PENALTY':
            pp_end_seconds = _compute_penalty_end_seconds(play['result']['penaltyMinutes'], play['about']['period'], play['about']['periodTime'])
            play_event = {
                "eventIdx": play['about']['eventIdx'],
                "team": play['team']['triCode'],
                "penaltySeverity": play['result']['penaltySeverity'],
                "period": play['about']['period'],
                "description": play['result']['description'],
                "penaltyMinutes": play['result']['penaltyMinutes'],
                "start_time": _game_time_to_seconds(play['about']['period'], play['about']['periodTime']),
                "end_time": pp_end_seconds
            }
            penalty_array.append(play_event)
        else:
            pp_team = _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId'])
            if pp_team:
                    returnList.append({
                        "eventIdx": play['about']['eventIdx'],
                        #"team": play['team']['triCode'],
                        "period": play['about']['period'],
                        "description": play['result']['description'],
                        "penaltyMinutes": 0,
                        "start_time": _game_time_to_seconds(play['about']['period'], play['about']['periodTime']),
                        'powerplay': pp_team
                    })
            
    return returnList


def get_zone_info(x: float, y: float, period: int) -> str:
    raise NotImplementedError


def get_player_info(id: int) -> dict:
    raise NotImplementedError


def load_game_file(filename: str) -> dict:
    logger.info('Normalizing file: {0}'.format(filename))

    with open(filename) as json_file:
        game_data = json.load(json_file)

    json_file.close()

    return game_data


def larv_faceoff_data(data: dict) -> dict:
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

    return_list = []

    for play in data['liveData']['plays']['allPlays']:
        if play['result']['eventTypeId'] == 'FACEOFF':
            temp_object = {
                "game_id":          game_data['game_id'],
                "season":           game_data['season'],
                "game_start_time":  game_data['game_start_time'],
                "game_tz":          game_data['game_tz'],
                "play_id":          play['about']['eventIdx'],
                "description":      play['result']['description'],
                "period":           play['about']['period'],
                "home_team":        game_data['home_team'],
                "away_team":        game_data['away_team'],
                "home_player":      None, #play['players'],
                "away_player":      None, #play['players'],
                "coordinates":      play['coordinates'],
                "zone":             "HOME_ATTACKING|NEUTRAL|HOME_DEFENSIVE",
                "home_score":       play['about']['goals']['home'],
                "away_score":       play['about']['goals']['away'],
                "power_play":       _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId']),
                "winning_player":   None, #play['players'],
                "losing_player":    None, #play['players'],
            }

            return_list.append(temp_object)

    return return_list


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

faceoff_data = larv_faceoff_data(game_dict)

print(json.dumps(faceoff_data, indent=2))



#files = glob.glob("api_data/game*.json")

#for filename in files:
#    try:
#        normalize_faceoff_data(filename)
#    except Exception as ex:
#        logging.error(ex)