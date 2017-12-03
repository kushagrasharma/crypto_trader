def reward(state, action):
	if action == "hold":
		if state["bitcoin"] > 0:
			return 0
		else: 
			return 0
	elif action == "buy":
		return 0
	else:
		return (state["total_in_usd"] - state["assets_at_buy"]) / state["assets_at_buy"]