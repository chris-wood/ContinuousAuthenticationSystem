'''
File: Classifier.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math
import threading
import time
import KeyloggerFeatureExtractor

DB = "profiles.csv" # Future versions would make this an encrypted SQLite DB for efficiency

# Constant sleep time before checking results
SLEEP_TIME = 120

# Data collection mode (used for offline Weka analysis)
OFFLINE_ANALYSIS = True
OFFLINE_FILE = "classifier"
OFFLINE_FILE_EXT = ".csv"

class Classifier(threading.Thread):
	'''
	The main classifier class that contains many different classification algorithms
	for testing and evaluation purposes.
	'''

	def __init__(self, manager):
		''' 
		Default constructor... This guy does nothing for now.
		''' 
		threading.Thread.__init__(self)
		self.manager = manager
		self.running = False

	def run(self):
		self.running = True
		offlineFileNum = 0
		while self.running:
			print("Classifier is starting to sleep")
			time.sleep(SLEEP_TIME)

			# Pull all of the information from the profile manager and use it for classification
			vectors = self.manager.getSessionVectors()
			aggregate = []
			#aggregate.append(vectors[0][0]) # we don't require the name to be at the front of this vector
			for i in range(1, len(vectors[0])):
				sum = 0
				for v in vectors:
					sum = sum + v[i]
				aggregate.append(sum / len(vectors))

			# Check to see if we perform the analysis or we save the log data offline
			if (OFFLINE_ANALYSIS):
				fileName = OFFLINE_FILE + "_" + str(offlineFileNum) + OFFLINE_FILE_EXT
				offlineFileNum = offlineFileNum + 1

				# Open the file and write it out
				fHandle = open(fileName, 'w')
				for i in range(0, len(aggregate) - 1):
					fHandle.write(aggregate[i] + ',')
				fHandle.write(aggregate[len(aggregate) - 1] + '\n')
			else:
				self.findMatch(aggregate)

	def standardize(self, vectors):
		'''
		Vectors is a dictionary that maps names to their profiles.

		Note: this method is incomplete.
		'''
		# Traverse each vector to generate the mean/stddev for each feature
		for i in range(0, len(vectors[vectors.keys()[0]])):
			total = 0
			totalSquared = 0
			count = 0
			for key in vectors:
				total = total + vectors[key][i]
				totalSquared = totalSquared + (vectors[key][i] ** 2)
				count = count + 1

			# Compute the mean and standard deviation
			mean = total / count
			stddev = math.sqrt((totalSquared / count) - (mean * mean))

			# Update the value for each vector so that they're normalized
			#meanList.append(mean)

	def normalize(self, vectors, testVector = None):
		'''
		Vectors is a dictionary that maps names to their profiles.
		'''
		for i in range(0, len(vectors[vectors.keys()[0]])):
			minVal = sys.maxint
			maxVal = 0
			nonZero = False
			for key in vectors:
				if (vectors[key][i] < minVal):
					minVal = vectors[key][i]
					nonZero = True
				if (vectors[key][i] > maxVal):
					maxVal = vectors[key][i]
					nonZero = True

				#print("feature " + str(i) + ", " + str(maxVal) + ", " + str(minVal))
				#print(maxVal, minVal)

			# Include the test vector in this calculation
			if (testVector != None):
				if (testVector[i] < minVal):
					minVal = testVector[i]
				if (testVector[i] > maxVal):
					maxVal = testVector[i]

			# Now update the values
			for key in vectors:
				if nonZero and ((maxVal - minVal) > 0):
					#print("old: " + str(vectors[key][i]))
					vectors[key][i] = (vectors[key][i] - minVal) / (maxVal - minVal)
					#print("new: " + str(vectors[key][i]))
			if (testVector != None):
				if nonZero and ((maxVal - minVal) > 0):
					testVector[i] = (testVector[i] - minVal) / (maxVal - minVal)
		return vectors

	def findMatch(self, testing_contents):
		'''
		Process the testing contents to determine the closest profile to which this matches
		in the profile database. 
		'''
		# Open the database file and read all of the user profiles contained, running each one against the 
		# classifier to see what the best match is...
		databaseFile = open(DB, 'r')
		databaseLines = databaseFile.readlines()

		# Normalize the database
		vectors = {}
		for line in databaseLines:
			lineList = line.split(',')
			vectors[lineList[0]] = []
			for i in range(1, len(lineList)):
				try:
					vectors[lineList[0]].append(float(lineList[i]))
				except:
					pass
		vectors = self.normalize(vectors, testVector = testing_contents)
		#print(vectors)

		# Traverse the profiles and find the best match
		matchId, finalDistance = '', sys.maxint
		for key in vectors:
			indices = self.prune(testing_contents)
			#print testing_contents
			#print indices
			distance = self.euclidean_distance(vectors[key], testing_contents, indices)
			print(key, distance)
			if (distance <= finalDistance):
				finalDistance = distance
				matchId = key

		print("Match: " + matchId)

	def prune(self, testing_contents):
		'''
		Prune out non-relevant features (ones that are 0, etc) from the test set
		to make our classification results better.

		It is assumed that each profile stores the same features, so we don't need to do
		any commonality pruning. Of course,if this wasn't the case, then we could write an auxiliary
		pruning method to take care of this.
		'''
		indices = []
		for i in range(0, len(testing_contents)):
			try:
				if (float(testing_contents[i]) > 0):
					indices.append(i)
			except:
				pass
		return indices

	def euclidean_distance(self, modelProfile, testProfile, indices):
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

# For testing purposes - make sure this classifier works as expected first (test with Nate's old one)
def main():
	args = sys.argv
	testing_file = open(args[1])

	testing_contents = testing_file.read().split('\n')
	contents = testing_contents[1].split(',') # caw: changed from index 0 to 1 because 0 now contains feature labels
	rawData = []
	for i in range(0, len(contents)):
		try:
			rawData.append(float(contents[i]))
		except:
			pass

	classifier = Classifier(None)
	classifier.findMatch(rawData)

if __name__ == '__main__':
	main()

