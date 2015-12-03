import json
from sklearn import linear_model

class LinearReg:

  def __init__(self, train_features, train_eff):
    self.train_features = train_features
    self.train_eff = train_eff
    self.create_model()

  def create_model(self):
    self.clf = linear_model.LinearRegression()
    self.clf.fit(self.train_features, self.train_eff) 
