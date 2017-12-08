from qlearningAgents import ApproximateQAgent
import pickle
import numpy as np
from extractors import *
import copy

# seed the random number generator so that we can duplicate the results
np.random.seed(1337)

# define which feature sets from extractors.py we should train and test
feature_sets = [Try1, Try2]

# run training and testing for all defined feature_sets
for feature_set in feature_sets:
	# initialize a new q-learning agent with the desired feature extractor
    q = ApproximateQAgent(featExtractor=feature_set)
    # run the tests
    test = q.testAndTrain(n_train=2000, n_test=100)
    