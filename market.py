import pandas as pd
import random
import math
import datetime
from copy import copy, deepcopy

def dateparse (time_in_secs):    
    return datetime.datetime.fromtimestamp(float(time_in_secs))


class BitcoinMarket():
	def __init__(self, fileName="coinbaseUSD_1-min_data_2014-12-01_to_2017-10-20.csv"):
		self.marketData = pd.read_csv(fileName, parse_dates=True,date_parser=dateparse, index_col='Timestamp') 
		self.marketData.reset_index(level=0, inplace=True)
		self.marketData.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume_btc', 'volume_currency', 'weighted_price']
		self.curTimestamp = 1
		self.numTimestamps = len(self.marketData)

	def getCurrentMarketInfo(self):
		""" 
		Returns a dictionary of the current market information.
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
		"""
		return copy(self.marketData.loc[self.curTimestamp])

	def getPastMarketInfo(self, timeDelta):
		return deepcopy(self.marketData.loc[self.curTimestamp - timeDelta])

	def getCurTimestamp(self):
		return self.curTimestamp

	def getNumTimestamps(self):
		return self.numTimestamps

	def setTimestamp(self, timestamp):
		self.curTimestamp = timestamp

	def setSampledTimestamp(self, upperbound):
		"""
			upperbound is a decimal (i.e. 0.8 to sample from the first 80% of timestamps)
		"""
		self.curTimestamp = random.randint(1, math.floor(self.numTimestamps * upperbound))
		return self.curTimestamp

	def incrementTime(self):
		""" 
			Increments the market to the next timestep. Returns boolean 
		    indicating if time could be incremented. 
		"""
		self.curTimestamp += 1
		return self.curTimestamp <= self.numTimestamps

