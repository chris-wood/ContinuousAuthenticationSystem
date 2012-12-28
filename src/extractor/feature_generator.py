# Run throgh a directory and parse each log file to a feature profile
# usage: python feature_generator.py dir

import sys
import os
import subprocess

# Walk the directory
directory = sys.argv[1]
for filename in os.listdir(directory):
	extension = os.path.splitext(filename)[1]
	print("Running: " + str("KeyloggerFeatureExtractor " + directory + os.sep + filename + " " + directory + os.sep + filename + ".csv"))
	subprocess.call(["python", "KeyloggerFeatureExtractor.py", directory + os.sep + filename, directory + os.sep + filename + ".csv"])
