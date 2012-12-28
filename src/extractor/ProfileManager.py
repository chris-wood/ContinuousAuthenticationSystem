'''
File: ProfileManager.py
Author: Christopher Wood, caw4567@rit.edu
'''

# For socket I/O programming
import socket
import threading
import Queue # thread-safe queue for producer/consumer implementations

DB = "profiles.csv"

class ProfileManager(object):
	'''
	This class buffers profiles collected during a classification window and is
	queried by the Classifier when needed.
	'''

	def __init__(self):
		self.profileMap = {}
		self.sessionList = []
		#self.loadProfiles(DB)

	def loadProfiles(self, file):
		'''
		Load the existing user profiles from the database
		'''
		try:
			print "Processing:", arg
			with open(arg, 'rb') as f:
				lines = f.readlines()
				data = lines.split(',')
				print("Loaded: " + str(data[0]))
				self.profileMap[data[0]] = data[1:] # the first field is the user ID
		except:
			print("Error reading " + file)

	def submitProfileVector(self, vector):
		self.sessionList.append(vector)

	def getSessionVectors(self):
		return self.sessionList

