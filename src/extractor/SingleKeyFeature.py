'''
File: SingleKeyFeature.py
Author: Name Smith 
Contributor: Christopher Wood, caw4567@rit.edu
'''

import sys
import math

MEDIAN_CUSHION = 5

class SingleKeyFeature(object):
	# Selected features for a single key
	def __init__(self):
		self.total_time = 0
		self.total_fly = 0
		self.total_clicks = 0
		self.times = []
		self.flies = []
		self.min_time = sys.maxint
		self.max_time = 0
		self.min_fly = sys.maxint
		self.max_fly = 0

	def getAverageFly(self):
		if (self.total_clicks < MEDIAN_CUSHION):
			return float(self.total_fly) / self.total_clicks
		else:
			newTimes = []
			for i in self.flies:
				newTimes.append(i)
			newTimes.sort()

			if (self.total_clicks % 2 == 0):
				middle = self.total_clicks // 2
				return float(newTimes[middle]) / float(newTimes[middle + 1])
			else:
				middle = self.total_clicks // 2
				return float(newTimes[middle])

	def getAverageDown(self):
		if (self.total_clicks < MEDIAN_CUSHION):
			return float(self.total_time) / self.total_clicks
		else:
			newTimes = []
			for i in self.times:
				newTimes.append(i)
			newTimes.sort()

			if (self.total_clicks % 2 == 0):
				middle = self.total_clicks // 2
				return float(newTimes[middle]) / float(newTimes[middle + 1])
			else:
				middle = self.total_clicks // 2
				return float(newTimes[middle])

	def getDownStandardDeviation(self):
		num = 0.0
		for x in self.times:
			num = num + ((x - self.getAverageDown()) ** 2)
		return math.sqrt(float(num) / float(len(self.times)))

	def getFlyStandardDeviation(self):
		num = 0.0
		for x in self.flies:
			num = num + (float(x - self.getAverageFly()) ** 2)
		return math.sqrt(num / len(self.flies))
