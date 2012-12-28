'''
File: Prune.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math
import threading
import time
import os

WEKA_OUTPUT = False
WEKA_FILE = "pruned_profiles.arff"

def boundsPrune(contents):
	'''
	Prune out non-relevant features (ones that are 0, etc) from the test set
	to make our classification results better.

	It is assumed that each profile stores the same features, so we don't need to do
	any commonality pruning. Of course,if this wasn't the case, then we could write an auxiliary
	pruning method to take care of this.
	'''
	UPPER_BOUND = 1000 # for bound pruning

	indices = []
	for i in range(1, len(contents[0])):
		try:
			relativeFeature = True
			for x in contents:
				# Check to see if this value is within the bounds that are necessary
				if (float(x[i]) == 0) or (float(x[i]) >= UPPER_BOUND):
					#print("Pruning: " + str(x[i]))
					relativeFeature = False
			if (relativeFeature == True):
				indices.append(i)
		except:
			pass
	return indices

def statisticalPrune(headers, contents):
	'''
	Prune outliers based on standard deviation for all of the provided
	'''
	# The maps that store the counts/total values so we can calculate the stddev after the second pass
	totalMap = {"singledown" : 0, "digraph" : 0, "singlefly" : 0}
	countMap = {"singledown" : 0, "digraph" : 0, "singlefly" : 0}

	for vector in contents:

		totalMap["singledown"] = 0
		totalMap["singlefly"] = 0
		totalMap["digraph"] = 0
		#totalMap["speed"] = 0
		#totalMap["deletions"] = 0
		countMap["singledown"] = 0
		countMap["singlefly"] = 0
		countMap["digraph"] = 0
		#countMap["speed"] = 0
		#countMap["deletions"] = 0

		for i in range(1, len(vector)):
			if ("singledown" in headers[i]):
				totalMap["singledown"] = totalMap["singledown"] + float(vector[i])
				countMap["singledown"] = countMap["singledown"] + 1
			elif ("singlefly" in headers[i]):
				totalMap["singlefly"] = totalMap["singlefly"] + float(vector[i])
				countMap["singlefly"] = countMap["singlefly"] + 1
			elif ("digraph" in headers[i]):
				totalMap["digraph"] = totalMap["digraph"] + float(vector[i])
				countMap["digraph"] = countMap["digraph"] + 1
			#elif ("speed" in headers[i]):
			#	totalMap["speed"] = totalMap["speed"] + float(vector[i])
			#	countMap["speed"] = countMap["speed"] + float(vector[i])
			#elif ("deletions" in in headers[i]):
			#	totalMap["deletions"] = totalMap["deletions"] + float(vector[i])
			#	countMap["deletions"] = countMap["deletions"] + float(vector[i])

		# Calculate the averages
		singledownMean = totalMap["singledown"] / countMap["singledown"]
		singleflyMean = totalMap["singlefly"] / countMap["singlefly"]
		digraphMean = totalMap["digraph"] / countMap["digraph"]

		# Calculate the variance
		singledownVariance = 0
		singleflyVariance = 0
		digraphVariance = 0
		for i in range(1, len(vector)):
			if ("singledown" in headers[i]):
				singledownVariance = singledownVariance + ((singledownMean - float(vector[i])) * (singledownMean - float(vector[i])))
			elif ("singlefly" in headers[i]):
				singleflyVariance = singleflyVariance + ((singleflyMean - float(vector[i])) * (singleflyMean - float(vector[i])))
			elif ("digraph" in headers[i]):
				digraphVariance = digraphVariance + ((digraphMean - float(vector[i])) * (digraphMean - float(vector[i])))
		singledownVariance = singledownVariance / countMap["singledown"]
		singleflyVariance = singleflyVariance / countMap["singlefly"]
		digraphVariance = digraphVariance / countMap["digraph"]

		# Finally, the stddev...
		singledownStddev = math.sqrt(singledownVariance)
		singleflyStddev = math.sqrt(singleflyVariance)
		digraphStddev = math.sqrt(digraphVariance)
		print singledownStddev
		print singleflyStddev
		print digraphStddev
		#print vector

		# Now, prune the dataset
		for i in range(1, len(vector)):
			if ("singledown" in headers[i]) and (float(vector[i]) > 0):
				upperBound = singledownMean + (3 * singledownStddev)
				lowerBound = singledownMean - (3 * singledownStddev)
				#print("value to check: " + vector[i])
				#print("upperBound = " + str(upperBound))
				#print("lowerBound = " + str(lowerBound))
				if not (float(vector[i]) > lowerBound and float(vector[i]) < upperBound):
				#if (float(vector[i]) < (4 * singledownStddev)) or (float(vector[i]) > (4 * singledownStddev)):
					vector[i] = "0"
			elif ("singlefly" in headers[i]) and (float(vector[i]) > 0):
				upperBound = singleflyMean + (3 * singleflyStddev)
				lowerBound = singleflyMean - (3 * singleflyStddev)
				if not (float(vector[i]) > lowerBound and float(vector[i]) < upperBound):
				#if (float(vector[i]) < (4 * singleflyStddev)) or (float(vector[i]) > (4 * singleflyStddev)):
					vector[i] = "0"
			elif ("digraph" in headers[i]) and (float(vector[i]) > 0):
				upperBound = digraphMean + (3 * digraphStddev)
				lowerBound = digraphMean - (3 * digraphStddev)
				if not (float(vector[i]) > lowerBound and float(vector[i]) < upperBound):
				#if (float(vector[i]) < (4 * digraphStddev)) or (float(vector[i]) > (4 * digraphStddev)):
					vector[i] = "0"

	return contents

def pairwiseSimilarityPrune(contents):
	'''
	Contents is assumed to be a map containing all of the profiles read in from memory.
	Prune all features that fall within the range of the mean+-stddev (leaving outliers).
	'''

	stdDevCushion = 0.1

	# Walk each feature and build up the feature column
	for i in range(1, len(contents[0])):
		column = []
		total = 0
		count = 0
		for profile in contents:
			#column.append(contents[key][i])
			total = total + float(profile[i])
			count = count + 1

		# Compute the average and then variance/stddev
		mean = (float(total) / count)
		variance = 0
		for key in contents:
			variance = variance + ((mean - float(profile[i])) * (mean - float(profile[i])))
		stddev = math.sqrt(variance)

		# Now, trim everything within the range [mean-stddev, mean+stddev]
		lowerBound = mean - (stdDevCushion * stddev)
		upperBound = mean + (stdDevCushion * stddev)
		for profile in contents:
			val = float(profile[i])
			if (val >= lowerBound) and (val <= upperBound):
				profile[i] = "0" # contents is a set of strings!

	return contents

def main():

	global WEKA_OUTPUT
	global WEKA_FILE

	indicesToKeep = None #[4,6,7,8,11,13,14,15,16,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,41,42,43,44,45,46,47,48,49,50,51,52,53,54,57,58,59,60,61,62,63,64,65]

	vectors = []

	files = []
	for arg in sys.argv[1:]:
		if not (os.path.isdir(arg)):
			files.append(arg)

	for arg in files:
		try:
			print "Processing:", arg
			with open(arg, 'r') as f:
				fContents = f.read().split('\n')
				contents = fContents[1].split(',')
				vectors.append(contents) 
				#vectors[arg] = processLog(f)
		except IOError as e:
			print >> sys.stderr, e

	# Pull out the headers from one of the files
	headers = []
	with open(files[0], 'r') as f: # just use the first file since it's easier
		fContents = f.read().split('\n')
		contents = fContents[0].split(',')
		for label in contents:
			headers.append(label)

	# Now do the pruning from standard deviation and whatnot
	#print vectors
	vectors = statisticalPrune(headers, vectors)

	# Now do the bounds pruning
	#print vectors
	indices = boundsPrune(vectors)
	indices.append(0)
	print("Indices to include: " + str(indices))

	# Prune based on statistical properties
	#print("Before pariwise: " + str(vectors))
	#vectors = pairwiseSimilarityPrune(vectors)
	#print("After pairwise: " + str(vectors))

	# Remove these elements from the vectors and headers
	#for i in indices:
	#	for v in vectors:
	#		v.pop(i)
	#	headers.pop(i) 
	if not (WEKA_OUTPUT):
		index = 0
		for arg in files:
			try:
				print "Processing:", arg
				with open(arg, 'w') as f:
					kIndex = 0
					line = ""
					for i in range(0, len(headers)):
					#for i in indices:
						if (i in indices):
							if (indicesToKeep == None or kIndex in indicesToKeep):
								#f.write(headers[i] + ',')
								line = line + headers[i] + ','
						else:
							#f.write(headers[i] + ',')
							line = line + headers[i] + ','
						kIndex = kIndex + 1
					line = line[0:len(line) - 1]
					f.write(line + '\n')
					kIndex = 0
					#for i in indices:
					line = ""
					for i in range(0, len(vectors[index])):
						if (i in indices):
							if (indicesToKeep == None or kIndex in indicesToKeep):
								#f.write(vectors[index][i] + ',')
								line = line + vectors[index][i] + ','
						else:
							#f.write('0,')
							line = line + '0,'
						kIndex = kIndex + 1
					line = line[0:len(line) - 1]
					f.write(line + '\n')
					index = index + 1
					#vectors[arg] = processLog(f)
			except IOError as e:
				print >> sys.stderr, e
	else: # Handle weka output (for comparison of the pruned/not pruned features)
		index = 0
		try:
			with open(WEKA_FILE, 'w') as f:

				f.write('@relation profiles\n\n')
				f.write('@attribute identifier {')
				for i in range(0, len(files) - 1):
					f.write(str(files[i]) + ',')
				f.write(str(files[len(files) - 1]) + '}\n')

				index = 0
				for i in range(0, len(headers)):
				#for i in indices:
					if (indicesToKeep == None or index in indicesToKeep):
						if (i in indices):
							if (len(headers[i]) > 0):
								f.write('@attribute ' + str(headers[i]) + ' numeric\n')
						else: #caw: new
							f.write('@attribute ' + str(headers[i]) + ' numeric\n')
					index = index + 1
				f.write('\n')

				f.write('@data\n')
				index = 0
				for key in files:
					f.write(str(key) + ",")
					line = ""
					kIndex = 0
					print(len(vectors[index]))
					for i in range(0, len(vectors[index])):
					#for i in indices:
						if (i in indices):
							if (indicesToKeep == None or kIndex in indicesToKeep):
								line = line + vectors[index][i] + ','
						else:
							line = line + '0,' #caw: new
						kIndex = kIndex + 1
					line = line[0:(len(line) - 1)] # trim the trailing comma
					f.write(line + '\n')
					index = index + 1
		except IOError as e:
			print >> sys.stderr, e
			

if (__name__ == '__main__'):
	main()