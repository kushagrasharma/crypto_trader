# Reward functions for trading agents

def reward(state, nextState):
	"""
		Reward function for a trading agent
	"""
	# The reward of the current action is the change in total_usd between timestamps
	return nextState["total_in_usd"] - state["total_in_usd"]
