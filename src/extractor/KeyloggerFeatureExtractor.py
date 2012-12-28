'''
File: KeyloggerFeatureExtractor.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math
import SingleKeyFeature
import KGraphFeature
import Queue
import threading
import sqlite3
from time import clock, time # for time-based extraction

class KeyloggerFeatureExtractor(threading.Thread):
	'''
	This class is responsible for extracting features from the consumer queue
	on a window or time basis, and then perform feature extraction on the data 
	that was collected.
	'''

	# The epoch window for collecting keystrokes from the consumer's buffer
	BUFFER_SIZE = 300 # test value... this will have to be larger in practice

	# Key map constants (127 characters on the keyboard are monitored)
	KEY_CODE_LOW = 1
	KEY_CODE_HIGH = 127

	def __init__(self, serv, queue, session):
		'''
		The constructor for the feature extractor.
		'''
		threading.Thread.__init__(self)
		self.server = serv
		self.running = True
		self.queue = queue
		self.session = session

		self.keyQueue = {}
		self.features = {}
		self.last = 0

		# Fixed sets of digraphs and trigraphs we're interested in measuring
		self.fixedDigraphs = ["TH", "HE", "IN", "EN", "NT", "RE", "ER", "AN", "TI", "ES", "ON", "AT", "AM"]
		self.fixedTrigraphs = ["MPU", "COM", "PUT", "THE", "UTE", "OMP", "TER", "TIO", "ERS"]
		self.fixedKGraphs = {} # None are defined as of yet..

	def run(self):
		'''
		The feature extractor loop.
		'''
		print("Beginning extractor loop.")
		time = clock()
		while self.running:
			diff = clock() - time
			if not (self.queue.qsize() < self.BUFFER_SIZE):
				bucket = []
				while (not self.queue.empty()): # drain the queue!
					bucket.append(self.queue.get())
				vector = self.extract(bucket)
				vector.insert(0, "currentUser")
				self.session.submitProfileVector(vector)

				# Reset the timer for data aggregation
				time = clock()

	def featureHeaders(self):
		'''
		Construct the feature header (useful for generating Weka compliant CSV files)
		'''
		builder = []

		# First one is the name
		builder.append("FEATURESname") # use FEATURES string to help processing...

		# Next are the single key data
		for i in range(self.KEY_CODE_LOW, self.KEY_CODE_HIGH + 1):
			#builder.append(str(i) + "_down_min")
			#builder.append(str(i) + "_down_max")
			builder.append(str(i) + "_down_avg_singledown")
			builder.append(str(i) + "_down_std_singledown")
			#builder.append(str(i) + "_fly_min")
			#builder.append(str(i) + "_fly_max")
			builder.append(str(i) + "_fly_avg_singlefly")
			builder.append(str(i) + "_fly_std_singlefly")

		# The two new features
		builder.append("speed")
		builder.append("deletions")

		# Now add the digraph features
		for i in range(0, len(self.fixedDigraphs)):
			#builder.append(self.fixedDigraphs[i] + "_min")
			#builder.append(self.fixedDigraphs[i] + "_max")
			builder.append(self.fixedDigraphs[i] + "_avg_digraph")
			builder.append(self.fixedDigraphs[i] + "_std_digraph")

		return builder

	def extract(self, log):
		'''
		The feaxture extraction method, that returns a single user profile vector.
		'''
		contentBuilder = self.generateSingleDurationVector(log)
		digraphContent = self.generateDigraphVector(log)
		for element in digraphContent:
			contentBuilder.append(element)
		return contentBuilder

	def generateSingleDurationVector(self, log):
		'''
		This method generates a single profile timestamp based on the information
		in the log list. It is assumed that the log parameter is a list of keystroke
		data tuples: time key up/down
		'''

		# Custom feature helper variables
		totalTime = 0
		deletions = 0

		builder = []
		self.last = 0
		for data in log:
			split = data.strip('\r\n').split(' ')

			# Ensure the split is of the appropriate length
			if (len(split) == 3):
				time = int(split[0])
				totalTime = totalTime + time
				key = int(split[1])

				# Check for deletions
				if (key == 14):
					deletions = deletions + 1

				# Handle the key release
				if (key in self.keyQueue):
					total = time - self.keyQueue[key]

					# See if we need to add a new feature to the dictionary
					if not (key in self.features):
						self.features[key] = SingleKeyFeature.SingleKeyFeature()

					# Increment the clicks and add totals
					self.features[key].total_time = self.features[key].total_time + total
					if (self.last != 0):
						self.features[key].total_fly = self.features[key].total_fly + (time - self.last)
					else:
						self.features[key].total_fly = self.features[key].total_fly + 0
					self.features[key].total_clicks = self.features[key].total_clicks + 1

					# Add the times to the storage variables
					self.features[key].times.append(total)
					self.features[key].flies.append(time - self.last)

					# Check the fly min and max
					if ((time - self.last) < self.features[key].min_fly):
						self.features[key].min_fly = time - self.last
					if ((time - self.last) > self.features[key].max_fly):
						self.features[key].max_fly = time - self.last

					# Check down min/max
					if (total < self.features[key].min_time):
						self.features[key].min_time = total
					if (total > self.features[key].max_time):
						self.features[key].max_time = total

					# Remove the key from the self.keyQueue
					del self.keyQueue[key]

				# Else we add the key to the self.keyQueue
				else: # the key was pressed
					self.keyQueue[key] = time

				# Store the key press time
				self.last = time

		# Iterate over all common key characters
		for i in range(self.KEY_CODE_LOW, self.KEY_CODE_HIGH + 1):
			if (i in self.features):
				#builder.append(self.features[i].min_time)
				#builder.append(self.features[i].max_time)
				builder.append(self.features[i].getAverageDown())
				builder.append(self.features[i].getDownStandardDeviation())
				#builder.append(self.features[i].min_fly)
				#builder.append(self.features[i].max_fly)
				builder.append(self.features[i].getAverageFly())
				builder.append(self.features[i].getFlyStandardDeviation())
			else:
				for j in range(0,4): # we append 8 zeros - this number must match the number of features in the above loop
					builder.append(0)

		# Append the average typing speed as a feature
		builder.append((totalTime / len(log)))

		# Append the number of deletions (indicating # of errors)
		builder.append(deletions)

		# Return the resulting string...
		return builder

	def generateSingleTransitionVector(self, log):
		'''
		This method generates a single profile for transitions between
		all keys that are being monitored.
		'''

		transitionMap = {}
		countMap = {}
		keyMap = {}
		builder = []
		for data in log:
			split = data.strip('\r\n').split(' ')

			# Ensure the split is of the appropriate length
			if (len(split) == 3):
				time = int(split[0])
				totalTime = totalTime + time
				key = int(split[1])

				try:
					if ('KEY_UP' in status):
						keyMap[key] = time
					elif (('KEY_DOWN' in status) and (key in keyMap)):
						if not (key in transitionMap):
							transition[key] = 0
							countMap[key] = 0

						# Store the data now
						transition[key] = transition[key] + (time - keyMap[key])
						countMap[key] = countMap[key] + 1
						del keyMap[key] # remove the key from the map
				except:
					pass

		# Format the output
		for i in range(self.KEY_CODE_LOW, self.KEY_CODE_HIGH + 1):
			if (i in transitionMap):
				builder.append(transitionMap[key] / countMap[key])
			else:
				builder.append(0)

	def generateDigraphVector(self, log):
		'''
		This method generates a single profile timestamp for digraphs based on the information
		in the log list. It is assumed that the log parameter is a list of keystroke
		data tuples: time key up/down.
		'''
		builder = []
		digraphs = {}
		downTimes = {}
		numberToChar = {}
		digraphString = ""
		skipTime = False # for handling sentence boundaries

		digraphChar = [] # List of length at most 2 (since it's a digraph)
		digraphChar.append(0)
		digraphChar.append(0)

		# Initialize the numberToChar map
		for i in range(65,91):
			numberToChar[i] = i

		for data in log:
			split = data.strip('\r\n').split(' ')

			# Ensure the split is of the appropriate length
			if (len(split) == 3):
				time = int(split[0])
				key = int(split[1])
				status = str(split[2])

				try:
					if (('KEY_DOWN' in status) and (key in numberToChar)): # check to see if this is one of the digraphs we are interested in
						#print("down")

						if (key == 52):
							skipTime = True
							digraphString = ""
						else:
							digraphChar[1] = chr(key)
							digraphString = str(digraphChar[0]) + str(digraphChar[1])
							digraphChar[0] = digraphChar[1]

							# Add it to the down time map
							downTimes[digraphChar[1]] = time
					elif (('KEY_UP' in status) and (digraphString in self.fixedDigraphs)):	
						if not (digraphString in digraphs):
							digraphs[digraphString] = KGraphFeature.KGraphFeature()
						digraphs[digraphString].addTime(time - downTimes[digraphString[0]])
				except:
					pass

		for i in range(0, len(self.fixedDigraphs)):
			found = False
			for di in digraphs:
				if (self.fixedDigraphs[i] == di):
					found = True
					#builder.append(digraphs[self.fixedDigraphs[i]].getMin())
					#builder.append(digraphs[self.fixedDigraphs[i]].getMax())
					builder.append(digraphs[self.fixedDigraphs[i]].getAverage())
					builder.append(digraphs[self.fixedDigraphs[i]].getStandardDeviation())
			if found == False:
				for j in range(0,2): # we append 4 zeros - this is not a valid digraph
					builder.append(0)


		# Return the vector
		return builder

	def generateTrigraphVector(self, log):
		'''
		This method generates a single profile timestamp for trigraphs based on the information
		in the log list. It is assumed that the log parameter is a list of keystroke
		data tuples: time key up/down.
		'''
		builder = []
		trigraphs = {}
		downTimes = {}
		numberToChar = {}
		trigraphString = ""

		trigraphChar = [] # List of length at most 3 
		trigraphTimes = []

		# Initialize the numberToChar map (for the characters that we care about)
		for i in range(65,91):
			numberToChar[i] = i

		for data in log:
			split = data.strip('\r\n').split(' ')

			# Ensure the split is of the appropriate length
			if (len(split) == 3):
				time = int(split[0])
				key = int(split[1])
				status = str(split[2])

				try:
					if (('KEY_DOWN' in status) and (key in numberToChar)): # check to see if this is one of the digraphs we are interested in
						if (len(trigraphChar) < 3):
							trigraphChar.append(key)
							trigraphTimes.append(time)
						else:
							# Store the data here
							trigraphChar[0] = trigraphChar[1]
							trigraphChar[1] = trigraphChar[2]
							trigraphChar[2] = key
							trigraphTimes[0] = trigraphTimes[1]
							trigraphTimes[1] = trigraphTimes[2]
							trigraphTimes[2] = time

							# Reconstruct the string for comparison
							trigraphString = str(trigraphChar[0]) + str(trigraphChar[1]) + str(trigraphChar[2])

					elif (('KEY_UP' in status) and (trigraphString in self.fixedTrigraphs)):
						if not (trigraphString in trigraphs):
							trigraphs[trigraphString] = KGraphFeature.KGraphFeature()
						trigraphs[trigraphString].addTime(time - trigraphTimes[2])
				except:
					pass

		for i in range(0, len(self.fixedTrigraphs)):
			found = False
			for ti in trigraphs:
				if (self.fixedTrigraphs[i] == ti):
					found = True
					#builder.append(trigraphs[self.fixedTrigraphs[i]].getMin())
					#builder.append(trigraphs[self.fixedTrigraphs[i]].getMax())
					builder.append(trigraphs[self.fixedTrigraphs[i]].getAverage())
					builder.append(trigraphs[self.fixedTrigraphs[i]].getStandardDeviation())
			if found == False:
				for j in range(0,2): # we append 4 zeros - this is not a valid digraph
					builder.append(0)


		# Return the vector
		return builder

	def generateKGraphVector(self, k, log):
		'''
		This method generates a single profile timestamp for k-graphs based on the information
		in the log list. It is assumed that the log parameter is a list of keystroke
		data tuples: time key up/down.
		'''
		builder = []
		kgraphs = {}
		downTimes = {}
		numberToChar = {}
		kgraphString = ""

		kgraphChar = [] # List of length at most 3 
		kgraphTimes = []

		# Initialize the numberToChar map (for the characters that we care about)
		for i in range(65,91):
			numberToChar[i] = i

		for data in log:
			split = data.strip('\r\n').split(' ')

			# Ensure the split is of the appropriate length
			if (len(split) == 3):
				time = int(split[0])
				key = int(split[1])
				status = str(split[2])

				try:
					if (('KEY_DOWN' in status) and (key in numberToChar)): # check to see if this is one of the digraphs we are interested in
						if (len(kgraphChar) < k):
							kgraphChar.append(key)
							kgraphTimes.append(time)
						else:
							for i in range(0, k - 1):
								kgraphChar[i] = kgraphChar[i + 1]
								kgraphTimes[i] = kgraphTimes[i + 1]
							kgraphChar[k - 1] = key
							kgraphTimes[k - 1] = time

							# Reconstruct the string for comparison
							kgraphString = ""
							for i in range(0, k):
								kgraphString = kgraphString + str(kgraphChar[i])

					elif (('KEY_UP' in status) and (kgraphString in self.fixedKGraphs[k])):
						if not (kgraphString in kgraphs):
							kgraphs[kgraphString] = KGraphFeature.KGraphFeature()
						kgraphs[kgraphString].addTime(time - kgraphTimes[2])
				except:
					pass

		for i in range(0, len(self.fixedKGraphs[k])):
			found = False
			for ki in kgraphs:
				if (self.fixedKGraphs[k][i] == ki):
					found = True
					#builder.append(kgraphs[self.fixedKGraphs[k][i]].getMin())
					#builder.append(kgraphs[self.fixedKGraphs[k][i]].getMax())
					builder.append(kgraphs[self.fixedKGraphs[k][i]].getAverage())
					builder.append(kgraphs[self.fixedKGraphs[k][i]].getStandardDeviation())
			if found == False:
				for j in range(0,2): # we append 4 zeros - this is not a valid digraph
					builder.append(0)


		# Return the vector
		return builder

# The main method for testing this module
def main():
	'''
	The main method that can be used to unit test this module.
	'''
	extractor = KeyloggerFeatureExtractor(None, None, None)
	stats = {}
	'''
	#for arg in sys.argv[1:]:
	if ("-out" in sys.argv[1]):
		outFile = sys.argv[2]
		outFileHandler = open(outFile, 'w')
		bucket = []
		for arg in sys.argv[3:]:
			try:
				print "Processing:", arg
				with open(arg, 'rb') as f:
					lines = f.readlines()
					bucket.append(extractor.extract(lines))
		# Write the headers
		headers = extractor.featureHeaders()
		for i in range(0, len(headers) - 1):
			outFileHandler.write(headers[i] + ',')
		outFileHandler.write('\n')

		# Write the data
		for data in bucket:
			outFileHandler.write(arg + ',')
			for i in range(0, len(data) - 1):
				outFileHandler.write(str(data[i]) + ',')
			outFileHandler.write(str(data[len(data) - 1]) + '\n')
			#print(extractor.extract(lines))
	else:
	'''
	try:
		tempFile = open(sys.argv[2], 'w')
		arg = sys.argv[1]
		print "Processing:", arg
		with open(arg, 'rb') as f:
			lines = f.readlines()
			data = extractor.extract(lines)

			# Write the headers!
			headers = extractor.featureHeaders()
			for i in range(0, len(headers) - 1):
				tempFile.write(headers[i] + ',')
			tempFile.write('\n')

			# Write the data!
			tempFile.write(arg + ',')
			for i in range(0, len(data) - 1):
				tempFile.write(str(data[i]) + ',')
			tempFile.write(str(data[len(data) - 1]) + '\n')
			#print(extractor.extract(lines))
	except Exception as e:
		print(e)

if (__name__=='__main__'):
	main()
