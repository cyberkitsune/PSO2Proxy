import plugins
import packetFactory
import data.clients
import data.players
from twisted.protocols import basic
from config import JSONConfig

ircSettings = JSONConfig("cfg/gchat-irc.config.json",
                         {'enabled': False, 'nick': "PSO2IRCBot", 'server': '', 'port': 6667, 'channel': ""}, True)

ircMode = ircSettings.get_key('enabled')
ircNick = ircSettings.get_key('nick')
ircServer = (ircSettings.get_key('server'), ircSettings.get_key('port'))
ircChannel = ircSettings.get_key('channel')

chatPreferences = JSONConfig("cfg/gchat.prefs.json")

if ircMode:
    from twisted.words.protocols import irc
    from twisted.internet import reactor, protocol

    ircBot = None

    # noinspection PyUnresolvedReferences
    class GChatIRC(irc.IRCClient):
        currentPid = 0
        userIds = {}

        def __init__(self):
            global ircNick
            self.nickname = ircNick

        def get_user_id(self, user):
            if user not in self.userIds:
                self.userIds[user] = self.currentPid
                self.currentPid += 1
            return self.userIds[user]

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
                print("[GlobalChat] [IRC] <%s> %s" % (user.split("!")[0], msg))
                for client in data.clients.connectedClients.values():
                    if client.get_preferences()['globalChat'] and client.get_handle() is not None:
                        client.get_handle().send_crypto_packet(
                            packetFactory.TeamChatPacket(self.get_user_id(user.split("!")[0]),
                                                         "[GIRC-%s]" % user.split("!")[0], msg).build())

        def action(self, user, channel, msg):
            if channel == self.factory.channel:
                print("[GlobalChat] [IRC] * %s %s" % (user, msg))
                for client in data.clients.connectedClients.values():
                    if client.get_preferences()['globalChat'] and client.get_handle() is not None:
                        client.get_handle().send_crypto_packet(
                            packetFactory.TeamChatPacket(self.get_user_id(user.split("!")[0]),
                                                         "[GIRC-%s]" % user.split("!")[0], "* %s" % msg).build())

        def send_global_message(self, user, message):
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


@plugins.on_start_hook
def create_preferences():
    global chatPreferences
    global ircMode
    if ircMode:
        global ircChannel
        global ircServer
        bot = GIRCFactory(ircChannel)
        reactor.connectTCP(ircServer[0], ircServer[1], bot)


# noinspection PyUnresolvedReferences
@plugins.on_connection_hook
def check_config(user):
    global chatPreferences
    if user.playerId in data.clients.connectedClients:
        client_preferences = data.clients.connectedClients[user.playerId].get_preferences()
        if 'globalChat' not in client_preferences:
            if chatPreferences.keyExists(user.playerId):
                client_preferences['globalChat'] = chatPreferences.getKey(user.playerId)['toggle']
            else:
                client_preferences['globalChat'] = True
                chatPreferences.setKey(user.playerId, {'toggle': True})
            if client_preferences['globalChat']:
                user.send_crypto_packet(packetFactory.SystemMessagePacket(
                    "[Proxy] {red}Global chat is enabled, use |g <Message> to chat and |goff to disable it.",
                    0x3).build())
            else:
                user.send_crypto_packet(packetFactory.SystemMessagePacket(
                    "[Proxy] {red}Global chat is disabled, use |gon to enable it and use |g <Message> to chat.",
                    0x3).build())
        data.clients.connectedClients[user.playerId].set_preferences(client_preferences)


# noinspection PyUnresolvedReferences
@plugins.CommandHook("gon", "Enable global chat.")
def enable(context, params):
    global chatPreferences
    preferences = data.clients.connectedClients[context.playerId].get_preferences()
    preferences['globalChat'] = True
    context.send_crypto_packet(
        packetFactory.SystemMessagePacket("[GlobalChat] Global chat enabled for you.", 0x3).build())
    data.clients.connectedClients[context.playerId].set_preferences(preferences)
    new_preferences = chatPreferences.getKey(context.playerId)
    new_preferences['toggle'] = True
    chatPreferences.setKey(context.playerId, new_preferences)
    savePrefs()


# noinspection PyUnresolvedReferences
@plugins.CommandHook("goff", "Disable global chat.")
def disable(context, params):
    preferences = data.clients.connectedClients[context.playerId].get_preferences()
    preferences['globalChat'] = False
    context.send_crypto_packet(
        packetFactory.SystemMessagePacket("[GlobalChat] Global chat disabled for you.", 0x3).build())
    data.clients.connectedClients[context.playerId].set_preferences(preferences)
    new_preferences = chatPreferences.getKey(context.playerId)
    new_preferences['toggle'] = False
    chatPreferences.setKey(context.playerId, new_preferences)


# noinspection PyUnresolvedReferences
@plugins.CommandHook("g", "Chat in global chat.")
def chat(context, params):
    global ircMode
    if isinstance(context, basic.LineReceiver):
        if ircMode:
            global ircBot
            if ircBot is not None:
                import unicodedata

                ircBot.send_global_message(
                    "Console",
                    unicodedata.normalize('NFKD', params[2:]).encode('ascii', 'ignore'))
        for client in data.clients.connectedClients.values():
            if client.get_preferences()['globalChat'] and client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
                    packetFactory.TeamChatPacket(0x1, "[GCONSOLE]",
                                                 params[2:]).build())
        return
    if not data.clients.connectedClients[context.playerId].get_preferences()['globalChat']:
        context.send_crypto_packet(packetFactory.SystemMessagePacket(
            "[GlobalChat] You do not have global chat enabled, and can not send a global message.", 0x3).build())
        return
    print("[GlobalChat] <%s> %s" % (data.players.playerList[context.playerId][0], params[3:]))
    if ircMode:
        global ircBot
        if ircBot is not None:
            import unicodedata

            ircBot.send_global_message(
                unicodedata.normalize('NFKD', data.players.playerList[context.playerId][0]).encode('ascii', 'ignore'),
                unicodedata.normalize('NFKD', params[3:]).encode('ascii', 'ignore'))
    for client in data.clients.connectedClients.values():
        if client.get_preferences()['globalChat'] and client.get_handle() is not None:
            client.get_handle().send_crypto_packet(
                packetFactory.TeamChatPacket(context.playerId, "[G-%s]" % data.players.playerList[context.playerId][0],
                                             params[3:]).build())

