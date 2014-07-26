import packetFactory, bans, data.clients, data.players, data.blocks
from twisted.protocols import basic
from twisted.python import log

commandList = {}

class CommandHandler(object):
	def __init__(self, commandName):
		self.commandName = commandName
	def __call__(self, f):
		global commandList
		commandList[self.commandName] = f

@CommandHandler("help")
def aboutMe(sender, params):
	if not isinstance(sender, basic.LineReceiver):
		string = '[Command] %s, how may I help you?' % sender.transport.getPeer().host
		sender.sendCryptoPacket(packetFactory.ChatPacket(sender.playerId, string).build())
	else:
		sender.transport.write("[Command] Hello Console! Valid commands: %s\n" % ', '.join(commandList.keys()) )
@CommandHandler("reloadbans")
def reloadBans(sender, params):
	if isinstance(sender, basic.LineReceiver):
		bans.loadBans()

@CommandHandler("listbans")
def listBans(sender, params):
	if isinstance(sender, basic.LineReceiver):
		sender.transport.write(''.join(bans.banList))

@CommandHandler("clients")
def listClients(sender, params):
	if isinstance(sender, basic.LineReceiver):
		print("[ClientList] === Connected Clients ===")
		for ip, client in data.clients.connectedClients.iteritems():
			cHandle = client.getHandle()
			cHost = cHandle.transport.getPeer().host
			cSID = cHandle.myUsername
			if cSID is not None:
				cSID = cSID.rstrip('\0')
			cPID = cHandle.playerId
			if cPID in data.players.playerList:
				cPName = data.players.playerList[cPID][0].rstrip('\0')
			else:
				cPName = None
			blockNum = cHandle.transport.getHost().port
			if blockNum in data.blocks.blockList:
				cPBlock = data.blocks.blockList[blockNum][1].rstrip('\0')
			else:
				cPBlock = None
			print("[ClientList] IP: %s SEGA ID: %s Player ID: %s Player Name: %s Block: %s" % (cHost, cSID, cPID, cPName, cPBlock))
		print("[ClientList] There are %i clients in total." % len(data.clients.connectedClients))

@CommandHandler("globalmsg")
def globalMessage(sender, params):
	if isinstance(sender, basic.LineReceiver):
		message = params.split(' ',1)[1]
		for client in data.clients.connectedClients.values():
			client.getHandle().sendCryptoPacket(packetFactory.GoldGlobalMessagePacket("[Proxy Global Message] %s" % message).build())
		print("[ShipProxy] Sent global message!", ...)