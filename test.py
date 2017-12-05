from qlearningAgents import ApproximateQAgent
import pickle
import numpy as np
from extractors import *
import copy


np.random.seed(1337)

#print "TESTING"
#print q.runTest()

feature_sets = [Try1]

for feature_set in feature_sets:
    q = ApproximateQAgent(featExtractor=feature_set)
    test = q.testAndTrain(n_iter=2000)
    print test