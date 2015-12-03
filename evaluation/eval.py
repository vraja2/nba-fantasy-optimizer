import json
import numpy as np
import sys
sys.path.append('../models')

from sklearn.cross_validation import KFold

from lin_reg import LinearReg 

# TODO: make this a base class and have various evaluation classes for each model
class Evaluation:

  def __init__(self):
    with open('../data/seasonStats.json') as stats:    
      self.stats = json.load(stats)
    self.year = 2015
    self.construct_data_sets()
    self.evaluate_avg_player_eff_error()
    self.evaluate_avg_player_ranking_error()

  def construct_data_sets(self):
    self.feature_matrix = []
    self.eff_vec = []
    self.year_vec = []
    self.name_vec = []
    for year,player_stats in self.stats.iteritems():
      next_year = str(int(year)+1)
      if float(year) < self.year:
        next_yr_stats = self.stats[next_year]
        for player_name,stat_cats in player_stats.iteritems():
          if player_name in self.stats[next_year]:
            feat_vec = []
            per_game_stats = stat_cats["per_game"]
            next_year_per_game_stats = next_yr_stats[player_name]["per_game"]
            eff = 0.0
            for stat_name, stat_val in per_game_stats.iteritems():
              if stat_name in ["PTS","TRB","AST","STL","BLK","FG","FT","FGA","FTA","TOV"]:
                feat_vec.append(float(stat_val))
            for stat_name, stat_val in next_year_per_game_stats.iteritems():
              if stat_name in ["PTS","TRB","AST","STL","BLK","FG","FT"]:
                eff += float(stat_val)
              elif stat_name in ["FGA", "FTA", "TOV"]:
                eff -= float(stat_val)
            self.name_vec.append(player_name)
            self.eff_vec.append(eff)
            self.feature_matrix.append(feat_vec)
            self.year_vec.append(int(year))

  def evaluate_avg_player_eff_error(self):
    # train on data from all years, but use k-fold cross validation
    np_eff_vec = np.array(self.eff_vec)
    np_feature_matrix = np.array(self.feature_matrix)
    kf = KFold(len(self.eff_vec),n_folds=10)
    fold_num = 0
    for train_idx, test_idx in kf:
      feat_train, feat_test = np_feature_matrix[train_idx], np_feature_matrix[test_idx]
      eff_train, eff_test = np_eff_vec[train_idx], np_eff_vec[test_idx]
      lr_model = LinearReg(feat_train, eff_train)
      avg_error = self.evaluate_model(lr_model, feat_test, eff_test)
      print "Fold {}: {} % error".format(fold_num,avg_error)
      fold_num += 1
  
  def evaluate_avg_player_ranking_error(self):
    years = [1985+i for i in range(30)]
    for exclude_year in years:
      feat_train = []
      eff_train = []
      feat_test = []
      eff_test = []
      test_player_names = []
      for i,year in enumerate(self.year_vec):
        if year != exclude_year:
          feat_train.append(self.feature_matrix[i])
          eff_train.append(self.eff_vec[i])
        else:
          feat_test.append(self.feature_matrix[i])
          eff_test.append(self.eff_vec[i])
          test_player_names.append(self.name_vec[i])
      lr_model = LinearReg(feat_train, eff_train)
      avg_rank_error = self.evaluate_rank(lr_model, feat_test, eff_test, test_player_names)
      print "Year {}: Rank Error = {}".format(exclude_year, avg_rank_error)

  def evaluate_rank(self, model, features, eff, player_names):
    pred_tups = []
    real_tups = []
    for i,feature in enumerate(features):
      pred_eff = model.clf.predict(feature)
      curr_name = player_names[i]
      pred_tups.append((curr_name,pred_eff))
      real_tups.append((curr_name,eff[i]))
    pred_tups = sorted(pred_tups,key=lambda x: x[1])
    real_tups = sorted(real_tups,key=lambda x: x[1])
    # map from player name to position in sorted lists
    pred_name_to_pos = {}
    real_name_to_pos = {}
    for i,pred_tup in enumerate(pred_tups):
      real_tup = real_tups[i]
      pred_name_to_pos[pred_tup[0]] = i
      real_name_to_pos[real_tup[0]] = i
    avg_rank_diff = 0.0
    for name in player_names:
      avg_rank_diff += abs(pred_name_to_pos[name]-real_name_to_pos[name])
    avg_rank_diff /= len(player_names)
    return avg_rank_diff

  def evaluate_model(self, model, features, eff):
    avg_error_percent = 0.0
    for i,feature in enumerate(features):
      eff_pred = model.clf.predict(feature)
      # so that values aren't incorrectly very large
      if eff[i] >= 0.1:
        avg_error_percent += abs(eff[i]-eff_pred)/eff[i]
    return avg_error_percent/len(features)*100

if __name__ == "__main__":
  e = Evaluation()
