import csv
import json
import svmlight

class SVMRank:

  def __init__(self):
    self.per_game_features = ["per_game-PTS","per_game-TRB","per_game-AST","per_game-STL","per_game-BLK","per_game-FG","per_game-FT","per_game-FGA","per_game-FTA","per_game-TOV"]
    self.construct_datasets()

  def construct_datasets(self):
    self.feature_matrix = []
    self.eff_vec = []
    self.year_vec = []
    self.name_vec = []
    with open('../data/cleanedSeasonStats.csv', 'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        features = []
        feature_num = 1
        for i,key in enumerate(row.keys()):
          if key in self.per_game_features:
            features.append((feature_num, float(row[key])))
            feature_num += 1
        self.feature_matrix.append((float(row['next-eff']), features, int(row['year'])))
        self.eff_vec.append(row['next-eff'])
        self.name_vec.append(row['player'])
        self.year_vec.append(row['year'])
  
  def create_model(self, train_features, train_eff):
    print "Training SVM"
    self.clf = svmlight.learn(train_features, type='ranking', verbosity=0)
    print "Finishing training SVM"

  def export_results(self, test_features, test_player_names):
    predictions = svmlight.classify(self.clf, test_features)
    prediction_tuples = []
    for i,prediction in enumerate(predictions):
      prediction_tuples.append((test_player_names[i],prediction))
    prediction_tuples = sorted(prediction_tuples,key=lambda x: -x[1])
