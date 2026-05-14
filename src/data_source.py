#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import pandas as pd
import requests as re
from requests.exceptions import RequestException

if __name__ == '__main__':
    # trying out https://www.fotmob.com/api
    # by using requests to pull data straight from the site

    session = re.Session()
    base_url = 'https://www.fotmob.com/api'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'no-cache',            
            }
        params = {'id':47, 'season':'2025/2026'}
        url = f'{base_url}/leagues'
        response = session.get(url, params=params, headers=headers)

        print(response.text)

        result = response.json()
        print(result)
    except RequestException as err:
        print(f'Error in request: {err}')