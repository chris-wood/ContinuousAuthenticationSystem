# Run the pairwise distance calculations over a set of files in a directory
# usage: python distance_calculator.py dir

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
OUTPUT_FILE = directory + os.sep + "output"
output = open(OUTPUT_FILE, 'w')
for i in range(0, len(files)):
	for j in range(i + 1, len(files)):
		#print("Processing " + files[i] + " and " + files[j])
		file1 = open(files[i])
		file2 = open(files[j])

		file1_contents = file1.read().split('\n')
		f1contents = file1_contents[1].split(',') # index 0 contains feature headers

		file2_contents = file2.read().split('\n')
		f2contents = file2_contents[1].split(',') # index 0 contains feature headers

		data1 = []
		data2 = []
		for k in range(0, len(f1contents)):
			try:
				f1contents[k] = float(f1contents[k])
				data1.append(f1contents[k])
			except:
				pass
		for k in range(0, len(f2contents)):
			try:
				f2contents[k] = float(f2contents[k])
				data2.append(f2contents[k])
			except:
				pass

		indices = Distance.prune(data1, data2)
		#print("Euclidean: " + str(Distance.euclidean_distance(data1, data2, indices)))
		output.write(files[i] + "," + files[j] + "," + "euclidean" + "," + str(Distance.euclidean_distance(data1, data2, indices)) + "\n")
		#print("City: " + str(Distance.city_distance(data1, data2)))
		output.write(files[i] + "," + files[j] + "," + "city" + "," + str(Distance.city_distance(data1, data2)) + "\n")
		#print("Chebychev: " + str(Distance.chebychev_distance(data1, data2)))
		output.write(files[i] + "," + files[j] + "," + "chebychev" + "," + str(Distance.chebychev_distance(data1, data2)) + "\n")
		#print("Cosine: " + str(Distance.cosine_difference(data1, data2)))
		output.write(files[i] + "," + files[j] + "," + "cosine" + "," + str(Distance.cosine_difference(data1, data2)) + "\n")
		#print("Correlation: " + str(Distance.correlation_distance(data1, data2)))
		output.write(files[i] + "," + files[j] + "," + "correlation" + "," + str(Distance.correlation_distance(data1, data2)) + "\n")

