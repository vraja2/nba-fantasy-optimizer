import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import math

def get_efficiency(row, category='per_game'):
    return (float(row[category + '-PTS']) + \
            float(row[category + '-TRB']) + \
            float(row[category + '-AST']) + \
            float(row[category + '-STL']) + \
            float(row[category + '-BLK']) + \
            float(row[category + '-FG']) - float(row[category + '-FGA']) + \
            float(row[category + '-FT']) - float(row[category + '-FTA']) - \
            float(row[category + '-TOV']))

def get_next_efficiency(name, year, df):
    if ((df['player'] == name) & (df['year'] == year + 1)).any(): # if the next year is present
        if ((df['player'] == name) & (df['year'] == year + 1) & (df['totals-Tm'] == 'TOT')).any(): # was traded, use TOT
            return df.loc[(df['player'] == name) & (df['year'] == year + 1) & (df['totals-Tm'] == 'TOT'), 'curr-eff'].item()
        else:
            return df.loc[(df['player'] == name) & (df['year'] == year + 1), 'curr-eff'].item()
    else:
        return float('NaN')
df = pd.read_csv('../data/seasonStats.csv')


# remove '*' from player names
df['player'] = [player if player[-1] != '*' else player[:-1] for player in df['player']]

# add effs
df['curr-eff'] = [get_efficiency(row, 'per_game') for index, row in df.iterrows()]
df['next-eff'] = [get_next_efficiency(row['player'], row['year'], df) for index, row in df.iterrows()]

# remove the ones with no next-year data
df = df[[not math.isnan(x) for x in df['next-eff']]]

# write to file'
df.to_csv('../data/cleanedSeasonStats.csv', index=False)
