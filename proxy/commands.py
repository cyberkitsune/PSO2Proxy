import packetFactory, bans, data.clients, data.players
from twisted.protocols import basic

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
		string = '[Command] %s, how may I help you?' % sender.getPeer().host
		sender.sendPacketCrypto(packetFactory.ChatPacket(sender.playerId, string).build())
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
		sender.transport.write("[ClientList] === Connected Clients ===\n")
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
			sender.transport.write(str("[ClientList] IP: %s SEGA ID: %s Player ID: %s Player Name: %s\n" % (cHost, cSID, cPID, cPName)))
		sender.transport.write("[ClientList] There are %i clients in total.\n" % len(data.clients.connectedClients))
