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
import argparse
import pandas as pd

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
    """Convert seconds since start of game to a string

    ## Parameters
    
    - seconds: int - Seconds since the start of the game

    ## Returns
    
    - string - "period|mm:ss" The Period, period minutes and seconds
    """
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
    """Converts game time to seconds since start of game

    Converts the period, minutes and seconds to seconds since the start of the game.

    ## Parameters
    
    - period: int - The period to convert
    - game_time: str - The mm:ss of the period to convert

    ## Returns

    - int - The seconds since the start of the game
    """
    match = re.match(r'^(\d+):(\d+)', game_time)
    minutes = match[1]
    seconds = match[2]

    period_seconds = (period - 1) * 1200
    minute_seconds = int(minutes) * 60

    return int(period_seconds) + int(minute_seconds) + int(seconds)


def _invert_team(team: str) -> str:
    """ Return the opposing tesm

    ## Parameters

    - team: str - The team to get the opponent for

    ## Returns

    - str - The opposing team

    """
    if team == game_data['home_team']:
        return game_data['away_team']

    if team == game_data['away_team']:
        return game_data['home_team']


def _on_powerplay(game_seconds: int, play_type: str) -> str:
    """Return the team currently on the power play

    Inspect the `penalty_array` global to see if the play occurs during a powerplay.

    If the play type is a scoring play this may end the power play in the `penalty_array`

    ## Parameters

    - game_seconds: int - The seconds since the start of the game
    - play_type: str - The play type to check

    ## Retruns

    - string: The team that is currently on the power play
    """
    global penalty_array

    for play in penalty_array:
        if game_seconds >= play['start_time'] and game_seconds <= play['end_time']:
            if play_type == 'GOAL' and play['penaltySeverity'] == 'Minor':
                play['end_time'] = game_seconds

            return _invert_team(play['team'])

    return None


def _decode_players(players: List) -> dict:
    """Return a simplified dictionary of faceoff players

    Simplifies the NHL players array for a faceoff play

    ## Parameters

    - players: List - The players list from the play['players'] array

    ## Return

    - dict: Simplified dictionary of players for the play

    """
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


def _compute_zone(x: float, period: int, player: str) -> str:
    """Compute the zone name for a player and period

    Compute the ATTACKING_ZONE, DEFENDING_ZONE or NEUTRAL_ZONE based on the x coordinate.

    Since ATTACKING/DEFENDING depend on period and team this can be a little hairy

    ## Parameters

    - x: int - The x coordinate provides by the play['coordinates'] list in the NHL API
    - period: int - The period to calculate for.
    - player: string - The player to calculate for. (accounts for team)

    ## Returns

    string - ATTACKING_ZONE, DEFENDING_ZONE, NEUTRAL_ZONE

    """
    if x >= -50 and x <= 50:
        return 'NEUTRAL_ZONE'

    home_player = False
    home_player = ( player in home_players )

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


def parse_power_play_data(data: dict) -> List[dict]:
    """Extract powerplay data from NHL API Data

    Looks over allPlays and computes penelties. Adds to the `penalty_array` global.

    ## Parameters:

    - data: dict - Dictionary of NHL Game data

    ## Returns:

    - List[dict]: Returns list of penalty objects.

    ## Penalty Dictionary:

    ```json
    {
      "eventIdx": "int",
      "team": "string (ex. BOS)",
      "period": "int",
      "description": "string",
      "penaltyMinutes": "int",
      "start_time": "int (seconds since start of game)",
      "end_time": "int (seconds since start of game)"
    }
    ```
    """
    
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


def load_game_file(filename: str) -> dict:
    """ Pull in game file from filesystem

    ## Parameters

    - filename: str - Filename to read. From statsapi.web.nhl.com/api/v1/game

    ## Returns

    - dict: Dictionary structure of NHL game api

    ## Notes

    Check [GitHub](https://gitlab.com/dword4/nhlapi) for API Docs

    """
    logger.info('Normalizing file: {0}'.format(filename))

    with open(filename) as json_file:
        game_data = json.load(json_file)

    json_file.close()

    return game_data


def parse_game_data(data: dict) -> dict:
    """Parse the game specific data from the game dictionary

    Works with `game_data` global to store game data for other functions.

    ## Parameters

    - data: dict - NHL game API dictionary

    ## Returns

    - dict: A dictionary of game data

    ## Notes

    Game Dictonary

    ```json
    {
      "game_id": "int",
      "season": "int",
      "game_start_time": "string isodate",
      "game_tz": "string ex: CST",
      "home_team": "string ex: BOS",
      "away_team": "string ex: BOS",
    }
    ```
    """
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
    

def parse_player_data(data: dict) -> List[dict]:
    """Parse and store player data to `home_players` and `away_players` lists

    ## Parameters

    - data: dict - NHL game API dictionary

    ## Returns

    - List[dict]: List of simplified player dictionaries

    ## Player Dictionary

    ```json
    {
      "id": "int",
      "fullName": "string",
      "shootsCatches: "string",
      "team": "string ex: BOS",
      "primaryPosition: "string",
    # }
    ```
    """
    global home_players
    global away_players

    returnList = []

    for key, player in data['gameData']['players'].items():
        try:
            # Deal with rookies that are in pre-season games, but don't get picked up
            if 'currentTeam' in player:
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
        except Exception as ex:
            logger.error('Error converting player data for player:')
            logger.error(player)
            #logger.exception(ex)

    return returnList


def parse_faceoff_data(data: dict) -> List[dict]:
    """Parse Faceoff data into a list of faceoff dictionaries

    Main function of the script. Parses the `allPlay` data to extract and normalize the faceoff data.

    Returns two entries per faceoff, one for the winner, one for the loser.

    ## Parameters

    - data: dict - NHL game API dictionary    

    ## Returns

    - List[dict] - List of Faceoff dictionaries

    ## Faceoff Dictionary

    ```json
    {
        "game_id": "2019020010",
        "season": "20192020",
        "game_start_time": "2019-10-04T00:30:00Z",
        "game_tz": "CST",
        "play_id": 3,
        "game_time": 0,
        "description": "Patrice Bergeron faceoff won against Tyler Seguin",
        "period": "1",
        "coordinates": "0.0,0.0",
        "player": "Tyler Seguin",
        "team": "DAL",
        "opponent": "Patrice Bergeron",
        "opposing_team": "BOS",
        "home_ice": true,
        "power_play": false,
        "penelty_kill": false,
        "zone": "NEUTRAL_ZONE",
        "score_diff": 0,
        "win": false
    }
    ```
    """
    return_list = []

    for play in data['liveData']['plays']['allPlays']:
        if play['result']['eventTypeId'] == 'FACEOFF':
            players = _decode_players(play['players'])
            no = {}
            no['game_id'] = str(game_data['game_id'])
            no['season'] = game_data['season']
            no['game_start_time'] = game_data['game_start_time']
            no['game_tz'] = game_data['game_tz']
            no['play_id'] = play['about']['eventIdx']
            no['game_time'] = _game_time_to_seconds(play['about']['period'], play['about']['periodTime'])
            no['description'] = play['result']['description']
            no['period'] = str(play['about']['period'])
            no['coordinates'] = "{0},{1}".format(play['coordinates']['x'], play['coordinates']['y'])
            hp = no.copy()
            ap = no.copy()

            hp['player'] = players['home_player']
            hp['team'] = game_data['home_team']
            hp['opponent'] = players['away_player']
            hp['opposing_team'] = game_data['away_team']
            hp['home_ice'] = True
            hp['power_play'] = ( game_data['home_team'] == _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId']) )
            hp['penelty_kill'] = ( game_data['away_team'] == _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId']) )
            hp['zone'] = _compute_zone(play['coordinates']['x'], play['about']['period'], players['home_player'])
            hp['score_diff'] = play['about']['goals']['home'] - play['about']['goals']['away']
            hp['win'] = ( players['winning_player'] == players['home_player'] )

            ap['player'] = players['away_player']
            ap['team'] = game_data['away_team']
            ap['opponent'] = players['home_player']
            ap['opposing_team'] = game_data['home_team']
            ap['home_ice'] = False
            ap['power_play'] = ( game_data['away_team'] == _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId']) )
            ap['penelty_kill'] = ( game_data['home_team'] == _on_powerplay(_game_time_to_seconds(play['about']['period'], play['about']['periodTime']), play['result']['eventTypeId']) )
            ap['zone'] = _compute_zone(play['coordinates']['x'], play['about']['period'], players['away_player'])
            ap['score_diff'] = play['about']['goals']['away'] - play['about']['goals']['home']
            ap['win'] = ( players['winning_player'] == players['away_player'] )

            return_list.append(hp)
            return_list.append(ap)

    return return_list


parser = argparse.ArgumentParser(description="Convert NHL API Live data to faceoff data")
parser.add_argument('--input', help="Input file")
parser.add_argument('--output', help="Output file")
parser.add_argument('--format', help="json or csv format")
parser.add_argument('--header', dest='header', action='store_true')

args = parser.parse_args()

# Load in the game json
game_dict = load_game_file(args.input)

# Parse the game data. Saved into the `game_data` global
game_data = parse_game_data(game_dict)

# Parse the player data. Populates the `home_players` and `away_players` global
player_data = parse_player_data(game_dict)

# Parse the power play data. Saved into the penaly_array global
pp_data = parse_power_play_data(game_dict)

# Finally parse the faceoff data.
faceoff_data = parse_faceoff_data(game_dict)

# Pull the faceoff_data into a dataframe to make it easy to export.
fo_df = pd.DataFrame.from_dict(faceoff_data)

if args.output:
    if args.format.lower() == 'csv':
        fo_df.to_csv(args.output, index=False, header=args.header)
        exit(0)

    if args.format.lower() == 'json':
        fo_df.to_json(args.output, index=False, header=args.header)
        exit(0)

if args.format.lower() == 'csv':
    print(fo_df.to_csv(index=False, header=args.header))
    exit(0)

if args.format.lower() == 'json':
    print(fo_df.to_json(index=False, header=args.header))
    exit(0)