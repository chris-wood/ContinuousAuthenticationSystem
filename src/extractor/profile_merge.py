# Merge several different context profiles together and put them in a single profile file.
# usage: python profile_merge.py dir output

import sys
import os
import subprocess
import Distance

# Walk the directory to collect the files
directory = sys.argv[1]
files = []
for filename in os.listdir(directory):
	extension = os.path.splitext(filename)[1]
	if ("csv" in extension):
		files.append(directory + os.sep + filename)

# Run through each pair now.
OUTPUT_FILE = directory + os.sep + sys.argv[2]
output = open(OUTPUT_FILE, 'w')
wroteHeaders = False
for i in range(0, len(files)):
	#print("Processing " + files[i] + " and " + files[j])
	file1 = open(files[i])

	file1_contents = file1.read().split('\n')
	if not wroteHeaders:
		wroteHeaders = True
		headers = file1_contents[0].split(',')
		line = ""
		for header in headers:
			line = line + header + ","
		line = line[0:len(line) - 1]
		output.write(line + '\n')

	data = file1_contents[1].split(',') # index 0 contains feature headers
	line = ""
	for header in data:
		line = line + header + ","
	line = line[0:len(line) - 1]
	output.write(line + '\n')