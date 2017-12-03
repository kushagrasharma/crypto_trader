

class FeatureExtractor():
	def getFeatures(state, action):
		raise NotImplementedError


class BasicFeatureExtractor(FeatureExtractor):
	def getFeatures(self, state, action):
		"""
			state is a dictionary of the current portfolio and market information.
			Available fields include:
		    	- id
		    	- timestamp
		    	- open
		    	- high
		    	- low
		    	- close
		    	- volume_btc
		    	- volume_currency
		    	- weighted_price 
		    	- funds
		    	- num_bitcoins
		    	- total
		"""
		market = state["market"].getCurrentMarketInfo()
		past = state["market"].getPastMarketInfo(5)
		features = {
			# "volatility": market["high"] - market["low"],
			# "volume_btc": market["volume_btc"],
			# "volume_currency": market["volume_currency"],
			"weighted_price": market["weighted_price"] - past["weighted_price"],
			"action": {"buy" : 3, "hold" : 2, "sell" : 1}[action]
		}
		return features


class MarketFeatureExtractor(FeatureExtractor):
	def getFeatures(state, action):
		market = state["market"]
		# list of market data for current and past 10 timestamps
		marketData = [market.getPastMarketInfo(x) for x in range(11)]
		# Compute deltas TODO
		return None
