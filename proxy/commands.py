import packetFactory, config, data.clients, data.players, data.blocks
from twisted.protocols import basic
from twisted.python import log
from twisted.internet import reactor

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

@CommandHandler("count")
def count(sender, params):
	if not isinstance(sender, basic.LineReceiver):
		string = '[Command] There are %s users currently connected to your proxy.' % len(data.clients.connectedClients)
		sender.sendCryptoPacket(packetFactory.ChatPacket(sender.playerId, string).build())
	else:
		print("[ShipProxy] There are %s users currently on the proxy." % len(data.clients.connectedClients))

@CommandHandler("reloadbans")
def reloadBans(sender, params):
	if isinstance(sender, basic.LineReceiver):
		config.loadBans()

@CommandHandler("listbans")
def listBans(sender, params):
	if isinstance(sender, basic.LineReceiver):
		sender.transport.write(''.join(config.banList))

@CommandHandler("ban")
def ban(sender, params):
	if isinstance(sender, basic.LineReceiver):
		args = params.split(' ')
		if len(args) < 3:
			print("[Command] Invalid usage! Proper usage, >>> ban <segaid/pid> <value>")
			return
		if args[1] == "segaid":
			if config.isIdBanned(args[2]):
				print("[Command] %s is already banned!" % args[2])
				return
			config.banList.append({'segaId' : args[2]})
			config.saveBans()
		elif args[1] == "pid":
			if config.isPlayerBanned(args[2]):
				print('[Command] %s is already banned!' % args[2])
				return
			config.banList.append({'playerId' : args[2]})
			config.saveBans()
		else:
			print("[Command] Invalid usage! Proper usage, >>> ban <segaid/pid> <value>")
			return

@CommandHandler("kick")
def kick(sender, params):
	if isinstance(sender, basic.LineReceiver):
		args = params.split(' ')
		if len(args) < 2:
			print("[Command] Invalid usage! Proper usage: >>> kick <playerId>")
			return
		if args[1] in data.clients.connectedClients:
			data.clients.connectedClients[args[1]].getHandle().transport.loseConnection()
			print("[Command] Kicked %s." % args[1])
		else:
			print("[Command] I couldn't find %s!" % args[1])

@CommandHandler("clients")
def listClients(sender, params):
	if isinstance(sender, basic.LineReceiver):
		print("[ClientList] === Connected Clients (%i total) ===" % len(data.clients.connectedClients))
		for ip, client in data.clients.connectedClients.iteritems():
			cHandle = client.getHandle()
			cHost = cHandle.transport.getPeer().host
			cSID = cHandle.myUsername
			if cSID is None:
				continue
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

@CommandHandler("globalmsg")
def globalMessage(sender, params):
	if isinstance(sender, basic.LineReceiver):
		if len(params.split(' ',1)) < 2:
			print("[ShipProxy] That message is not long enough!")
			return
		message = params.split(' ',1)[1]
		for client in data.clients.connectedClients.values():
			if client.getHandle() is not None:
				client.getHandle().sendCryptoPacket(packetFactory.GoldGlobalMessagePacket("[Proxy Global Message] %s" % message).build())
		print("[ShipProxy] Sent global message!")

@CommandHandler("exit")
def exit(sender, params):
	if isinstance(sender, basic.LineReceiver):
		print("[ShipProxy] Exiting...")
		reactor.callFromThread(reactor.stop)