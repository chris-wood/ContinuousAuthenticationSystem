'''
File: Distance.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math
import threading
import time

UPPER_BOUND = 1000

def prune(contents1, contents2):
	'''
	Prune out non-relevant features (ones that are 0, etc) from the test set
	to make our classification results better.

	It is assumed that each profile stores the same features, so we don't need to do
	any commonality pruning. Of course,if this wasn't the case, then we could write an auxiliary
	pruning method to take care of this.
	'''
	indices = []
	for i in range(0, len(contents1)):
		try:
			if (float(contents1[i]) > 0) and (float(contents2[i]) > 0) and (float(contents1[i]) < UPPER_BOUND) and (float(contents2[i]) < UPPER_BOUND):
				indices.append(i)
		except:
			pass
	return indices

def euclidean_distance(modelProfile, testProfile, indices):
	'''
	Calculate the straightforward Euclidean distance between a single
	model profile and the test profile in question.
	'''
	distance = 0
	for i in indices:
		try:
			modelVal = float(modelProfile[i])
			testVal = float(testProfile[i])
			distance = distance + math.pow(modelVal - testVal, 2)
		except:
			print("Non-numeric feature found.: " + str(modelProfile[i]) + ", " + str(testProfile[i]))
			pass

	# Return the total distance...
	return math.sqrt(distance)

def city_distance(modelProfile, testProfile):
	distance = 0
	for i in range(0, len(modelProfile)):
		try:
			difference = abs(modelProfile[i] - testProfile[i])
			distance = distance + difference
		except:
			pass
	return distance

def minkowski_distance(modelProfile, testProfile, p):
	distance = 0
	for i in range(0, len(modelProfile)):
		try:
			difference = (abs(modelProfile[i] - testProfile[i])) ** p
			distance = distance + difference
		except:
			pass

	if (p == 1):
		return distance
	elif (p == 2):
		return math.sqrt(distance)
	else:
		return -1 # not supported

def chebychev_distance(modelProfile, testProfile):
	maxDistance = 0
	for i in range(0, len(modelProfile)):
		try:
			difference = (abs(modelProfile[i] - testProfile[i]))
			if (difference > maxDistance):
				maxDistance = difference
		except:
			pass
	return maxDistance

def cosine_difference(modelProfile, testProfile):
	distance = 0
	dotProduct = 0
	xLength = 0
	yLength = 0

	# Compute the dot product and vector length in euclidean space
	for i in range(0, len(modelProfile)):
		try:
			product = modelProfile[i] * testProfile[i]
			if (product < 3e+27): # some unpruned vector elements cause this to not calculate correctly, so we omit them from the calculation
				dotProduct = dotProduct + product
				xLength = xLength + (modelProfile[i] * modelProfile[i])
				yLength = yLength + (testProfile[i] * testProfile[i])
		except:
			pass

	return 1.0 - (float(dotProduct) / (math.sqrt(xLength) * math.sqrt(yLength)))

def correlation_distance(modelProfile, testProfile):
	xTotal = 0
	yTotal = 0
	for i in range(0, len(modelProfile)):
		try:
			xTotal = xTotal + modelProfile[i]
			yTotal = yTotal + testProfile[i]
		except:
			pass

	dotProduct = 0
	xLength = 0
	yLength = 0
	xMean = float(xTotal) / len(modelProfile)
	yMean = float(yTotal) / len(modelProfile)

	# Compute the dot product and vector length in euclidean space
	for i in range(0, len(modelProfile)):
		try:
			product = abs(modelProfile[i] - xMean) * abs(testProfile[i] - yMean)
			dotProduct = dotProduct + product
			xLength = xLength + (abs(modelProfile[i] - xMean) * abs(modelProfile[i] - xMean))
			yLength = yLength + (abs(testProfile[i] - yMean) * abs(testProfile[i] - yMean))
		except:
			pass

	return 1.0 - (float(dotProduct) / (math.sqrt(xLength) * math.sqrt(yLength)))


def main():
	args = sys.argv
	file1 = open(args[1])
	file2 = open(args[2])

	file1_contents = file1.read().split('\n')
	f1contents = file1_contents[1].split(',') # index 0 contains feature headers

	file2_contents = file2.read().split('\n')
	f2contents = file2_contents[1].split(',') # index 0 contains feature headers

	data1 = []
	data2 = []
	for i in range(0, len(f1contents)):
		try:
			f1contents[i] = float(f1contents[i])
			data1.append(f1contents[i])
		except:
			pass
	for i in range(0, len(f2contents)):
		try:
			f2contents[i] = float(f2contents[i])
			data2.append(f2contents[i])
		except:
			pass

	indices = prune(data1, data2)
	print("Euclidean: " + str(euclidean_distance(data1, data2, indices)))
	print("City: " + str(city_distance(data1, data2)))
	print("Chebychev: " + str(chebychev_distance(data1, data2)))
	print("Cosine: " + str(cosine_difference(data1, data2)))
	print("Correlation: " + str(correlation_distance(data1, data2)))

if (__name__ == '__main__'):
	main()