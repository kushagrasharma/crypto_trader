import pandas as pd
import numpy as np
import time

# Abstract class to define what a feature extractor should look like
class FeatureExtractor():
	def getFeatures(state, action):
		raise NotImplementedError


# A trivial first attempt at feature selection
class Try0(FeatureExtractor):
	def getFeatures(self, state, action):
		"""
			state is a dictionary of the current portfolio and market information.
			Available fields include:
		    	- market (a market object as defined in market.py)
		    	- funds
		    	- bitcoin
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


# first try at selecting a feature set.  Here we use all of the features we computed 
# during the preprocessing phase.
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
			15: market["weighted_price"] - past15["weighted_price"],
			16: market["weighted_price"] - pastDay["weighted_price"],
		}
		return np.array([d[i] for i in d])



# A second try at selecting a feature set.  Here we use a subset of the features used in Try1
class Try2(FeatureExtractor):
	def getFeatures(self, state, action):
		market = state["market"].getCurrentMarketInfo()
		pastHour = state["market"].getPastMarketInfo(4)
		pastDay = state["market"].getPastMarketInfo(4*24)
		d = {
			"1" : market.rsi4Hours,
			"2" : market.willr4Hours,
			"3" : market.dema4Hours,
			# We found that these two metrics dominanted the Q-function in terms of weights and values,
			# so we removed them to hopefully get more accurate approximations
			# "4" : market.chaikinOscillator,
			# "5" : market.chaikinLine,
			"6" : market.trueRange4Hours,
			"7" : market.linearRegSlope4Hours,
			"8" : {"buy" : 3, "hold" : 2, "sell" : 1}[action],
			"9": market["weighted_price"] - pastHour["weighted_price"],
			"10": market["weighted_price"] - pastDay["weighted_price"],
			"11" : market["std"],
			"12" : market.tsf,
		}
		return np.array([d[str(i)] for i in d])



# Same feature extractor as Try1, but modified to work nicer with the 
# K Nearest Neighbors Algorithm
class KNearestNeighborsExtractor(FeatureExtractor):
	def getFeatures(self, row):
		d = {
			1: row["willr4Hours"],
			2: row["willr4Days"],
			3: row["willrWeek"],
			3: row["tema4Hours"],
			4: row["tema4Days"],
			5: row["temaWeek"],
			6: row["rsi4Hours"],
			7: row["rsi4Days"],
			8: row["rsiWeek"],
			9: row["trueRange4Hours"],
			10: row["trueRange4Days"],
			11: row["trueRangeWeek"],
			12: row["linearRegSlope4Hours"],
			13: row["linearRegSlope4Days"],
			14: row["linearRegSlopeWeek"],
			15: row["tsf4Hours"],
			16: row["tsf4Days"],
			17: row["tsfWeek"],
			18: row["std4Hours"],
			19: row["weighted_price"],
		}
		return np.array([d[i] for i in d])