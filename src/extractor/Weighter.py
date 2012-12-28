'''
File: Weighter.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math
import threading
import time
import os

WEKA_OUTPUT = True
WEKA_FILE = "merged_weighted_profiles.arff"

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

def main():

	global WEKA_OUTPUT
	global WEKA_FILE

	# TODO: put the new code here

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
	print("Before pariwise: " + str(vectors))
	vectors = pairwiseSimilarityPrune(vectors)
	print("After pairwise: " + str(vectors))

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