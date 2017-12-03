import pandas as pd

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
		past15 = state["market"].getPastMarketInfo(15)
		pastDay = state["market"].getPastMarketInfo(1440)
		features = {
			# "volatility": market["high"] - market["low"],
			# "volume_btc": market["volume_btc"],
			# "volume_currency": market["volume_currency"],
			"delta_15_minutes": market["weighted_price"] - past15["weighted_price"],
			"delta_24_hours": market["weighted_price"] - pastDay["weighted_price"],
			"willr" : (market["high"] - market["close"]) / (market["high"] - market["low"]) * 100,
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



class Try1(FeatureExtractor):
	def getFeatures(self, state, action):
		market = state["market"].getCurrentMarketInfo()
		past15 = state["market"].getPastMarketInfo(15)
		pastDay = state["market"].getPastMarketInfo(1440)
		return {
			"1" : willr(state, action),
			"2" : rocr(state, action, 15),
			"3" : rocr(state, action, 60),
			"4" : rocr(state, action, 1440),
			"5" : momentum(state, action, 15),
			"6" : momentum(state, action, 60),
			"7" : momentum(state, action, 1440),
			"8" : {"buy" : 3, "hold" : 2, "sell" : 1}[action],
			"9": market["weighted_price"] - past15["weighted_price"],
			"10": market["weighted_price"] - pastDay["weighted_price"]
		}


def willr(state, action):
	"""
		Determines where today's closing price fell within the range on past 10-day's transaction. 
	"""
	market = state["market"]
	cur = market.getCurrentMarketInfo()
	past = [market.getPastMarketInfo(i) for i in range(10)]
	high = max([x["high"] for x in past])
	low = min([x["low"] for x in past])

	if high - low == 0:
		return 0
	return (high - cur["close"]) / (high - low) * 100

def rocr(state, action, n):
	"""
		Compute rate of change relative to previous trading intervals
	"""
	market = state["market"].getCurrentMarketInfo()
	pastN = state["market"].getPastMarketInfo(n)
	return (market["weighted_price"] / pastN["weighted_price"]) * 100

def momentum(state, action, n):
	"""
		Measures the change in price
	"""
	market = state["market"]
	cur = market.getCurrentMarketInfo()
	past = market.getPastMarketInfo(n)
	return cur["weighted_price"] - past["weighted_price"]

def RSI(state, window_length=14):
	pasts = []
	for i in range(window_length, 0, -1):
		pasts.append(state["market"].getPastMarketInfo(1440*i).close)
	pasts = pd.Series(pasts)
	delta = pasts.diff() 
	delta = delta[1:]
	up, down = delta.copy(), delta.copy()
	up[up < 0] = 0
	down[down > 0] = 0
	roll_up1 = pd.stats.moments.ewma(up, window_length)
	roll_down1 = pd.stats.moments.ewma(down.abs(), window_length)
	RS1 = roll_up1 / roll_down1
	return (100.0 - (100.0 / (1.0 + RS1))).iloc[-1]
