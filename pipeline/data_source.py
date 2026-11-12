#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import os
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('APIFOOTBALL_KEY')
BASE_URL = 'https://v3.football.api-sports.io'
HEADERS = {'x-apisports-key': API_KEY}
LEAGUE_ID = 39 # Premier League
DB_PATH = 'data/processed/EPL_data.db'
CACHE_DIR = Path('data/raw/api_football/fixtures')
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BATCH_SIZE = 20 # API max for ?ids=
PAUSE = 0.25 # ~240/min, under Pro 300 req/min
UK_TZ = ZoneInfo('Europe/London')
REQUIRED_STATS = ['expected_goals', 'Ball Possession', 'Total Shots', 'Shots on Goal']

if not API_KEY:
    raise SystemExit('APIFOOTBALL_KEY is not set. Add it to .env in the repo root')

request_count = 0

def api_get(endpoint, params):
    global request_count
    time.sleep(PAUSE)
    response = requests.get(f'{BASE_URL}/{endpoint}', headers=HEADERS, params=params, timeout=30)
    request_count += 1
    response.raise_for_status()
    data = response.json()

    if data['errors']:
        raise RuntimeError(f'API error for {endpoint} {params}: {data["errors"]}')

    return data['response']

def cache_path(fixture_id):
    return CACHE_DIR / f'fixture_{fixture_id}.json'

def get_finished_ids(season):
    fixtures = api_get('fixtures', {'league': LEAGUE_ID, 'season': season})
    return [f['fixture']['id'] for f in fixtures if f['fixture']['status']['short'] == 'FT']

def find_uncached(fixture_ids):
    return [fid for fid in fixture_ids if not cache_path(fid).exists()]

def has_required_stats(fixture):
    if len(fixture['statistics']) != 2:
        return False
    for team in fixture['statistics']:
        values = {s['type']: s['value'] for s in team['statistics']}
        if any(values.get(stat) is None for stat in REQUIRED_STATS):
            return False
    return True

def fetch_and_cache(fixture_ids):
    for start in range(0, len(fixture_ids), BATCH_SIZE):
        batch = fixture_ids[start:start+BATCH_SIZE]
        fixtures = api_get('fixtures', {'ids': '-'.join(str(fid) for fid in batch)})

        for f in fixtures:
            if has_required_stats(f):
                cache_path(f['fixture']['id']).write_text(json.dumps(f))

        print(f'fetched {start + len(batch)}/{len(fixture_ids)}')

def load_cached(fixture_ids):
    missing = [fid for fid in fixture_ids if not cache_path(fid).exists()]
    if missing:
        raise SystemExit(f'{len(missing)} finished fixtures have no complete stats yet: {missing}')
    return [json.loads(cache_path(fid).read_text()) for fid in fixture_ids]
