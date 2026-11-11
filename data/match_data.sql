BEGIN;

CREATE UNIQUE INDEX IF NOT EXISTS match_data_team_id_date ON match_data (team_id, date);

COMMIT;