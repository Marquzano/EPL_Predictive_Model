import sqlite3,os,sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
def myprint(string,clear=False):
    if clear:
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K") 
    print(string)

#Adjust OS Commands
def OScom(command):
    windows = {'open':'start','rm':'del'}
    if os.name=='nt':
        return(windows[command])
    else:
        return(command)

def OSpath(path):
    if os.name=='nt':
        return(path.replace('/',os.sep))
    else:
        return(path)

#File Names
matchdb = OSpath('../data/processed/Matches_21to25.db')
matchcsv = OSpath('../data/processed/Matches_21to25.csv')
matchxlsx = OSpath('../data/processed/Matches_21to25.xlsx')

#Load in data
text = pd.read_csv(f"{matchcsv}")

#Loop Through Each Team
for team in np.sort(text['Home'].unique()):
    print(f'Processing {team}')
    #Remove spaces from team name for file management
    teamfile = ''.join(team.split(' '))

    #Get all data for the given team and trim to relevant stats
    full = pd.read_csv(OSpath(f'../data/processed/Teams/{teamfile}/AllData.csv'))
    full = full[['ID','Season','Round','Home','HomeGoal','AwayGoal','HomeXG','AwayXG','HomePoss','AwayPoss',
                'HomeSH','HomeSOT','HomeDist','HomeFK','HomePK','HomePKAtt',
                'AwaySH','AwaySOT','AwayDist','AwayFK','AwayPK','AwayPKAtt']]
    home = pd.read_csv(OSpath(f'../data/processed/Teams/{teamfile}/AllData_Home.csv'))
    home = home[['ID','Season','Round','HomeGoal','AwayGoal','HomeXG','AwayXG','HomePoss',
                'HomeSH','HomeSOT','HomeDist','HomeFK','HomePK','HomePKAtt']]
    away = pd.read_csv(OSpath(f'../data/processed/Teams/{teamfile}/AllData_Away.csv'))
    away = away[['ID','Season','Round','HomeGoal','AwayGoal','HomeXG','AwayXG','AwayPoss',
                'AwaySH','AwaySOT','AwayDist','AwayFK','AwayPK','AwayPKAtt']]

    #Output data arrays
    window = 10
    fl,hl,al = [len(full.loc[window:]),
                len(home.loc[window:]),
                len(away.loc[window:])]
    [roll_all_full, roll_window_full, roll_season_full,
     roll_all_home, roll_window_home, roll_season_home,
     roll_all_away, roll_window_away, roll_season_away] = [[[]]*fl,[[]]*fl,[[]]*fl,
                                                           [[]]*hl,[[]]*hl,[[]]*hl,
                                                           [[]]*al,[[]]*al,[[]]*al]
    header = ['ID','AvgGF','AvgGA','XG','AvgPoss','AvgSH','AvgSOT','AvgDist','AvgFK','AvgPK','AvgPKAtt']

    #Loop through each match and update data
    #Start at row 11 (i.e. window size +1), and use the first 10 (i.e. window size) 
    #entries to build starting stats
    row_ind = window
    while row_ind<len(full):
        
        #Update rolling stats for full history
        #Full history lookback
        roll_all_full[row_ind-window]=[full.loc[row_ind]['ID'],
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomeGoal'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwayGoal'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['AwayGoal'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['HomeGoal'].sum())/row_ind,
            full.loc[row_ind]['HomeXG'] if full.loc[row_ind]['Home']==team else full.loc[row_ind]['AwayXG'],                           
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomePoss'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwayPoss'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomeSH'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwaySH'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomeSOT'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwaySOT'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomeDist'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwayDist'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomeFK'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwayFK'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomePK'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwayPK'].sum())/row_ind,
            (full.loc[range(0,row_ind)].query(f"Home=='{team}'")['HomePKAtt'].sum() + full.loc[range(0,row_ind)].query(f"Home!='{team}'")['AwayPKAtt'].sum())/row_ind
        ]

        #Windowed lookback
        roll_window_full[row_ind-window]=[full.loc[row_ind]['ID'],
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomeGoal'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwayGoal'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['AwayGoal'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['HomeGoal'].sum())/window,
            full.loc[row_ind]['HomeXG'] if full.loc[row_ind]['Home']==team else full.loc[row_ind]['AwayXG'],                           
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomePoss'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwayPoss'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomeSH'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwaySH'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomeSOT'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwaySOT'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomeDist'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwayDist'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomeFK'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwayFK'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomePK'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwayPK'].sum())/window,
            (full.loc[range(row_ind-window,row_ind)].query(f"Home=='{team}'")['HomePKAtt'].sum() + full.loc[range(row_ind-window,row_ind)].query(f"Home!='{team}'")['AwayPKAtt'].sum())/window
        ]

        myprint(f'Processing {team}-Full{"."*(row_ind%5+1)}',clear=True)
        row_ind += 1
    
    roll_all_full_df = pd.DataFrame(roll_all_full, columns=header)
    roll_all_full_df = roll_all_full_df.round(3)
    roll_all_full_df.astype({'ID':int})
    roll_all_full_df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/Roll_All_Full.csv'),index=False)
    roll_window_full_df = pd.DataFrame(roll_window_full, columns=header)
    roll_window_full_df = roll_window_full_df.round(3)
    roll_window_full_df.astype({'ID':int})
    roll_window_full_df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/Roll_Window_Full.csv'),index=False)

    #Repeat for home-only data
    row_ind = window
    while row_ind<len(home):
        #Full history lookback
        roll_all_home[row_ind-window]=[int(home.loc[row_ind]['ID']),
            home.loc[range(0,row_ind)]['HomeGoal'].mean(),
            home.loc[range(0,row_ind)]['AwayGoal'].mean(),
            home.loc[row_ind]['HomeXG'],
            home.loc[range(0,row_ind)]['HomePoss'].mean(),
            home.loc[range(0,row_ind)]['HomeSH'].mean(),
            home.loc[range(0,row_ind)]['HomeSOT'].mean(),
            home.loc[range(0,row_ind)]['HomeDist'].mean(),
            home.loc[range(0,row_ind)]['HomeFK'].mean(),
            home.loc[range(0,row_ind)]['HomePK'].mean(),
            home.loc[range(0,row_ind)]['HomePKAtt'].mean(),
        ]

        #Windowed lookback
        roll_window_home[row_ind-window]=[int(home.loc[row_ind]['ID']),
            home.loc[range(row_ind-window,row_ind)]['HomeGoal'].mean(),
            home.loc[range(row_ind-window,row_ind)]['AwayGoal'].mean(),
            home.loc[row_ind]['HomeXG'],
            home.loc[range(row_ind-window,row_ind)]['HomePoss'].mean(),
            home.loc[range(row_ind-window,row_ind)]['HomeSH'].mean(),
            home.loc[range(row_ind-window,row_ind)]['HomeSOT'].mean(),
            home.loc[range(row_ind-window,row_ind)]['HomeDist'].mean(),
            home.loc[range(row_ind-window,row_ind)]['HomeFK'].mean(),
            home.loc[range(row_ind-window,row_ind)]['HomePK'].mean(),
            home.loc[range(row_ind-window,row_ind)]['HomePKAtt'].mean(),
        ]

        myprint(f'Processing {team}-Home{"."*(row_ind%5+1)}',clear=True)
        row_ind += 1

    roll_all_home_df = pd.DataFrame(roll_all_home, columns=header)
    roll_all_home_df = roll_all_home_df.round(3)
    roll_all_home_df.astype({'ID':int})
    roll_all_home_df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/Roll_All_Home.csv'),index=False)
    roll_window_home_df = pd.DataFrame(roll_window_home, columns=header)
    roll_window_home_df = roll_window_home_df.round(3)
    roll_window_home_df.astype({'ID':int})
    roll_window_home_df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/Roll_Window_Home.csv'),index=False)

    #Repeat for away-only data
    row_ind = window
    while row_ind<len(away):
        #Full History lookback
        roll_all_away[row_ind-window]=[int(away.loc[row_ind]['ID']),
            away.loc[range(0,row_ind)]['AwayGoal'].mean(),
            away.loc[range(0,row_ind)]['HomeGoal'].mean(),
            away.loc[row_ind]['AwayXG'],
            away.loc[range(0,row_ind)]['AwayPoss'].mean(),
            away.loc[range(0,row_ind)]['AwaySH'].mean(),
            away.loc[range(0,row_ind)]['AwaySOT'].mean(),
            away.loc[range(0,row_ind)]['AwayDist'].mean(),
            away.loc[range(0,row_ind)]['AwayFK'].mean(),
            away.loc[range(0,row_ind)]['AwayPK'].mean(),
            away.loc[range(0,row_ind)]['AwayPKAtt'].mean(),
        ]

        #Windowed lookback
        roll_window_away[row_ind-window]=[int(away.loc[row_ind]['ID']),
            away.loc[range(row_ind-window,row_ind)]['AwayGoal'].mean(),
            away.loc[range(row_ind-window,row_ind)]['HomeGoal'].mean(),
            away.loc[row_ind]['AwayXG'],
            away.loc[range(row_ind-window,row_ind)]['AwayPoss'].mean(),
            away.loc[range(row_ind-window,row_ind)]['AwaySH'].mean(),
            away.loc[range(row_ind-window,row_ind)]['AwaySOT'].mean(),
            away.loc[range(row_ind-window,row_ind)]['AwayDist'].mean(),
            away.loc[range(row_ind-window,row_ind)]['AwayFK'].mean(),
            away.loc[range(row_ind-window,row_ind)]['AwayPK'].mean(),
            away.loc[range(row_ind-window,row_ind)]['AwayPKAtt'].mean(),
        ]

        myprint(f'Processing {team}-Away{"."*(row_ind%5+1)}',clear=True)
        row_ind += 1

    
    
    roll_all_away_df = pd.DataFrame(roll_all_away, columns=header)
    roll_all_away_df = roll_all_away_df.round(3)
    roll_all_away_df.astype({'ID':int})
    roll_all_away_df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/Roll_All_Away.csv'),index=False)
    roll_window_away_df = pd.DataFrame(roll_window_away, columns=header)
    roll_window_away_df = roll_window_away_df.round(3)
    roll_window_away_df.astype({'ID':int})
    roll_window_away_df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/Roll_Window_Away.csv'),index=False)
    
    myprint(f'{team} Processed.',clear=True)