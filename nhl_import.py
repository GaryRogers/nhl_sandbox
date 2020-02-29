#!/usr/bin/env python3
import requests
import pandas as pd

# https://gitlab.com/dword4/nhlapi

base_url = 'https://statsapi.web.nhl.com/api/v1'

bruins_game_ids = [
    2019020010,
    2019020027,
    2019020043,
    2019020056,
    2019020064,
    2019020078,
    2019020098,
    2019020115,
    2019020133,
    2019020162,
    2019020174,
    2019020179,
    2019020206,
    2019020220,
    2019020224,
    2019020248,
    2019020267,
    2019020272,
    2019020294,
    2019020303,
    2019020320,
    2019020333,
    2019020351,
    2019020374,
    2019020378,
    2019020391,
    2019020417,
    2019020424,
    2019020438,
    2019020454,
    2019020470,
    2019020484,
    2019020488,
    2019020508,
    2019020524,
    2019020538,
    2019020555,
    2019020571,
    2019020582,
    2019020606,
    2019020613,
    2019020627,
    2019020641,
    2019020671,
    2019020678,
    2019020694,
    2019020711,
    2019020719,
    2019020727,
    2019020755,
    2019020761,
    2019020789,
    2019020801,
    2019020812,
    2019020826,
    2019020844,
    2019020855,
    2019020877,
    2019020895,
    2019020907,
    2019020929,
    2019020945,
    2019020956,
    2019020968,
    2019020984,
    2019020999,
    2019021019,
    2019021035,
    2019021053,
    2019021073,
    2019021093,
    2019021101,
    2019021118,
    2019021136,
    2019021144,
    2019021163,
    2019021176,
    2019021191,
    2019021207,
    2019021232,
    2019021250,
    2019021260
 ]

def import_conferences():
    response = requests.get("{0}/conferences".format(base_url))

    file = open('api_data/conferences.json', 'w')
    file.write(response.text)
    file.close

def import_divisions():
    response = requests.get("{0}/divisions".format(base_url))

    file = open('api_data/divisions.json', 'w')
    file.write(response.text)
    file.close

def import_game(game_id: int):
    url = "{0}/game/{1}/feed/live".format(base_url, game_id)

    print("getting url: {0}".format(url))

    response = requests.get(url)

    print("Response status: {0}".format(response.status_code))

    if response.status_code == 200:
        file = open('api_data/game_{0}.json'.format(game_id), 'w')
        file.write(response.text)
        file.close

def import_schedule(season: int):
    response = requests.get("{0}/schedule?season={1}".format(base_url, season))

    file = open('api_data/season_{0}.json'.format(season), 'w')
    file.write(response.text)
    file.close

#import_games(2019)
#import_schedule(20192020)

#for game_id in bruins_game_ids:
#    import_game(game_id)