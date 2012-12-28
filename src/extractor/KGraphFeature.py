'''
File: KGraphFeature.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math

class KGraphFeature(object):
	def __init__(self):
		self.times = []
		self.min_time = sys.maxint
		self.max_time = 0

	def addTime(self, time):
		self.times.append(time)
		if (time > self.max_time):
			self.max_time = time
		if (time < self.min_time):
			self.min_time = time

	def getMin(self):
		return self.min_time

	def getMax(self):
		return self.max_time

	def getAverage(self):
		total = 0
		for x in self.times:
			total = total + x
		if (len(self.times) == 0):
			return 0
		else:
			return float(total) / len(self.times) # no 0-check for division

	def getStandardDeviation(self):
		numerator = 0
		avg = self.getAverage()
		for x in self.times:
			numerator = numerator + (float(x - avg) ** 2)
		if (len(self.times) == 0):
			return 0
		else:
			return math.sqrt((numerator / len(self.times)) * 100 / 100) 
