import socket
import threading
import struct
import string

class ClientObject(object):
    def __init__(self,clientInfo):
        self.sock = clientInfo[0]
        self.address = clientInfo[1]

    def update(self,message):
    	'''
    	Send data back to the client. 
    	This will be primarily used for debug purposes.
    	'''
        self.sock.send(message.encode())