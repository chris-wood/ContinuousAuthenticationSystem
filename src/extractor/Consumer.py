'''
File: Consumer.py
Author: Christopher Wood, caw4567@rit.edu
Usage: 
	python consumer.py
'''

# Needed libraries
import time
import sys
import socket
import threading
import Queue # thread-safe queue for producer/consumer implementations

# The client handler thread
import Handler
import ClientObject
import KeyloggerFeatureExtractor
import ProfileManager
import Classifier

class Server(threading.Thread):
	'''
	This the server class that is responsible for spawning client handler threads
	for all incoming connections. It is set to only accept incoming connections from the
	localhost, but network capabilities would also be possible.
	'''

	# Socket configuration parameters
	HOST = 'localhost'
	PORT = 9998
	BUFFSIZE = 1024
	running  = False

	# The socket object
	serverSock = None

	# Client thread handlers (in case the keylogger needs to restart)
	clientList = []
	handler = None

	# The data bucket
	queue = Queue.Queue()

	def __init__(self):
		threading.Thread.__init__(self)
		self.running = False
		print("Consumer created.")

	def run(self):
		address = (self.HOST, self.PORT)
		self.running = True
		self.serverSock = socket.socket()
		self.serverSock.bind(address)
		self.serverSock.listen(2)

		# Create the handler thread
		self.handler = Handler.Handler(self, self.queue)
		self.handler.start()

		# Wait for incoming connections
		while self.running:
			clientInfo = self.serverSock.accept()
			print("Client connected from {}.".format(clientInfo[1]))
			self.handler.clientList.append(ClientObject.ClientObject(clientInfo))

		serverSock.close()
		print("- end -")

def help():
	print("System commands:")
	print("  quit    - shut down the system.")
	print("  verbose - toggle console output")

def main():
	print("Starting keylogger consumer. Building the thread components.")
	server = Server()
	server.start()
	profileManager = ProfileManager.ProfileManager()
	classifier = Classifier.Classifier(profileManager)
	extractor = KeyloggerFeatureExtractor.KeyloggerFeatureExtractor(server, server.queue, profileManager)
	extractor.start()
	classifier.start()

	time.sleep(1)
	print("------------------------------------")
	print("Type 'help' or '?' for available commands.")
	print("------------------------------------")
	userInput = raw_input(">> ")
	if (userInput == 'help' or userInput == '?'):
		help()
	while (userInput != 'quit'):
		userInput = raw_input(">> ")
		# TODO: switch on the input and handle it accordingly

	print("Shutting down the system...")
	#classifier.stop()
	#extractor.stop()
	#server.stop()
	sys.exit(0)

# Let it rip.
main()
