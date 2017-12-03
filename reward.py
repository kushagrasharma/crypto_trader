"""
def reward(state, action, nextState):
	if action == "hold":
		if state["bitcoin"] > 0:
			return -1
		else: 
			return 0
	elif action == "buy":
		return -1
	else:
		return (state["total_in_usd"] - state["assets_at_buy"]) / state["assets_at_buy"]

"""
def reward(history):
    if len(history) < 2:
        return 0
    return history[-1][2] - history[-2][2]
 	#return nextState["total_in_usd"] - state["total_in_usd"]