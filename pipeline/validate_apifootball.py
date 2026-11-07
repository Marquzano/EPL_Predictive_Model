import os
import json
import random
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('APIFOOTBALL_KEY')
BASE_URL = 'https://v3.football.api-sports.io'
HEADERS = {'x-apisports-key': API_KEY}
LEAGUE_ID = 39                 # Premier League
SEASONS = [2022, 2023, 2024]   # API-Football uses START year (2024 = 2024-25)
DB_PATH = 'data/processed/EPL_data.db'
CACHE_DIR = Path('data/raw/api_football')
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_PER_SEASON = 30
RANDOM_SEED = 42
UK_TZ = ZoneInfo('Europe/London')
API_TO_DB_NAMES = {
    'Ipswich': 'Ipswich Town',
    'Leeds': 'Leeds United',
    'Leicester': 'Leicester City',
    'Luton': 'Luton Town',
    'Newcastle': 'Newcastle United',
    'Sheffield Utd': 'Sheffield United',
    'Tottenham': 'Tottenham Hotspur',
    'Wolves': 'Wolverhampton Wanderers'
}
KEY = ['season', 'date', 'team']
CHECK_COLUMNS = ['time', 'round', 'venue', 'opponent', 'result', 'gf', 'ga']
STAT_COLUMNS = ['xg', 'xga', 'poss', 'sh', 'sot']

if not API_KEY:
    raise SystemExit('APIFOOTBALL_KEY is not set. Add it to .env in the repo root')

def fetch(endpoint, params, cache_name):
    cache_file = CACHE_DIR / f'{cache_name}.json'
    if cache_file.exists():
        return json.loads(cache_file.read_text())

    response = requests.get(f'{BASE_URL}/{endpoint}', headers=HEADERS, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data['errors']:
        raise RuntimeError(f'API error for {endpoint} {params}: {data["errors"]}')
    if not data['response']:
        raise RuntimeError(f'Empty response for {endpoint} {params}')

    cache_file.write_text(json.dumps(data))
    print(f'fetched {cache_name} | left today: {response.headers.get("x-ratelimit-requests-remaining")}'
          f' | left this minute: {response.headers.get("x-ratelimit-remaining")}')

    time.sleep(7)
    return data

def load_db_matches():
    con = sqlite3.connect(DB_PATH)
    try:
        query = ('SELECT season, date, time, round, venue, result, gf, ga, opponent, '
                 'xg, xga, poss, sh, sot, team FROM match_data WHERE season IN (2023, 2024, 2025);')
        return pd.read_sql(query, con=con)
    finally:
        con.close()

def apply_name_mapping(api_df, db_names):
    api_df['team'] = api_df['team'].replace(API_TO_DB_NAMES)
    api_df['opponent'] = api_df['opponent'].replace(API_TO_DB_NAMES)
    unknown = (set(api_df['team']) | set(api_df['opponent'])) - db_names
    if unknown:
        raise ValueError(f'Unmapped API team names: {sorted(unknown)}')
    return api_df

def get_fixtures(season):
    data = fetch('fixtures', {'league': LEAGUE_ID, 'season': season}, f'fixtures_{season}')
    return [f for f in data['response'] if f['fixture']['status']['short'] == 'FT']

def get_statistics(fixture_id):
    data = fetch('fixtures/statistics', {'fixture': fixture_id}, f'stats_{fixture_id}')
    return data['response']

def sample_fixture_ids(fixtures):
    ids = sorted(f['fixture']['id'] for f in fixtures)
    return random.Random(RANDOM_SEED).sample(ids, SAMPLE_PER_SEASON)

def result_for(gf, ga):
    if gf > ga:
        return 'W'
    if gf < ga:
        return 'L'
    return 'D'

def fixture_rows(f):
    kickoff = datetime.fromisoformat(f['fixture']['date']).astimezone(UK_TZ)
    common = {
        'fixture_id': f['fixture']['id'],
        'season': f['league']['season'] + 1,
        'date': kickoff.strftime('%Y-%m-%d'),
        'time': kickoff.strftime('%H:%M'),
        'round': f['league']['round'].replace('Regular Season - ', 'Matchweek ')
    }
    home, away = f['teams']['home'], f['teams']['away']
    home_goals, away_goals = f['goals']['home'], f['goals']['away']
    return [
        {**common, 'venue': 'Home', 'team': home['name'], 'team_api_id': home['id'],
         'opponent': away['name'], 'gf': home_goals, 'ga': away_goals,
         'result': result_for(home_goals, away_goals)},
        {**common, 'venue': 'Away', 'team': away['name'], 'team_api_id': away['id'],
         'opponent': home['name'], 'gf': away_goals, 'ga': home_goals,
         'result': result_for(away_goals, home_goals)}
    ]

def to_float(value):
    if value is None:
        return float('nan')
    return float(str(value).rstrip('%'))

def team_stats(stats_response):
    stats = {}
    for entry in stats_response:
        values = {s['type']: s['value'] for s in entry['statistics']}
        stats[entry['team']['id']] = {
            'xg': to_float(values.get('expected_goals')),
            'poss': to_float(values.get('Ball Possession')),
            'sh': to_float(values.get('Total Shots')),
            'sot': to_float(values.get('Shots on Goal'))
        }
    team_a, team_b = stats
    stats[team_a]['xga'] = stats[team_b]['xg']
    stats[team_b]['xga'] = stats[team_a]['xg']
    return stats

def merge_sources(api_df, db_df):
    merged = api_df.merge(db_df, on=KEY, how='outer', suffixes=('_api', '_db'),
                          indicator=True, validate='one_to_one')
    print(merged['_merge'].value_counts())
    unmatched = merged[merged['_merge'] != 'both']
    if not unmatched.empty:
        print(unmatched[KEY + ['_merge']].to_string())
    return merged[merged['_merge'] == 'both']

def compare_checks(merged):
    for col in CHECK_COLUMNS:
        mismatches = merged[merged[f'{col}_api'] != merged[f'{col}_db']]
        print(f'{col:9} mismatches: {len(mismatches)}')
        if 0 < len(mismatches) <= 10:
            print(mismatches[KEY + [f'{col}_api', f'{col}_db']].to_string())

def compare_stats(merged):
    results = []
    for col in STAT_COLUMNS:
        api, db = merged[f'{col}_api'], merged[f'{col}_db']
        both = api.notna() & db.notna()
        diff = api[both] - db[both]
        results.append({
            'stat': col,
            'n': int(both.sum()),
            'mean_diff': diff.mean(),
            'mean_abs_diff': diff.abs().mean(),
            'corr': api[both].corr(db[both]),
            'pct_exact': (diff.abs() < 0.05).mean() * 100
        })
    print(pd.DataFrame(results).round(3).to_string(index=False))

def main():
    fixtures = {}
    statistics = {}
    for season in SEASONS:
        fixtures[season] = get_fixtures(season)
        for fixture_id in sample_fixture_ids(fixtures[season]):
            statistics[fixture_id] = get_statistics(fixture_id)
        print(f'season {season}: {len(fixtures[season])} fixtures, {SAMPLE_PER_SEASON} sampled')

    rows = []
    for season_fixtures in fixtures.values():
        for f in season_fixtures:
            rows.extend(fixture_rows(f))
    api_df = pd.DataFrame(rows)

    start_rows = []
    for fixture_id, response in statistics.items():
        for team_api_id, values in team_stats(response).items():
            start_rows.append({'fixture_id': fixture_id, 'team_api_id': team_api_id, **values})
    stats_df = pd.DataFrame(start_rows)

    api_df = api_df.merge(stats_df, on=['fixture_id', 'team_api_id'], how='left')

    db_df = load_db_matches()
    api_df = apply_name_mapping(api_df, set(db_df['team']))
    merged = merge_sources(api_df, db_df)
    compare_checks(merged)
    compare_stats(merged)

if __name__ == '__main__':
    main()
