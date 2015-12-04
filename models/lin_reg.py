import json
from sklearn import linear_model

class LinearReg:
  """
  Weights will tell you how stats for a player in year "a" correspond to 
  efficiency of the same player in year "a+1"
  """

  def __init__(self):
    with open('../data/seasonStats.json') as stats:    
      self.stats = json.load(stats)
    self.year = 2015
    # maybe instead of per game stats from most recent season, we can use historically weighted stats where we
    # take into account the most recent year as well as improvements over the years
    self.per_game_features = ["PTS","TRB","AST","STL","BLK","FG","FT","FGA","FTA","TOV"]
    self.advanced_features = []
    self.custom_features = ["INJ_TREND","PTS_TREND","RB_TREND","AST_TREND","STL_TREND","BLK_TREND", "PT_TREND"]
    # a way to map from custom features to the functions that compute them
    self.custom_feature_to_func = {}
    self.initialize_custom_feature_dict()
    self.construct_data_sets()

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
            advanced_stats = stat_cats["advanced"]
            next_year_per_game_stats = next_yr_stats[player_name]["per_game"]
            eff = 0.0
            for stat_name, stat_val in per_game_stats.iteritems():
              if stat_name in self.per_game_features:
                feat_vec.append(float(stat_val))
            empty_stat = False
            for stat_name, stat_val in advanced_stats.iteritems():
              if stat_name in self.advanced_features:
                if stat_val == "":
                  empty_stat = True
                  break
                feat_vec.append(float(stat_val))
            if empty_stat:
              continue
            for stat_name, stat_val in next_year_per_game_stats.iteritems():
              if stat_name in ["PTS","TRB","AST","STL","BLK","FG","FT"]:
                eff += float(stat_val)
              elif stat_name in ["FGA", "FTA", "TOV"]:
                eff -= float(stat_val)
            self.name_vec.append(player_name)
            self.eff_vec.append(eff)
            self.feature_matrix.append(feat_vec)
            self.year_vec.append(int(year))
  
  def initialize_custom_feature_dict(self):
    self.custom_features = ["INJ_TREND","PTS_TREND","RB_TREND","AST_TREND","STL_TREND","BLK_TREND", "PT_TREND"]
    for feature in self.custom_features:
      if feature.find("TREND") != -1:
        self.custom_feature_to_func[feature] = self.compute_trend
  
  def compute_trend(self,data_over_time):
    # TODO: implement
    pass

  def create_model(self, train_features, train_eff):
    self.clf = linear_model.LinearRegression()
    self.clf.fit(train_features, train_eff)

  def export_results(self, test_features, test_eff, test_player_names):
    score_dict = {}
    for i,feature in enumerate(test_features):
      pred_eff = self.clf.predict(feature)
      curr_name = test_player_names[i]
      curr_dict = {}
      curr_dict["pred"] = pred_eff
      curr_dict["actual"] = test_eff[i]
      score_dict[curr_name] = curr_dict
    return score_dict
