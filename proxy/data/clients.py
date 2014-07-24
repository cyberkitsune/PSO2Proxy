import blocks

connectedClients = {}

class ClientData(object):
	"""docstring for ClientData"""
	def __init__(self, ipAddress, segaId, handle):
		self.ipAddress = ipAddress
		self.segaId = segaId
		self.handle = handle
	def getHandle(self):
		return self.handle
	def setHandle(self, handle):
		self.handle = handle

def addClient(handle):
	connectedClients[handle.playerId] = ClientData(handle.transport.getPeer().host, handle.myUsername, handle)

def removeClient(handle):
	del connectedClients[handle.playerId]

def populateData(handle):
	cData = connectedClients[handle.playerId]
	handle.myUsername = cData.segaId
	if handle.transport.getHost().port in blocks.blockList:
		bName = blocks.blockList[handle.transport.getHost().port][1]
	else:
		bName = None
	print("[ShipProxy] %s has successfully changed blocks to %s!" % (handle.myUsername, bName))
	handle.loaded = True
