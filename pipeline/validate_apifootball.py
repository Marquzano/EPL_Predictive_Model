import os
import json
import time
import sqlite3
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('APIFOOTBALL_KEY')
if not API_KEY:
    raise SystemExit('APIFOOTBALL_KEY is not set. Add it to .env in the repo root')

BASE_URL = 'https://v3.football.api-sports.io'
HEADERS = {'x-apisports-key': API_KEY}
LEAGUE_ID = 39                 # Premier League
SEASONS = [2022, 2023, 2024]   # API-Football uses START year (2024 = 2024-25)
DB_PATH = 'data/processed/EPL_data.db'
CACHE_DIR = Path('data/raw/api_football')
CACHE_DIR.mkdir(parents=True, exist_ok=True)
