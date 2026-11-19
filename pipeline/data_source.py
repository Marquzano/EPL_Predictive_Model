#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import os
import sys
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
MATCH_DATA_COLUMNS = ['date', 'time', 'round', 'venue', 'result', 'gf', 'ga', 'opponent',
           'xg', 'xga', 'poss', 'sh', 'sot', 'team', 'season', 'team_id']
FIXTURES_COLUMNS = ['season', 'home_id', 'away_id', 'round', 'date', 'time', 'status', 'fixture_id']
FIRST_SEASON = 2025
DEFAULT_SEASONS = [2026]

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

def get_fixture_list(season):
    return api_get('fixtures', {'league': LEAGUE_ID, 'season': season})

def finished_ids(fixture_list):
    return [f['fixture']['id'] for f in fixture_list if f['fixture']['status']['short'] == 'FT']

def find_uncached(fixture_ids):
    return [fid for fid in fixture_ids if not cache_path(fid).exists()]

def missing_stats(fixture):
    if len(fixture['statistics']) != 2:
        return ['no statistics for one or both teams']
    problems = []
    for team in fixture['statistics']:
        values = {s['type']: s['value'] for s in team['statistics']}
        for stat in REQUIRED_STATS:
            if values.get(stat) is None:
                problems.append(f"{team['team']['name']}: {stat}")
    return problems

def fetch_and_cache(fixture_ids):
    for start in range(0, len(fixture_ids), BATCH_SIZE):
        batch = fixture_ids[start:start+BATCH_SIZE]
        fixtures = api_get('fixtures', {'ids': '-'.join(str(fid) for fid in batch)})

        for f in fixtures:
            problems = missing_stats(f)
            if problems:
                print(f"INCOMPLETE {f['fixture']['id']} | {f['fixture']['date'][:10]} | "
                      f"{f['teams']['home']['name']} v {f['teams']['away']['name']} | "
                      f"missing: {', '.join(problems)}")
            else:
                cache_path(f['fixture']['id']).write_text(json.dumps(f))

        print(f'fetched {start + len(batch)}/{len(fixture_ids)}')

def load_cached(fixture_ids):
    missing = find_uncached(fixture_ids)
    if missing:
        print(f'SKIPPED {len(missing)} finished fixtures without complete stats: {missing}')
    return [json.loads(cache_path(fid).read_text()) for fid in fixture_ids if fid not in missing]

def result_for(gf, ga):
    if gf > ga:
        return 'W'
    if gf < ga:
        return 'L'
    return 'D'

def to_float(value):
    return float(str(value).rstrip('%'))

def team_stats(fixture):
    stats = {}
    for entry in fixture['statistics']:
        values = {s['type']: s['value'] for s in entry['statistics']}
        stats[entry['team']['id']] = {
            'xg': to_float(values['expected_goals']),
            'poss': to_float(values['Ball Possession']),
            'sh': to_float(values['Total Shots']),
            'sot': to_float(values['Shots on Goal'])
        }
    return stats

def match_data_row(common, venue, team, opponent, gf, ga, own, opp):
    return {**common, 'venue': venue, 'team': team, 'opponent': opponent,
            'gf': gf, 'ga': ga, 'result': result_for(gf, ga),
            'xg': own['xg'], 'xga': opp['xg'],
            'poss': own['poss'], 'sh': own['sh'], 'sot': own['sot']}

def kickoff_fields(f):
    kickoff = datetime.fromisoformat(f['fixture']['date']).astimezone(UK_TZ)
    return {
        'fixture_id': f['fixture']['id'],
        'season': f['league']['season'] + 1,
        'date': kickoff.strftime('%Y-%m-%d'),
        'time': kickoff.strftime('%H:%M'),
        'round': f['league']['round'].replace('Regular Season - ', 'Matchweek ')
    }

def fixture_table_rows(f):
    return {
        **kickoff_fields(f),
        'status': f['fixture']['status']['short'],
        'home': f['teams']['home']['name'],
        'away': f['teams']['away']['name']
    }

def fixture_rows(f):
    common = kickoff_fields(f)
    home, away = f['teams']['home'], f['teams']['away']
    hg, ag = f['goals']['home'], f['goals']['away']
    stats = team_stats(f)
    hs, aws = stats[home['id']], stats[away['id']]
    return [
        match_data_row(common, 'Home', home['name'], away['name'], hg, ag, hs, aws),
        match_data_row(common, 'Away', away['name'], home['name'], ag, hg, aws, hs)
    ]

def load_name_maps(con):
    aliases = dict(con.execute(
        "SELECT alias, team FROM team_aliases WHERE source = 'api_football'").fetchall())
    registry = dict(con.execute('SELECT team, team_id FROM team_registry').fetchall())
    return aliases, registry

def stop_on_unknown(unknown):
    if unknown:
        lines = '\n'.join(f' {name} (e.g. fixture {fid})' for name, fid in unknown.items())
        raise SystemExit(f'Unknown team names - add to team_aliases or team_registry, then rerun:\n{lines}')

def map_fixture_ids(rows, aliases, registry):
    unknown = {}
    for row in rows:
        for side in ('home', 'away'):
            name = aliases.get(row[side], row[side])
            if name not in registry:
                unknown.setdefault(name, row['fixture_id'])
            row[f'{side}_id'] = registry.get(name)
    stop_on_unknown(unknown)

def map_names(rows, aliases, registry):
    unknown = {}
    for row in rows:
        row['team'] = aliases.get(row['team'], row['team'])
        row['opponent'] = aliases.get(row['opponent'], row['opponent'])
        for name in (row['team'], row['opponent']):
            if name not in registry:
                unknown.setdefault(name, row['fixture_id'])
        row['team_id'] = registry.get(row['team'])

    stop_on_unknown(unknown)

def upsert(con, table, columns, key, rows):
    placeholders = ', '.join(f':{c}' for c in columns)
    updates = ', '.join(f'{c} = excluded.{c}' for c in columns if c not in key)
    sql = (f'INSERT INTO {table} ({", ".join(columns)}) VALUES ({placeholders}) '
           f'ON CONFLICT({", ".join(key)}) DO UPDATE SET {updates}')
    with con:
        con.executemany(sql, rows)
    print(f'upserted {len(rows)} rows into {table}')

def ingest_season(con, season, aliases, registry):
    fixture_list = get_fixture_list(season)

    fixture_table = [fixture_table_rows(f) for f in fixture_list]
    map_fixture_ids(fixture_table, aliases, registry)
    upsert(con, 'fixtures', FIXTURES_COLUMNS, ('season', 'home_id', 'away_id'), fixture_table)

    finished = finished_ids(fixture_list)
    to_fetch = find_uncached(finished)
    print(f'season {season}: {len(finished)} finished, {len(to_fetch)} to fetch')

    fetch_and_cache(to_fetch)
    fixtures = load_cached(finished)
    rows = [row for f in fixtures for row in fixture_rows(f)]
    map_names(rows, aliases, registry)
    upsert(con, 'match_data', MATCH_DATA_COLUMNS, ('team_id', 'date'), rows)

if __name__ == '__main__':
    seasons = [int(s) for s in sys.argv[1:]] or DEFAULT_SEASONS
    too_early = [s for s in seasons if s < FIRST_SEASON]
    if too_early:
        raise SystemExit(f'Refusing seasons {too_early}: before {FIRST_SEASON} is FBref history')

    con = sqlite3.connect(DB_PATH)
    try:
        aliases, registry = load_name_maps(con)
        for season in seasons:
            ingest_season(con, season, aliases, registry)
    finally:
        con.close()

    print(f'done | API requests this run: {request_count}')
    print(f'next: rerun data_transform.py to rebuild the performance tables')
