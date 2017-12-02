from market import BitcoinMarket

class Portfolio():
	def __init__(self, funds=10000, bitcoin=0):
		self.market = BitcoinMarket()
		self.originalFunds = funds
		self.funds = funds
		self.bitcoin = bitcoin
		self.history = []
		self.assets_at_buy = None

	def getCurrentState(self):
		""" 
		Returns a dictionary of the current portfolio and market information.
		Available fields include:
	    	- market (BitcoinMarket object)
	    	- funds
	    	- bitcoin
	    	- total_in_usd
		"""
		portfolioInfo = {
			"market" : self.market,
			"funds" : self.funds,
			"bitcoin" : self.bitcoin,
			"assets_at_buy" : self.assets_at_buy,
			"total_in_usd" : self.funds + self.bitcoin * self.market.getCurrentMarketInfo()["weighted_price"]
		}
		return portfolioInfo

	def getLegalActions(self, state):
		# In any state, you are always allowed to do nothing
		actions = ["hold"]
		if self.funds > 0:
			actions.append("buy")
		if self.bitcoin > 0:
			actions.append("sell")
		return actions
	
	def getHistory(self):
		return self.history

	def takeAction(self, action):
		# TODO fix these values
		if action == "buy":
			return self.buy(1)
		elif action == "sell":
			return self.sell(1)
		elif action == "hold":
			return self.hold()

	def buy(self, bitcoin):
		marketInfo = self.market.getCurrentMarketInfo()
		if marketInfo["weighted_price"] * bitcoin > self.funds:
			return False
		self.funds -= marketInfo["weighted_price"] * bitcoin
		self.bitcoin += bitcoin
		state = self.getCurrentState()
		self.assets_at_buy = state["total_in_usd"]
		self.history.append(["buy", bitcoin, state["total_in_usd"]])
		self.market.incrementTime()
		return True

	def sell(self, bitcoin):
		if bitcoin > self.bitcoin:
			return False
		marketInfo = self.market.getCurrentMarketInfo()
		self.bitcoin -= bitcoin
		self.funds += bitcoin * marketInfo["weighted_price"]
		state = self.getCurrentState()
		self.history.append(["sell", -1 * bitcoin, state["total_in_usd"]])
		self.market.incrementTime()
		return True

	def hold(self):
		self.market.incrementTime()
		state = self.getCurrentState()
		self.history.append(["hold", 0, state["total_in_usd"]])
		return True

	def reset(self, upperbound):
		"""
			Resets portfolio, picks random start time
		"""
		self.funds = self.originalFunds
		self.bitcoin = 0
		self.history = []
		self.market.setSampledTimestamp(upperbound)
