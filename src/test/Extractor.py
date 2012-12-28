'''
File: Extractor.py
Author: Christopher Wood, caw4567@rit.edu
'''

import socket
import threading
#import Consumer # the location of the queue for us to access
import Queue # thread-safe queue for producer/consumer implementations
import StatObj # the user profile object
from time import clock, time # for time-based extraction
import sqlite3 # for user profile storage and dynamic updating

class Extractor(threading.Thread):
	'''
	This class is responsible for extracting features from the consumer queue
	on a window or time basis, and then perform feature extraction on the data 
	that was collected.
	'''

	# The epoch window for collecting keystrokes from the consumer's buffer
	TIME_WINDOW = 5
	BUFFER_SIZE = 10 # test value... this will have to be larger in practice

	def __init__(self, serv, queue):
		threading.Thread.__init__(self)
		self.server = serv
		self.running = True
		self.queue = queue
		print("Extractor created.")

	def run(self):
		print("Beginning extractor loop.")
		time = clock()
		while self.running:
			diff = clock() - time
			if not ((diff < self.TIME_WINDOW) and (self.queue.qsize() < self.BUFFER_SIZE)):
				bucket = []
				while (not self.queue.empty()): # drain the queue!
					bucket.append(self.queue.get())
				#self.extract(bucket)
				time = clock()

	def processBucket(self, bucket):
		'''
		This method is responsible for processing the contents in the queue.

		TODO: expand on this comment...
		TODO: pull code from the common.py feature extraction logic
		'''
		print("Bucket contents.:")
		print(bucket)

	def extract(self, bucket):
		# define the regex used to split log lines
		line_re = re.compile(r"^(\d+)\s+(\d+)\s+KEY_(DOWN|UP)\s*$")
    
		states = {}     # map of key codes to the last seen state/time
		stats = {}      # map of key codes to statistics
    
		recent_press_lengths = deque()
		average_press_length = 0.0
    
		# iterate through lines in the log
		for line in f:
			# split the line
			m = line_re.match(line)
			if m is None:
				if verbose:
					print "invalid log line"
				continue    # invalid lines are ignored silently
			ts, code, down = m.groups()
			ts = int(ts)
			code = int(code)
			down = (down == "DOWN")
        
			try:
				last_ts, last_state = states[code]
				if down != last_state:  # state is changing
					if down:        # key is being pressed
						pass
					else:           # key is being released
						press_length = float(ts - last_ts)
                    
						# if ready, find the relative press length
						if len(recent_press_lengths) == AVERAGE_WINDOW:
							relative_length = press_length / average_press_length
                        
							# update the average (excluding outliers)
							if relative_length > 1.0/OUTLIER_SCALE and relative_length < OUTLIER_SCALE:
								# update the key stats
								try:
									stats[code].update(relative_length)
								except KeyError:
									stats[code] = stats_obj = StatObj()
									stats_obj.update(relative_length)
                        
								# remove the oldest value
								average_press_length -= recent_press_lengths.popleft()
                            
								# add the next value to the average
								recent_press_lengths.append(press_length/AVERAGE_WINDOW)
								average_press_length += recent_press_lengths[-1]
							else:
								if verbose:
									print "  outlier:", relative_length, code, ts
						else:
							# average is not yet stable (keep adding values)
							recent_press_lengths.append(press_length/AVERAGE_WINDOW)
							average_press_length += recent_press_lengths[-1]
					# update the state map with the new state
					states[code] = (ts, down)
			except KeyError:
				# never seen before - always add to the map
				states[code] = (ts, down)
        
		# all data had been added, compute derived stats
		for code, stats_obj in stats.iteritems():
			stats_obj.finalize()
