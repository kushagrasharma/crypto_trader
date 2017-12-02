

class FeatureExtractor():
	def getFeatures(state, action):
		raise NotImplementedError


class BasicFeatureExtractor(FeatureExtractor):
	def getFeatures(state, action):
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
		features = {
			"high": state["high"],
			"low": state["low"],
			"open": state["open"],
			"close": state["close"],
			"volume_btc": state["volume_btc"],
			"volume_currency": state["volume_currency"],
			"weighted_price": state["weighted_price"],
			"funds": state["funds"],
			"num_bitcoins": state["num_bitcoins"],
			"total": state["total"],
		}
		return features


class MarketFeatureExtractor(FeatureExtractor):
	def getFeatures(state, action):
		market = state["market"]
		# list of market data for current and past 10 timestamps
		marketData = [market.getPastMarketInfo(x) for x in range(11)]
		# Compute deltas TODO
		return None
