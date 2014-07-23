connectedClients = {}

class ClientData(object):
	"""docstring for ClientData"""
	def __init__(self, ipAddress, handle):
		self.ipAddress = ipAddress
		self.handle = handle
	def getHandle(self):
		return self.handle

def addClient(handle):
	connectedClients[handle.transport.getPeer().host] = ClientData(handle.transport.getPeer().host, handle)

def removeClient(handle):
	del connectedClients[handle.transport.getPeer().host]
