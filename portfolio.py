from market import BitcoinMarket

class Portfolio():
	def __init__(self, funds=10000, bitcoin=0):
		self.market = BitcoinMarket()
		self.originalFunds = funds
		self.funds = funds
		self.bitcoin = bitcoin
		self.history = []
		self.assets_at_buy = None
		self.initial_bitcoin_price = self.market.getCurrentMarketInfo()["weighted_price"]

	def getCurrentState(self):
		""" 
		Returns a dictionary of the current portfolio and market information.
		Available fields include:
	    	- market (BitcoinMarket object)
	    	- funds
	    	- bitcoin
	    	- assets_at_buy
	    	- total_in_usd
	    	- initial_bitcoin_price
		"""
		portfolioInfo = {
			"market" : self.market,
			"funds" : self.funds,
			"bitcoin" : self.bitcoin,
			"assets_at_buy" : self.assets_at_buy,
			"total_in_usd" : self.funds + self.bitcoin * self.market.getCurrentMarketInfo()["weighted_price"],
			"initial_bitcoin_price" : self.initial_bitcoin_price,
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
		"""
			Given a string indicating an action, this takes the respective action
		"""
		if action == "buy":
			return self.buy()
		elif action == "sell":
			return self.sell()
		elif action == "hold":
			return self.hold()

	def buy(self):
		"""
			Buys all bitcoin and increments time one step
		"""
		marketInfo = self.market.getCurrentMarketInfo()
		if self.funds == 0:
			return False
		bitcoin = self.bitcoin
		self.bitcoin = self.funds / marketInfo["weighted_price"]
		self.funds = 0
		state = self.getCurrentState()
		self.assets_at_buy = state["total_in_usd"]
		self.history.append(["buy", bitcoin, state["total_in_usd"]])
		self.market.incrementTime()
		return True

	def sell(self):
		"""
			Sells all bitcoin and increments time one step
		"""
		if self.bitcoin == 0:
			return False
		marketInfo = self.market.getCurrentMarketInfo()
		bitcoin = self.bitcoin
		self.funds = self.bitcoin * marketInfo["weighted_price"]
		self.bitcoin = 0
		state = self.getCurrentState()
		self.history.append(["sell", bitcoin, state["total_in_usd"]])
		self.market.incrementTime()
		return True

	def hold(self):
		"""
			Holds portfolio the same and increments time one step
		"""
		self.market.incrementTime()
		state = self.getCurrentState()
		self.history.append(["hold", 0, state["total_in_usd"]])
		return True

	def reset(self, lowerbound, upperbound):
		"""
			Resets portfolio, picks random start time
		"""
		self.funds = self.originalFunds
		self.bitcoin = 0
		self.history = []

		self.market.setSampledTimestamp(lowerbound, upperbound)
		self.initial_bitcoin_price = self.market.getCurrentMarketInfo()["weighted_price"]

