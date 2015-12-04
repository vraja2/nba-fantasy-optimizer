import json
import numpy as np
import sys
sys.path.append('../models')

from sklearn.cross_validation import KFold

from lin_reg import LinearReg 

# TODO: make this a base class and have various evaluation classes for each model
class Evaluation:

  def __init__(self):
    # maybe instead of per game stats from most recent season, we can use historically weighted stats where we
    # take into account the most recent year as well as improvements over the years
    lr = LinearReg()
    self.evaluate_avg_player_eff_error(lr)
    self.evaluate_avg_player_ranking_error(lr)

  def evaluate_avg_player_eff_error(self, model_obj):
    # train on data from all years, but use k-fold cross validation
    np_eff_vec = np.array(model_obj.eff_vec)
    np_feature_matrix = np.array(model_obj.feature_matrix)
    np_name_vec = np.array(model_obj.name_vec)
    k = 10
    kf = KFold(len(model_obj.eff_vec),n_folds=k)
    fold_num = 0
    avg_fold_error = 0.0
    for train_idx, test_idx in kf:
      feat_train, feat_test = np_feature_matrix[train_idx], np_feature_matrix[test_idx]
      eff_train, eff_test = np_eff_vec[train_idx], np_eff_vec[test_idx]
      test_player_names = np_name_vec[test_idx]
      model_obj.create_model(feat_train, eff_train)
      results = model_obj.export_results(feat_test, eff_test, test_player_names)
      if fold_num == 0:
        print results
      avg_error = self.evaluate_eff_error(results)
      print "Fold {}: {} % error".format(fold_num,avg_error)
      avg_fold_error += avg_error 
      fold_num += 1
    print "Average Error Across Folds = {}".format(avg_fold_error/k)

  def evaluate_avg_player_ranking_error(self, model_obj):
    years = [1985+i for i in range(30)]
    avg_rank_error = 0.0
    for exclude_year in years:
      feat_train = []
      eff_train = []
      feat_test = []
      eff_test = []
      test_player_names = []
      for i,year in enumerate(model_obj.year_vec):
        if year != exclude_year:
          feat_train.append(model_obj.feature_matrix[i])
          eff_train.append(model_obj.eff_vec[i])
        else:
          feat_test.append(model_obj.feature_matrix[i])
          eff_test.append(model_obj.eff_vec[i])
          test_player_names.append(model_obj.name_vec[i])
      model_obj.create_model(feat_train, eff_train)
      results = model_obj.export_results(feat_test, eff_test, test_player_names)
      rank_error = self.evaluate_rank(results)
      avg_rank_error += rank_error
      print "Year {}: Rank Error = {}".format(exclude_year, rank_error)
    print "Avg Rank Error = {}".format(avg_rank_error/len(years))

  def evaluate_rank(self, results):
    pred_tups = []
    real_tups = []
    player_names = []
    for player_name,player_results in results.iteritems():
      pred_tups.append((player_name,player_results["pred"]))
      real_tups.append((player_name,player_results["actual"]))
      player_names.append(player_name)
    pred_tups = sorted(pred_tups,key=lambda x: -x[1])
    real_tups = sorted(real_tups,key=lambda x: -x[1])
    # map from player name to position in sorted lists
    pred_name_to_pos = {}
    real_name_to_pos = {}
    for i,pred_tup in enumerate(pred_tups):
      real_tup = real_tups[i]
      pred_name_to_pos[pred_tup[0]] = i
      real_name_to_pos[real_tup[0]] = i
    avg_rank_diff = 0.0
    for name in player_names:
      diff = abs(pred_name_to_pos[name]-real_name_to_pos[name])
      avg_rank_diff += abs(pred_name_to_pos[name]-real_name_to_pos[name])
    avg_rank_diff /= len(player_names)
    return avg_rank_diff

  def evaluate_eff_error(self, results):
    avg_error_percent = 0.0
    num_players = 0
    for player_name,player_results in results.iteritems():
      if player_results["actual"] >= 0.1:
        avg_error_percent += abs(player_results["actual"]-player_results["pred"])/player_results["actual"]
        num_players += 1
    return avg_error_percent/num_players*100
    
if __name__ == "__main__":
  e = Evaluation()
