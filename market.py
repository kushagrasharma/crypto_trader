import pandas as pd
import numpy as np
import math
import datetime
from copy import copy, deepcopy


class BitcoinMarket():
	def __init__(self, fileName="15min_fulldata.csv"):
		self.marketData = pd.read_csv(fileName, parse_dates=True) 
		# remove any entries that don't have all features defined (i.e. first 30)
		self.marketData.dropna()
		# add in an index column
		self.marketData.reset_index(level=0, inplace=True)
		# keep track of where we currently are in the data
		self.curTimestamp = 1
		self.numTimestamps = len(self.marketData)

	def getCurrentMarketInfo(self):
		""" 
			Returns a dictionary of the current market information.
			Available fields include the fields in the given csv
		"""
		return copy(self.marketData.loc[self.curTimestamp])

	def getPastMarketInfo(self, timeDelta):
		"""
			Returns the market info timeDelta timestamps before
		"""
		if self.curTimestamp - timeDelta >= 0:
			return deepcopy(self.marketData.loc[self.curTimestamp - timeDelta])
		else:
			# If we have an invalid index, return the first datapoint
			return deepcopy(self.marketData.loc[0])

	def getCurTimestamp(self):
		return self.curTimestamp

	def getNumTimestamps(self):
		return self.numTimestamps

	def setTimestamp(self, timestamp):
		self.curTimestamp = timestamp

	def setSampledTimestamp(self, lowerbound, upperbound):
		"""
			lower and upperbound are decimals (i.e. 0.8 to sample from the first 80% of timestamps)
		"""
		self.curTimestamp = np.random.randint(math.ceil(self.numTimestamps * lowerbound), math.floor(self.numTimestamps * upperbound))
		print self.curTimestamp
		return self.curTimestamp

	def incrementTime(self):
		""" 
			Increments the market to the next timestep. Returns boolean value
		    indicating if time could be incremented. 
		"""
		self.curTimestamp += 1
		return self.curTimestamp <= self.numTimestamps

