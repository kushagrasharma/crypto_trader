from qlearningAgents import ApproximateQAgent
import json

with open('weights.json') as json_data:
    weights = json.load(json_data)

q = ApproximateQAgent(weights=weights)

for i in range(100000):
	print q.runEpisode()
