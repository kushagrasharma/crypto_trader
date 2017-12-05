import pandas as pd
import numpy as np
0
import time

class FeatureExtractor():
	def getFeatures(state, action):
		raise NotImplementedError


class Try0(FeatureExtractor):
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
		past15 = state["market"].getPastMarketInfo(1)
		pastDay = state["market"].getPastMarketInfo(96)
		d = {
			"volatility": market["high"] - market["low"],
			"volume_btc_delta_15_minutes": market["volume_btc"] - past15["volume_btc"],
			"volume_btc_delta_24_hours": market["volume_btc"] - pastDay["volume_btc"],
			"price_delta_15_minutes": market["weighted_price"] - past15["weighted_price"] * state["bitcoin"],
			"price_delta_24_hours": market["weighted_price"] - pastDay["weighted_price"] * state["bitcoin"],
			"willr" : market["willr4Hours"],
		}
		return np.array([d[str(i)] for i in d])

class Try1(FeatureExtractor):
	def getFeatures(self, state, action):
		market = state["market"].getCurrentMarketInfo()
		past15 = state["market"].getPastMarketInfo(1)
		pastDay = state["market"].getPastMarketInfo(96)
		d = {
			1: market["willr4Hours"],
			2: market["willr4Days"],
			3: market["willrWeek"],
			3: market["tema4Hours"],
			4: market["tema4Days"],
			5: market["temaWeek"],
			6: market["rsi4Hours"],
			7: market["rsi4Days"],
			8: market["rsiWeek"],
			9: market["trueRange4Hours"],
			10: market["trueRange4Days"],
			11: market["trueRangeWeek"],
			12: market["linearRegSlope4Hours"],
			13: market["linearRegSlope4Days"],
			14: market["linearRegSlopeWeek"],
			15: market["weighted_price"] - past15["weighted_price"] * state["bitcoin"],
			16: market["weighted_price"] - pastDay["weighted_price"] * state["bitcoin"],
		}
		return np.array([d[i] for i in d])

class Try2(FeatureExtractor):
	def getFeatures(self, state, action):
		market = state["market"].getCurrentMarketInfo()
		pastHour = state["market"].getPastMarketInfo(4)
		pastDay = state["market"].getPastMarketInfo(4*24)
		d = {
			"1" : market.rsi,
			"2" : market.willr,
			"3" : market.dema,
			#"4" : market.chaikinOscillator,
			#"5" : market.chaikinLine,
			"6" : market.trueRange,
			"7" : market.linearRegSlope,
			"8" : {"buy" : 3, "hold" : 2, "sell" : 1}[action],
			"9": market["weighted_price"] - pastHour["weighted_price"],
			"10": market["weighted_price"] - pastDay["weighted_price"],
			"11" : market["std"],
			"12" : market.tsf,
		}
		return np.array([d[str(i)] for i in d])

class Try3(FeatureExtractor):
	def getFeatures(self, state, action):
		market = state["market"].getCurrentMarketInfo()
		pastHour = state["market"].getPastMarketInfo(4)
		pastDay = state["market"].getPastMarketInfo(4*24)
		pastWeek = state["market"].getPastMarketInfo(4*24*7)






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