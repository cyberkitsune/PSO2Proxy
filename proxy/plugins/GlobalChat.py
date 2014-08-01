import plugins, packetFactory, json, os
import data.clients, data.players

gcUserPrefs = {}

@plugins.onStartHook
def createPrefs():
	global gcUserPrefs
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
	if not data.clients.connectedClients[context.playerId].getPrefs()['globalChat']:
		context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] You do not have global chat enabled, and can not send a global message.").build())
		return
	print("[GlobalChat] <%s> %s" % (data.players.playerList[context.playerId][0], params[3:]))
	for client in data.clients.connectedClients.values():
		if client.getPrefs()['globalChat'] and client.getHandle() is not None:
			client.getHandle().sendCryptoPacket(packetFactory.TeamChatPacket(context.playerId, data.players.playerList[context.playerId][0], "[G] %s" % params[3:]).build())
