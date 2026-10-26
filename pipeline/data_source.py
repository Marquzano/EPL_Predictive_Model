#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import pandas as pd
import requests as re
from requests.exceptions import RequestException

if __name__ == '__main__':
    # trying out API-Football
    # will continue once I figure out a plan to:
    # retrieve all necesarry stats from one endpoint (if possible)

    session = re.Session()
    base_url = 'https://v3.football.api-sports.io/'

    try:
        url = f'{base_url}leagues'
        params = {}
        headers = {
            'x-apisports-key': '710c55cb489a5287b157c77aed1fbd66'
            }
        response = session.get(url, params=params, headers=headers)

        print(response.text)

        result = response.json()
        print(result)
    except RequestException as err:
        print(f'Error in request: {err}')