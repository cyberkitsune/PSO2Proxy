import plugins, packetFactory, json, os
import data.clients, data.players

gcUserPrefs = {}
ircMode = True

if ircMode:
	from twisted.words.protocols import irc
	from twisted.internet import reactor, protocol

	ircBot = None
	channel = "#pso2proxygchat"

	class GChatIRC(irc.IRCClient):
		nickname = "PSO2IRCBot"

		def connectionMade(self):
			irc.IRCClient.connectionMade(self)
			print("[GlobalChat] IRC Connected!")

		def connectionLost(self, reason):
			irc.IRCClient.connectionLost(self, reason)
			print("[GlobalChat] IRC Connection lost!")

		def signedOn(self):
			global ircBot
			self.join(self.factory.channel)
			print("[GlobalChat] Joined %s" % self.factory.channel)
			ircBot = self

		def privmsg(self, user, channel, msg):
			if channel == self.factory.channel:
				print("[GlobalChat] [IRC] <%s> %s" % (user, msg))
				for client in data.clients.connectedClients.values():
					if client.getPrefs()['globalChat'] and client.getHandle() is not None:
						client.getHandle().sendCryptoPacket(packetFactory.TeamChatPacket(0x0, "[GIRC-%s]" % user.split("!")[0], msg).build())

		def action(self, user, channel, msg):
			if channel == self.factory.channel:
				print("[GlobalChat] [IRC] * %s %s" % (user, msg))
				for client in data.clients.connectedClients.values():
					if client.getPrefs()['globalChat'] and client.getHandle() is not None:
						client.getHandle().sendCryptoPacket(packetFactory.TeamChatPacket(0x0, "[GIRC-%s]" % user.split("!")[0], "* %s" % msg).build())

		def sendGmessage(self, user, message):
			self.msg(self.factory.channel, "[G] <%s> %s" % (user, message))

	class GIRCFactory(protocol.ClientFactory):
		"""docstring for ClassName"""
		def __init__(self, channel):
			self.channel = channel

		def buildProtocol(self, addr):
			p = GChatIRC()
			p.factory = self
			return p

		def clientConnectionLost(self, connector, reason):
			connector.connect()		

@plugins.onStartHook
def createPrefs():
	global gcUserPrefs
	global ircMode
	if not os.path.exists("cfg/gchat.prefs.json"):
		f = open('cfg/gchat.prefs.json', 'w')
		f.write(json.dumps(gcUserPrefs))
		f.close()
		print("[GlobalChat] Created user prefrences.")
	else:
		f = open('cfg/gchat.prefs.json', 'r')
		prefs = f.read()
		f.close()
		gcUserPrefs = json.loads(prefs)
		print('[GlobalChat] Loaded %i users prefrences.' % len (gcUserPrefs))
	if ircMode:
		global channel
		bot = GIRCFactory(channel)
		reactor.connectTCP("irc.badnik.net", 6667, bot)

@plugins.onConnectionHook
def checkConfig(user):
	global gcUserPrefs
	if user.playerId in data.clients.connectedClients:
		clientPrefs = data.clients.connectedClients[user.playerId].getPrefs()
		if 'globalChat' not in clientPrefs:
			if user.playerId in gcUserPrefs:
				clientPrefs['globalChat'] = gcUserPrefs[user.playerId]['toggle']
			else:
				clientPrefs['globalChat'] = True
				gcUserPrefs[user.playerId] = {}
				gcUserPrefs[user.playerId]['toggle'] = True
				savePrefs()
			if clientPrefs['globalChat'] == True:
				user.sendCryptoPacket(packetFactory.ChatPacket(user.playerId, "[Proxy] {red}Global chat is enabled, use |g <Message> to chat and |goff to disable it.").build())
			else:
				user.sendCryptoPacket(packetFactory.ChatPacket(user.playerId, "[Proxy] {red}Global chat is disabled, use |gon to enable it and use |g <Message> to chat.").build())
		data.clients.connectedClients[user.playerId].setPrefs(clientPrefs)

def savePrefs():
	f = open('cfg/gchat.prefs.json', 'w')
	f.write(json.dumps(gcUserPrefs))
	f.close()
	print("[GlobalChat] Saved user prefrences.")

@plugins.commandHook("gon")
def enable(context, params):
	global gcUserPrefs
	prefs = data.clients.connectedClients[context.playerId].getPrefs()
	prefs['globalChat'] = True
	context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] Global chat enabled for you.").build())
	data.clients.connectedClients[context.playerId].setPrefs(prefs)
	gcUserPrefs[context.playerId]['toggle'] = True
	savePrefs()


@plugins.commandHook("goff")
def disable(context, params):
	prefs = data.clients.connectedClients[context.playerId].getPrefs()
	prefs['globalChat'] = False
	context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] Global chat disabled for you.").build())
	data.clients.connectedClients[context.playerId].setPrefs(prefs)
	data.clients.connectedClients[context.playerId].setPrefs(prefs)
	gcUserPrefs[context.playerId]['toggle'] = False
	savePrefs()

@plugins.commandHook("g")
def chat(context, params):
	global ircMode
	if not data.clients.connectedClients[context.playerId].getPrefs()['globalChat']:
		context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] You do not have global chat enabled, and can not send a global message.").build())
		return
	print("[GlobalChat] <%s> %s" % (data.players.playerList[context.playerId][0], params[3:]))
	if ircMode:
		global ircBot
		if ircBot is not None:
			import unicodedata
			ircBot.sendGmessage(unicodedata.normalize('NFKD', data.players.playerList[context.playerId][0]).encode('ascii','ignore'), unicodedata.normalize('NFKD', params[3:]).encode('ascii','ignore'))
	for client in data.clients.connectedClients.values():
		if client.getPrefs()['globalChat'] and client.getHandle() is not None:
			client.getHandle().sendCryptoPacket(packetFactory.TeamChatPacket(context.playerId, "[G-%s]" % data.players.playerList[context.playerId][0], params[3:]).build())

