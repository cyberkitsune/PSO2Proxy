import plugins, packetFactory
import data.clients, data.players

@plugins.onConnectionHook
def checkConfig(user):
	if user.playerId in data.clients.connectedClients:
		clientPrefs = data.clients.connectedClients[user.playerId].getPrefs()
		if 'globalChat' not in clientPrefs:
			clientPrefs['globalChat'] = True
		data.clients.connectedClients[user.playerId].setPrefs(clientPrefs)

@plugins.commandHook("gon")
def enable(context, params):
	prefs = data.clients.connectedClients[context.playerId].getPrefs()
	prefs['globalChat'] = True
	context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] Global chat enabled for this session.").build())
	data.clients.connectedClients[context.playerId].setPrefs(prefs)

@plugins.commandHook("goff")
def disable(context, params):
	prefs = data.clients.connectedClients[context.playerId].getPrefs()
	prefs['globalChat'] = False
	context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] Global chat disabled for this session.").build())
	data.clients.connectedClients[context.playerId].setPrefs(prefs)

@plugins.commandHook("g")
def chat(context, params):
	if not data.clients.connectedClients[context.playerId].getPrefs()['globalChat']:
		context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[GlobalChat] You do not have global chat enabled, and can not send a global message.").build())
		return
	for client in data.clients.connectedClients.values():
		if client.getPrefs()['globalChat'] and client.getHandle() is not None:
			client.getHandle().sendCryptoPacket(packetFactory.TeamChatPacket(context.playerId, data.players.playerList[context.playerId][0], "[G] %s" % params[3:]).build())
