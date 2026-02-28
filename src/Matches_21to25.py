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
rawcsv = OSpath('../data/raw/final_matches.csv')
proccsv = OSpath('../data/processed/final_matches.csv')
procxlsx = OSpath('../data/processed/final_matches.xlsx')
matchdb = OSpath('../data/processed/Matches_21to25.db')
matchcsv = OSpath('../data/processed/Matches_21to25.csv')
matchxlsx = OSpath('../data/processed/Matches_21to25.xlsx')


#Initialize DB file
try:
    #Delete old .db if it exists
    os.system(OScom('rm')+f' {matchdb}')
except:
    pass
DB = sqlite3.connect(matchdb)
sql = DB.cursor()


#Load in Text Spreadsheets
text = pd.read_csv(f"{rawcsv}")#,na_filter=False)
#Sort data by date, then time, then ref, the venue so that every pair of rows
#is a single match showing the home stats then the away stats
text = text.sort_values(by=['date', 'time', 'referee', 'venue'],
                        ascending = [True, True, True, False])
text.reset_index(drop=True, inplace=True)
#Dist has at least one empty entry, replace it with 0
text['dist'] = text['dist'].replace(np.nan,0.)
#Output the cleaned and sorted datafile
text.to_excel(procxlsx,index=False,sheet_name='final_matches')
text.to_csv(proccsv,index=False,sep=',')

#Get unique teams and create TEAM table
teams = np.sort(text['team'].unique())
sql.execute("CREATE TABLE TEAM (ID INT PRIMARY KEY,"+
            "Team VARCHAR NOT NULL);")
sql.executemany("INSERT INTO TEAM VALUES (?,?)", zip(range(1,len(teams)+1),teams))

#Get unique venues and create VENUE table
#venues = np.sort(text['venue'].unique())
sql.execute("CREATE TABLE VENUE (ID INT PRIMARY KEY,"+
            "Venue VARCHAR NOT NULL);")
sql.executemany("INSERT INTO VENUE VALUES (?,?)", [(1,'Home'),(2,'Away')])#zip(range(1,len(venues)+1),venues))

#Get unique days and create DAY table
days = np.array(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])#days = np.sort(text['day'].unique())
sql.execute("CREATE TABLE DAY (ID INT PRIMARY KEY,"+
            "Day VARCHAR NOT NULL);")
sql.executemany("INSERT INTO DAY VALUES (?,?)", zip(range(1,len(days)+1),days))

#Get unique captains and create CAPTAIN table
cpts = np.sort(text['captain'].unique())
sql.execute("CREATE TABLE CAPTAIN (ID INT PRIMARY KEY,"+
            "Captain VARCHAR NOT NULL);")
sql.executemany("INSERT INTO CAPTAIN VALUES (?,?)", zip(range(1,len(cpts)+1),cpts))

#Get unique formations and create FORMATION table
forms = np.sort(pd.concat([text['formation'],text['opp formation']]).unique())
sql.execute("CREATE TABLE FORMATION (ID INT PRIMARY KEY,"+
            "Formation VARCHAR NOT NULL);")
sql.executemany("INSERT INTO FORMATION VALUES (?,?)", zip(range(1,len(forms)+1),forms))

#Get unique referees and create REFEREE table
refs = np.sort(text['referee'].unique())
sql.execute("CREATE TABLE REFEREE (ID INT PRIMARY KEY,"+
            "Referee VARCHAR NOT NULL);")
sql.executemany("INSERT INTO REFEREE VALUES (?,?)", zip(range(1,len(refs)+1),refs))

#Get unique season and create SEASON table
seasons = np.array([str(x) for x in np.sort(text['season'].unique())])
sql.execute("CREATE TABLE SEASON (ID INT PRIMARY KEY,"+
            "Season VARCHAR NOT NULL);")
sql.executemany("INSERT INTO SEASON VALUES (?,?)", zip(range(1,len(seasons)+1),seasons))


#Match Table (Primary)
sql.execute("CREATE TABLE MATCH (ID INT PRIMARY KEY,"+
            "SeasonID INT NOT NULL,"+
            "Round INT NOT NULL,"+
            "HomeID INT NOT NULL,"+
            "AwayID INT NOT NULL,"+
            "HomeWin INT NOT NULL,"+
            "AwayWin INT NOT NULL,"+
            "Draw INT NOT NULL,"+
            "HomeGoal INT NOT NULL,"+
            "AwayGoal INT NOT NULL,"+
            "HomeXG REAL NOT NULL,"+
            "AwayXG REAL NOT NULL,"+
            "HomePoss INT NOT NULL,"+
            "AwayPoss INT NOT NULL,"+
            "HomeCaptID INT NOT NULL,"+
            "HomeFormID INT NOT NULL,"+
            "HomeSH INT NOT NULL,"+
            "HomeSOT INT NOT NULL,"+
            "HomeAcc REAL,"+
            "HomeDef REAL,"+
            "HomeDist REAL NOT NULL,"+
            "HomeFK INT NOT NULL,"+
            "HomePK INT NOT NULL,"+
            "HomePKAtt INT NOT NULL,"+
            "AwayCaptID INT NOT NULL,"+
            "AwayFormID INT NOT NULL,"+
            "AwaySH INT NOT NULL,"+
            "AwaySOT INT NOT NULL,"+
            "AwayAcc REAL,"+
            "AwayDef REAL,"+
            "AwayDist REAL NOT NULL,"+
            "AwayFK INT NOT NULL,"+
            "AwayPK INT NOT NULL,"+
            "AwayPKAtt INT NOT NULL,"+
            "RefID INT NOT NULL,"+
            "Date VARCHAR NOT NULL,"+
            "DayID INT NOT NULL,"+
            "Time VARCHAR NOT NULL);")

def Acc(sh,sot):
    return(0. if sh==0 else float(sot/sh))
def Def(gf,sot):
    return(0. if sot==0 else float((sot-gf)/sot))
#Read through spreadsheet and populate the Match Table
row_ind,match_id = 0,1
while row_ind<len(text)-1:
    home = text.loc[row_ind]
    away = text.loc[row_ind+1]

    dbentry = [match_id,                                            #Match ID
            int(np.where(seasons==str(home['season']))[0][0])+1,    #Season ID
            int(home['round'].split()[1]),                          #Round Number
            int(np.where(teams==str(home['team']))[0][0])+1,        #Home Team ID
            int(np.where(teams==str(away['team']))[0][0])+1,        #Away Team ID
            0 if home['result'] in ['L','D'] else 1,                #Home Win
            0 if away['result'] in ['L','D'] else 1,                #Away Win
            0 if home['result']!='D' else 1,                        #Draw
            int(home['gf']),                                        #Home Goals
            int(away['gf']),                                        #Away Goals
            float(home['xg']),                                      #Home XG
            float(away['xg']),                                      #Away XG
            int(home['poss']),                                      #Home Poss
            int(away['poss']),                                      #Away Poss
            int(np.where(cpts==str(home['captain']))[0][0])+1,      #Home Captain
            int(np.where(forms==str(home['formation']))[0][0])+1,   #Home Formation
            int(home['sh']),                                        #Home SH
            int(home['sot']),                                       #Home SOT
            Acc(int(home['sh']),int(home['sot'])),                  #Home Accuracy
            Def(int(away['gf']),int(away['sot'])),                  #Home Defense
            float(home['dist']),                                    #Home Dist
            int(home['fk']),                                        #Home FK
            int(home['pk']),                                        #Home PK
            int(home['pkatt']),                                     #Home PKAtt
            int(np.where(cpts==str(away['captain']))[0][0])+1,      #Away Captain
            int(np.where(forms==str(away['formation']))[0][0])+1,   #Away Formation
            int(away['sh']),                                        #Away SH
            int(away['sot']),                                       #Away SOT
            Acc(int(away['sh']),int(away['sot'])),                  #Home Accuracy
            Def(int(home['gf']),int(home['sot'])),                  #Home Defense
            float(away['dist']),                                    #Away Dist
            int(away['fk']),                                        #Away FK
            int(away['pk']),                                        #Away PK
            int(away['pkatt']),                                     #Away PKAtt
            int(np.where(refs==str(home['referee']))[0][0])+1,      #Referee
            home['date'],                                           #Date
            int(np.where(days==str(home['day']))[0][0])+1,          #Day
            home['time']                                            #Time
            ]

    sql.execute(f"INSERT INTO MATCH VALUES "+ str(tuple(dbentry)))
    match_id += 1
    row_ind += 2
    
#Commit and Close DB for posterity
DB.commit()
DB.close()

#Reopen DB to query and export formatted table to Excel
DB = sqlite3.connect(matchdb)

#Query for full formatted table
query = '''
SELECT DISTINCT M.ID, SEASON.Season, M.Round, t1.Team AS Home, t2.Team AS Away, M.HomeWin,
M.AwayWin, M.Draw, M.HomeGoal, M.AwayGoal, M.HomeXG, M.AwayXG, M.HomePoss, M.AwayPoss,
c1.Captain AS HomeCaptain, f1.Formation AS HomeFormation,
M.HomeSH, M.HomeSOT, M.HomeAcc, M.HomeDef, M.HomeDist, M.HomeFK, M.HomePK, M.HomePKAtt,
c2.Captain AS AwayCaptain, f2.Formation AS AwayFormation,
M.AwaySH, M.AwaySOT, M.AwayAcc, M.AwayDef, M.AwayDist, M.AwayFK, M.AwayPK, M.AwayPKAtt,
REFEREE.Referee, M.Date, DAY.Day, M.Time FROM MATCH M
JOIN SEASON ON SEASON.ID=M.SeasonID
JOIN REFEREE ON REFEREE.ID=M.RefID
JOIN DAY ON DAY.ID=M.DayID
JOIN TEAM t1 ON t1.ID=M.HomeID JOIN TEAM t2 ON t2.ID=M.AwayID
JOIN CAPTAIN c1 ON c1.ID=M.HomeCaptID JOIN CAPTAIN c2 ON c2.ID=M.AwayCaptID
JOIN FORMATION f1 ON f1.ID=M.HomeFormID JOIN FORMATION f2 ON f2.ID=M.AwayFormID
ORDER BY M.ID ASC
'''
#Execute query and save output
df = pd.read_sql(query,DB)
df.to_excel(matchxlsx,index=False,sheet_name='Matches')
df.to_csv(matchcsv,index=False,sep=',')

DB.close()