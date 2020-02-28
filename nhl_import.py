#!/usr/bin/env python3
import requests
import pandas as pd

# https://gitlab.com/dword4/nhlapi

base_url = 'https://statsapi.web.nhl.com/api/v1'

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

def import_games(year: int):
    #for i in range(900):
    #    game_no = i + 1
    #    game_string = '{0:03d}'.format(i)
    #    game_id = '{0}02{1}'.format(year,game_string)
    #
    #    response = requests.get("{0}/game/{1}/feed/live".format(base_url, game_id))
    #
    #    if response.status_code == '200':
    #        file = open('api_data/game_{0}.json'.fomrat(game_id), 'w')
    #        file.write(response.text)
    #        file.close

    url = "{0}/game/{1}/feed/live".format(base_url, 2019020002)

    print("getting url: {0}".format(url))

    response = requests.get(url)

    print("Response status: {0}".format(response.status_code))

    if response.status_code == 200:
        file = open('api_data/game_{0}.json'.format('2019020002'), 'w')
        file.write(response.text)
        file.close

import_games(2019)