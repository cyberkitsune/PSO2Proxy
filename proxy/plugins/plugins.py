packetFunctions = {}
commands = {}
onStart = []
onConnection = []
onConnectionLoss = []

class packetHook(object):
	def __init__(self, pktType, pktSubtype):
		self.pktType = pktType
		self.pktSubtype = pktSubtype

	def __call__(self, f):
		global packetFunctions
		packetFunctions[(self.pktType, self.pktSubtype)] = f

class commandHook(object):
	"""docstring for commandHook"""
	def __init__(self, command):
		self.command = command

	def __call__(self, f):
		global commands
		commands[self.command] = f

def onStartHook(f):
	global onStart
	onStart.append(f)

def onConnectionHook(f):
	global onConnection
	onConnection.append(f)

def onConnectionLossHook(f):
	global onConnectionLoss
	onConnectionLoss.append(f)