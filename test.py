from qlearningAgents import ApproximateQAgent
import pickle
import numpy as np


np.random.seed(1337)
# with open('weights.txt') as f:
#     weights = pickle.load(f)

q = ApproximateQAgent()#weights=weights)

for i in range(100000):
	print q.runEpisode()
