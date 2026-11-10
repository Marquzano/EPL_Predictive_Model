BEGIN;

CREATE UNIQUE INDEX IF NOT EXISTS team_registry_team ON team_registry (team);
CREATE UNIQUE INDEX IF NOT EXISTS team_registry_team_id ON team_registry (team_id);

INSERT INTO team_registry (team, team_id) VALUES
    ('Sunderland', 27),
    ('Coventry City', 28),
    ('Hull City', 29)
ON CONFLICT (team) DO NOTHING;

CREATE TABLE IF NOT EXISTS team_aliases (
    source TEXT NOT NULL,
    alias TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (source, alias)
);

INSERT INTO team_aliases (source, alias, team) VALUES
    ('api_football', 'Wolves', 'Wolverhampton Wanderers'),
    ('api_football', 'Ipswich', 'Ipswich Town'),
    ('api_football', 'Leeds', 'Leeds United'),
    ('api_football', 'Leicester', 'Leicester City'),
    ('api_football', 'Luton', 'Luton Town'),
    ('api_football', 'Newcastle', 'Newcastle United'),
    ('api_football', 'Sheffield Utd', 'Sheffield United'),
    ('api_football', 'Tottenham', 'Tottenham Hotspur'),
    ('api_football', 'Coventry', 'Coventry City')
ON CONFLICT (source, alias) DO UPDATE SET team = excluded.team;

COMMIT;