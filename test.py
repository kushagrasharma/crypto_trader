from qlearningAgents import ApproximateQAgent
import pickle
import numpy as np
from extractors import *
import copy


np.random.seed(1337)



# print "TRAINING"
# for i in range(2000):
#     print "{}    {}".format(i, q.runEpisode())

#print "TESTING"
#print q.runTest()

feature_sets = [Try2]

for feature_set in feature_sets:
    q = ApproximateQAgent(featExtractor=feature_set)
    test = q.testAndTrain(n_iter=2000)
    print test