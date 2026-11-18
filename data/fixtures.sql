BEGIN;

CREATE TABLE IF NOT EXISTS fixtures (
    season INTEGER NOT NULL,
    home_id INTEGER NOT NULL,
    away_id INTEGER NOT NULL,
    round TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL,
    fixture_id INTEGER,
    PRIMARY KEY (season, home_id, away_id)
);

CREATE INDEX IF NOT EXISTS fixtures_date ON fixtures (date);

COMMIT;