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

home_players = []
away_players = []
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
    global home_players
    global away_players

    returnList = []

    for key, player in data['gameData']['players'].items():
        if player['currentTeam']['triCode'] == game_data['home_team']:
            home_players.append(player['fullName'])
        else:
            away_players.append(player['fullName'])

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


def _decode_players(players: List) -> dict:
    return_dict = {
        "home_player": None,
        "away_player": None,
        "winning_player": None,
        "losing_player": None
    }

    for player in players:
        if player['playerType'] == 'Winner':
            return_dict['winning_player'] = player['player']['fullName']
        else:
            return_dict['losing_player'] = player['player']['fullName']

        if player['player']['fullName'] in home_players:
            return_dict['home_player'] = player['player']['fullName']
        else:
            return_dict['away_player'] = player['player']['fullName']

    return return_dict


def _compute_zone(x: float, period: int, winning_player: str) -> str:
    if x >= -50 and x <= 50:
        return 'NEUTRAL_ZONE'

    home_player = False
    home_player = ( winning_player in home_players )

    if int(period) in [1,3,5,7,9]:
        if home_player:
            if x < -50:
                return 'DEFENDING_ZONE'
            if x > 50:
                return 'ATTACKING_ZONE'
        else:
            if x < -50:
                return 'ATTACKING_ZONE'
            if x > 50:
                return 'DEFENDING_ZONE'
    else:
        if home_player:
            if x < -50:
                return 'ATTACKING_ZONE'
            if x > 50:
                return 'DEFENDING_ZONE'
        else:
            if x < -50:
                return 'DEFENDING_ZONE'
            if x > 50:
                return 'ATTACKING_ZONE'

    return None
    

def parse_faceoff_data(data: dict) -> dict:
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
            players = _decode_players(play['players'])
            temp_object = {
                "game_id":          game_data['game_id'],
                "season":           int(game_data['season']),
                "game_start_time":  game_data['game_start_time'],
                "game_tz":          game_data['game_tz'],
                "play_id":          play['about']['eventIdx'],
                "description":      play['result']['description'],
                "period":           play['about']['period'],
                "home_team":        game_data['home_team'],
                "away_team":        game_data['away_team'],
                "home_player":      players['home_player'],
                "away_player":      players['away_player'],
                "coordinates":      play['coordinates'],
                "zone":             _compute_zone(play['coordinates']['x'], play['about']['period'], players['winning_player']),
                "home_score":       play['about']['goals']['home'],
                "away_score":       play['about']['goals']['away'],
                "power_play":       _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId']),
                "winning_player":   players['winning_player'],
                "losing_player":    players['losing_player']
            }

            return_list.append(temp_object)

    return return_list


game_dict = load_game_file('api_data/game_2019020043.json')

game_data = parse_game_data(game_dict)

player_data = parse_player_data(game_dict)

pp_data = parse_power_play_data(game_dict)

faceoff_data = parse_faceoff_data(game_dict)

print(json.dumps(faceoff_data, indent=2))

#files = glob.glob("api_data/game*.json")

#for filename in files:
#    try:
#        normalize_faceoff_data(filename)
#    except Exception as ex:
#        logging.error(ex)