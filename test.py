from qlearningAgents import ApproximateQAgent
q = ApproximateQAgent()


for i in range(50):
	print q.runEpisode()
