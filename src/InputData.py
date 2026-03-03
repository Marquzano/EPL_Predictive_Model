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

#Load in Match Data
matches = pd.read_csv(OSpath(f'../data/processed/Matches_21to25.csv'))
#Load in All Team Data and stor in dictionary
teams = dict()
for team in np.sort(matches['Home'].unique()):
    teams[team] = pd.read_csv(OSpath(f"../data/processed/Teams/{''.join(team.split(' '))}/Roll_Season_Full.csv"))

#Get Number of valid matches (i.e. ignore either team's first game of season)
n_val = 0
for i in range(len(matches)):
    m = matches.loc[i]
    if (m['ID'] in teams[m['Home']]['ID'].to_list()) and (m['ID'] in teams[m['Away']]['ID'].to_list()):
        n_val += 1


#Schema: [ [Macro], [[Home],[Awal]], [HW,AW,D] ]
data = [ [[]]*n_val, [[[],[]]]*n_val, [[]]*n_val ]

d_ind = 0
for i in range(len(matches)):
    #Set Macro Data
    m = matches.loc[i]
    if (m['ID'] in teams[m['Home']]['ID'].to_list()) and (m['ID'] in teams[m['Away']]['ID'].to_list()):
        data[0][d_ind] = f"Match {m['ID']}: S{m['Season']}-R{m['Round']} {m['Away']} at {m['Home']}"

        #Get Team Data from Match and trim Match ID
        home = np.array(teams[m['Home']].query(f"ID=={m['ID']}"))[0][1:]
        away = np.array(teams[m['Away']].query(f"ID=={m['ID']}"))[0][1:]
        data[1][d_ind] = np.array([away,home])

        #Get Results
        data[2][d_ind] = np.array([m['HomeWin'], m['AwayWin'], m['Draw']])

        #Update data index
        d_ind += 1


np.save(OSpath(f"../models/InputData.npy"),np.array(data, dtype=object))