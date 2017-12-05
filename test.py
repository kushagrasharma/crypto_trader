from qlearningAgents import ApproximateQAgent
import pickle
import numpy as np


np.random.seed(1337)
with open('results/weights.txt') as f:
     weights = pickle.load(f)

q = ApproximateQAgent()#weights=weights)

print "TRAINING"
for i in range(50):
    print "{}    {}".format(i, q.runEpisode())

print "TESTING"
print q.runTest()
