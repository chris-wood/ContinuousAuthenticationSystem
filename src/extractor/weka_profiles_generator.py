# Run throgh a directory and parse each log file to a feature profile
# usage: python weka_profiles_generator.py dir

import sys
import os
import subprocess

# Walk the directory
directory = sys.argv[1]
headers = []
contents = []
files = []
for filename in os.listdir(directory):
	extension = os.path.splitext(filename)[1]
	if ("csv" in extension):
		print "Processing:", directory + os.sep + filename
		files.append(filename)
		with open(directory + os.sep + filename, 'r') as f:
			fContents = f.read().split('\n')
			headers = fContents[0].split(',')
			contents.append(fContents[1].split(','))

# Write out the WEKA file
WEKA_FILE = "merged_profiles.arff"
with open(WEKA_FILE, 'w') as f:
	f.write('@relation profiles\n\n')
	f.write('@attribute identifier {')
	for i in range(0, len(files) - 1):
		f.write(str(files[i]) + ',')
	f.write(str(files[len(files) - 1]) + '}\n')

	index = 0
	for i in range(0, len(headers)):
	#for i in indices:
		f.write('@attribute ' + str(headers[i]) + ' numeric\n')
	f.write('\n')

	f.write('@data\n')
	index = 0
	for profile in contents:
		f.write(str(profile[0]) + ",")
		line = ""
		for i in range(1, len(profile)):
		#for i in indices:
			line = line + profile[i] + ','
		line = line[0:(len(line) - 1)] # trim the trailing comma
		f.write(line + '\n')
		index = index + 1
