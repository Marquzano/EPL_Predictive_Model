def check_raw_matches(cur):
    # checking the structure of the table
    cur.execute('PRAGMA table_info(match_data);')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT date FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT time FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT comp FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT round FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT day FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT venue FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Target, no nulls
    cur.execute('SELECT DISTINCT result FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT gf FROM match_data')
    print(cur.fetchall())
    
    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT ga FROM match_data')
    print(cur.fetchall())
    
    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT opponent FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT xg FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT xga FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT poss FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT attendance FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT captain FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed, (Feature?), no nulls, do see some unrecognized characters
    cur.execute('SELECT DISTINCT formation FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed, (Feature?), no nulls
    cur.execute('SELECT DISTINCT "opp formation" FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT referee FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT "match report" FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT notes FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT sh FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT sot FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT dist FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT fk FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT pk FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT pkatt FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT team FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT season FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')

def check_matches(cur):
    # checking the structure of the table
    cur.execute('PRAGMA table_info(match_data);')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT date FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT time FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT round FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT venue FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Target, no nulls
    cur.execute('SELECT DISTINCT result FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT gf FROM match_data')
    print(cur.fetchall())
    
    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT ga FROM match_data')
    print(cur.fetchall())
    
    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT opponent FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT xg FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT xga FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT poss FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT sh FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT sot FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT team FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT season FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')