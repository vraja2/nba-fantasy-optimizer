import csv
from pprint import pprint

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

players = []
with open('../data/bob.csv', 'rU') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    if row['year'] in ['2013']:
      features = []
      for i, key in enumerate(sorted(row.keys(), key=str)):
        if key != 'curr-eff':
          if is_number(row[key]):
            features.append((i+1, float(row[key])))
      player = (float(row['curr-eff']), features, 1)
      players.append(player)

pprint(players)