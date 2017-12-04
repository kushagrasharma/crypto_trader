import pandas as pd
import numpy as np
0
import time

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

class Try2(FeatureExtractor):
	def getFeatures(self, state, action):
		market = state["market"].getCurrentMarketInfo()
		pastHour = state["market"].getPastMarketInfo(4)
		pastDay = state["market"].getPastMarketInfo(4*24)
		d = {
			"1" : market.rsi,
			"2" : market.willr,
			"3" : market.dema,
			"4" : market.chaikinOscillator,
			"5" : market.chaikinLine,
			"6" : market.trueRange,
			"7" : market.linearRegSlope,
			"8" : {"buy" : 3, "hold" : 2, "sell" : 1}[action],
			"9": market["weighted_price"] - pastHour["weighted_price"],
			"10": market["weighted_price"] - pastDay["weighted_price"],
			"11" : market["std"],
			"12" : market.tsf,
		}
		return np.array([d[str(i)] for i in range(1, len(d) + 1)])


# """
# def willr(state, action):
# 	"""
# 		#Determines where today's closing price fell within the range on past 10-day's transaction. 
# 	"""
# 	market = state["market"]
# 	cur = market.getCurrentMarketInfo()
# 	past = [market.getPastMarketInfo(i) for i in range(10)]
# 	high = max([x["high"] for x in past])
# 	low = min([x["low"] for x in past])
# 	if high - low == 0:
# 		return 0
# 	return (high - cur["close"]) / (high - low) * 100

# def rocr(state, action, n):
# 	"""
# 		#Compute rate of change relative to previous trading intervals
# 	"""
# 	market = state["market"].getCurrentMarketInfo()
# 	pastN = state["market"].getPastMarketInfo(n)
# 	return (market["weighted_price"] / pastN["weighted_price"]) * 100

# def momentum(state, action, n):
# 	"""
# 		#Measures the change in price
# 	"""
# 	market = state["market"]
# 	cur = market.getCurrentMarketInfo()
# 	past = market.getPastMarketInfo(n)
# 	return cur["weighted_price"] - past["weighted_price"]

# def RSI_self(state, window_length=14, libr=False):
# 	pasts = []
# 	for i in range(window_length, 0, -1):
# 		pasts.append(state["market"].getPastMarketInfo(1440*i).close)
# 	pasts.append(state['market'].getCurrentMarketInfo().close)
# 	return RSI(pd.DataFrame(pasts, index=np.arange(len(pasts)), columns=['close']), timeperiod=window_length).iloc[-1]
# """
def aggregate(data):
    data.sort_values('timestamp')
    agged = {'timestamp' : data.iloc[0].timestamp, 
             'high' : np.max(data.high),
             'low' : np.min(data.low),
             'close' : data.iloc[-1].close,
             'open' : data.iloc[0].open,
             'volume_btc' : np.sum(data.volume_btc),
             'volume_currency' : np.sum(data.volume_currency)}
    agged['weighted_price'] = np.mean([agged['high'], agged['low'], agged['close'], agged['open']])
    return pd.DataFrame(agged, index=[0], columns=['timestamp', 'high', 'low', 'close', 'open', 'volume_btc', 'volume_currency'])