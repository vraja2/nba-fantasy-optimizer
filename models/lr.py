import json
import numpy as np
from pprint import pprint
from sklearn import linear_model

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

with open('../data/seasonStats.json') as data_file:
  data = json.load(data_file)
  years = data.keys()
  A = []
  b = []
  years = sorted(years, key=int)
  for year in years[-10:-2]:
    player_next_year_eff = 0
    playerNames = data[year].keys()
    for playerName in playerNames:
      playerStats = data[year][playerName]
      statTypes = sorted(playerStats.keys(), key=str)
      eff = 0
      next_year = unicode(str(int(year) + 1), "utf-8")
      if playerName in data[next_year]:
        statsVector = []
        for statType in statTypes: # ex. Total
          statNames = sorted(data[year][playerName][statType], key=str)
          for statName in statNames: # ex. PTS
            if statName in data[next_year][playerName][statType]:
              stat = data[year][playerName][statType][statName]
              next_year_stat = data[next_year][playerName][statType][statName]
              if is_number(stat):
                statsVector.append(float(stat))
                if statType == "per_game":
                  if statName in ["PTS", "TRB", "AST", "STL", "BLK", "FG", "FT"]:
                    eff += float(next_year_stat)
                  if statName in ["FGA", "FTA", "TOV"]:
                    eff -= float(next_year_stat)
              else:
                statsVector.append(0)

        b.append(eff)
        A.append(statsVector)

  A = np.array(A)
  b = np.array(b)
  clf = linear_model.LinearRegression()
  clf.fit(A, b)

  year_to_predict = years[-2]
  year_to_predict_next_year = unicode(str(int(year_to_predict) + 1), "utf-8")
  leaderboard = []
  for player_in_question in data[year].keys():
    if player_in_question in data[year_to_predict] and player_in_question in data[year_to_predict_next_year]:
      player_stats_in_question = []
      player_predicted_eff = 0
      for statType in statTypes:
        statNames = sorted(data[year_to_predict][player_in_question][statType], key=str)
        for statName in statNames:
          stat = data[year_to_predict][player_in_question][statType][statName]
          next_year_stat = data[year_to_predict_next_year][player_in_question][statType][statName]
          if is_number(stat):
            player_stats_in_question.append(float(stat))
            if statType == "per_game":
              if statName in ["PTS", "TRB", "AST", "STL", "BLK", "FG", "FT"]:
                player_predicted_eff += float(next_year_stat)
              if statName in ["FGA", "FTA", "TOV"]:
                player_predicted_eff -= float(next_year_stat)
          else:
            player_stats_in_question.append(0)

      predicted = np.dot(player_stats_in_question, clf.coef_) + clf.intercept_
      actual = player_predicted_eff
      leaderboard.append((player_in_question, predicted, actual))

pprint(sorted(leaderboard, key=lambda x: -x[1]))