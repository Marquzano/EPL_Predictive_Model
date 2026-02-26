import sqlite3,os
import pandas as pd
import numpy as np
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
    #Remove spaces from team name for file management
    teamfile = ''.join(team.split(' '))

    #Get all data where given team played
    df = text[(text['Home']==team)|(text['Away']==team)]
    df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/AllData.csv'),index=False)

    #Get all data where given team was home
    df = text[text['Home']==team]
    df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/AllData_Home.csv'),index=False)

    #Get all data where given team was away
    df = text[text['Away']==team]
    df.to_csv(OSpath(f'../data/processed/Teams/{teamfile}/AllData_Away.csv'),index=False)