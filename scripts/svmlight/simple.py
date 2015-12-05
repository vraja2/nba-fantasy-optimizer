import svmlight

training_data = __import__('data').train
test_data = __import__('data').test

# train a model based on the data
model = svmlight.learn(training_data, type='ranking', verbosity=0)

# classify the test data. this function returns a list of numbers, which represent
# the classifications.
predictions = svmlight.classify(model, test_data)
for p in predictions:
    print '%.8f' % p
