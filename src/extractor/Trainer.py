'''
File: Trainer.py
Author: Christopher Wood, caw4567@rit.edu
'''

import sys
import math
import Queue
import re
import sqlite3 # for user profile storage and dynamic updating (more advanced versions should use the database for storage)
import KeyloggerFeatureExtractor # for extraction...

# The constant database file name used to store new user profiles
DB = "profiles.csv"
WEKAOUT = "profiles.arff"

# Toggle Weka output
wekaOutput = True

def processLog(logFile):
	'''
	Run the feature extraction code on the provided log file
	'''
	# Regex to filter each log line (if there's clutter)
	line_re = re.compile(r"^(\d+)\s+(\d+)\s+KEY_(DOWN|UP)\s*$")

	bucket = []
	for line in logFile:
		match = line_re.match(line)
		if not (match is None):
			bucket.append(line)

	extractor = KeyloggerFeatureExtractor.KeyloggerFeatureExtractor(None, None, None)
	vector = extractor.extract(bucket)
	return vector

# For testing purposes - make sure this classifier works as expected first (test with Nate's old one)
def main():
	'''
	Go through the log files, run them through the extractor, and then store them in the database.
	'''

	if len(sys.argv) == 2 and sys.argv[1].lower() in ('-h', '--help'):
		print "python {0} [log1 log2 ... logN]".format(sys.argv[0])
		exit(1)

	# Traverse the set of provided log files and process each one...
	# process any logs
	vectors = {}
	for arg in sys.argv[1:]:
		try:
			print "Processing:", arg
			with open(arg, 'rb') as f:
				vectors[arg] = processLog(f)
				#feature_extract(file) - use the windows keylogger for this purpose...
				# store vector in stats
		except IOError as e:
			print >> sys.stderr, e

	# Normalize the data in the vectors
	extractor = KeyloggerFeatureExtractor.KeyloggerFeatureExtractor(None, None, None)
	#vectors = extractor.normalize(vectors)

	# Append the features (if we're generating a Weka CSV file)
	if (wekaOutput):
		# Append the @dataset relation.
		databaseFile = open(WEKAOUT, 'w')
		databaseFile.write('@relation profiles\n\n')

		# Append the @attribute relation.
		features = extractor.featureHeaders()

		# Append the identifier attribute as a nominal selector
		databaseFile.write('@attribute identifier {')
		for i in range(0, len(vectors) - 1):
			databaseFile.write(str(vectors.keys()[i]) + ',')
		databaseFile.write(str(vectors.keys()[len(vectors) - 1]) + '}\n')

		for i in range(1, len(features)):
			databaseFile.write('@attribute ' + str(features[i]) + ' numeric\n')
		databaseFile.write('\n')
		#for f in features:
		#	databaseFile.write('@attribute ' + str(f) + ' numeric\n')
		#databaseFile.write('\n')
		print("features: " + str(len(features)))

		# Append the @dataset entries now
		databaseFile.write('@data\n')
		for key in vectors:
			print("profiles: " + str(len(vectors[key])))
			databaseFile.write(str(key) + ",")
			for i in range(0, len(vectors[key]) - 1):
				databaseFile.write(str(vectors[key][i]) + ',')
			databaseFile.write(str(vectors[key][len(vectors[key] ) - 1]) + '\n')
			#for feature in vectors[key]:
			#	databaseFile.write(str(feature) + ",")
			#databaseFile.write('\n')

	else:
		databaseFile = open(DB, 'w')
		for key in vectors:
			print("profiles: " + str(len(vectors[key])))
			databaseFile.write(str(key) + ",")
			for feature in vectors[key]:
				databaseFile.write(str(feature) + ",")
			databaseFile.write('\n')

# Let it rip...
if __name__ == '__main__':
	main()

