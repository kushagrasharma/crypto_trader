def reward(state, action):
	if state["numBitcoin"] == 0:
		return 0