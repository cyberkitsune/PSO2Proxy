import commands
import config
from config import YAMLConfig
import data.clients
import data.players
import json
import packetFactory
import plugins
from PSO2DataTools import check_irc_with_pso2
from PSO2DataTools import check_pso2_with_irc
from PSO2DataTools import replace_irc_with_pso2
from PSO2DataTools import replace_pso2_with_irc
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.words.protocols import irc

try:
    import PSO2PDConnector
    redisEnabled = True
except ImportError:
    redisEnabled = False

ircSettings = YAMLConfig("cfg/gchat-irc.config.yml",
                         {'enabled': False, 'nick': "PSO2IRCBot", 'server': '', 'port': 6667, 'svname': 'NickServ', 'svpass': '', 'channel': "", 'output': True, 'autoexec': []}, True)

ircBot = None
ircMode = ircSettings.get_key('enabled')
ircOutput = ircSettings.get_key('output')
ircNick = ircSettings.get_key('nick')
ircServer = (ircSettings.get_key('server'), ircSettings.get_key('port'))
ircChannel = ircSettings.get_key('channel')
ircServicePass = ircSettings.get_key('svpass')
ircServiceName = ircSettings.get_key('svname')

gchatSettings = YAMLConfig("cfg/gchat.config.yml", {'displayMode': 0, 'bubblePrefix': '', 'systemPrefix': '{whi}', 'prefix': ''}, True)


def doRedisGchat(message):
    gchatMsg = json.loads(message['data'])
    strgchatmsg = str(gchatMsg['text'].encode('utf-8'))
    if not check_irc_with_pso2(strgchatmsg):
        return
    if gchatMsg['server'] == PSO2PDConnector.connector_conf['server_name']:
        return
    if gchatMsg['sender'] == 1:
        for client in data.clients.connectedClients.values():
            if client.preferences.get_preference('globalChat') and client.get_handle() is not None:
                if lookup_gchatmode(client.preferences) == 0:
                    client.get_handle().send_crypto_packet(packetFactory.TeamChatPacket(gchatMsg['playerId'], "[GIRC] %s" % gchatMsg['playerName'], "%s%s" % (client.preferences.get_preference('globalChatPrefix'), replace_irc_with_pso2(strgchatmsg).decode('utf-8'))).build())
                else:
                    client.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[GIRC] <%s> %s" % (gchatMsg['playerName'], "%s%s" % (client.preferences.get_preference('globalChatPrefix'), replace_irc_with_pso2(strgchatmsg).decode('utf-8'))), 0x3).build())
    else:
        if ircMode:
                global ircBot
                if ircBot is not None:
                    ircBot.send_global_message(gchatMsg['ship'], str(gchatMsg['playerName'].encode('utf-8')), strgchatmsg, str(gchatMsg['server']))
        for client_data in data.clients.connectedClients.values():
                if client_data.preferences.get_preference('globalChat') and client_data.get_handle() is not None:
                    if lookup_gchatmode(client_data.preferences) == 0:
                        client_data.get_handle().send_crypto_packet(packetFactory.TeamChatPacket(gchatMsg['playerId'], "(%s) [G-%02i] %s" % (gchatMsg['server'], gchatMsg['ship'], gchatMsg['playerName']), "%s%s" % (client_data.preferences.get_preference('globalChatPrefix'), gchatMsg['text'])).build())
                    else:
                        client_data.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("(%s) [G-%02i] <%s> %s" % (gchatMsg['server'], gchatMsg['ship'], gchatMsg['playerName'], "%s%s" % (client_data.preferences.get_preference('globalChatPrefix'), gchatMsg['text'])), 0x3).build())


if redisEnabled:
    PSO2PDConnector.thread.pubsub.subscribe(**{'plugin-message-gchat': doRedisGchat})

if ircMode:
    # noinspection PyUnresolvedReferences
    class GChatIRC(irc.IRCClient):
        currentPid = 0
        userIds = {}

        def __init__(self):
            global ircNick
            self.nickname = ircNick
            self.ircOutput = ircOutput

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

	def joinChan(self):
	    global ircBot
	    try:
                if self.factory.channel[:1] in ["#", "!", "+", "&"]:
                    self.join(self.factory.channel)
                    print("[GlobalChat] Joined %s" % self.factory.channel)
                    ircBot = self
                else:
                    raise NameError("[GlobalChat] Failed to join %s channel must contain a #, !, + or & before the channel name" % self.factory.channel)
            except NameError as ne:
                print(ne)
                log.msg(ne)

        def signedOn(self):
            global ircBot
            global ircServicePass
            for command in ircSettings.get_key('autoexec'):
                self.sendLine(command)
                print("[IRC-AUTO] >>> %s" % command)
	    if ircServicePass == '':
	        self.joinChan(self)
			
        def privmsg(self, user, channel, msg):
            if not check_irc_with_pso2(msg):
                return
            if channel == self.factory.channel:
                if self.ircOutput is True:
                    print("[GlobalChat] [IRC] <%s> %s" % (user.split("!")[0], replace_irc_with_pso2(msg).decode('utf-8')))
                if redisEnabled:
                    PSO2PDConnector.db_conn.publish("plugin-message-gchat", json.dumps({'sender': 1, 'text': replace_irc_with_pso2(msg).decode('utf-8'), 'server': PSO2PDConnector.connector_conf['server_name'], 'playerName': user.split("!")[0], 'playerId': self.get_user_id(user.split("!")[0])}))
                for client in data.clients.connectedClients.values():
                    if client.preferences.get_preference('globalChat') and client.get_handle() is not None:
                        if lookup_gchatmode(client.preferences) == 0:
                            client.get_handle().send_crypto_packet(packetFactory.TeamChatPacket(self.get_user_id(user.split("!")[0]), "[GIRC] %s" % user.split("!")[0], "%s%s" % (client.preferences.get_preference('globalChatPrefix'), replace_irc_with_pso2(msg).decode('utf-8'))).build())
                        else:
                            client.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[GIRC] <%s> %s" % (user.split("!")[0], "%s%s" % (client.preferences.get_preference('globalChatPrefix'), replace_irc_with_pso2(msg).decode('utf-8'))), 0x3).build())
            else:
                print("[IRC] <%s> %s" % (user, msg))

        def noticed(self, user, channel, message):
            print("[IRC] [NOTICE] %s %s" % (user, message))
            if user.split("!")[0] == 'NickServ' and 'registered' in message:
                global ircServicePass
                global ircServiceName
                global ircBot
                if ircServicePass is not '':
                    ircBot = self
                    ircBot.msg(ircServiceName, "identify %s" % (ircServicePass))
                    print("[IRC] Sent identify command to %s." % (ircServiceName))
	            self.joinChan(self)

        def action(self, user, channel, msg):
            if not check_irc_with_pso2(msg):
                return
            if channel == self.factory.channel:
                if self.ircOutput is True:
                    print("[GlobalChat] [IRC] * %s %s" % (user, replace_irc_with_pso2(msg).decode('utf-8')))
                for client in data.clients.connectedClients.values():
                    if client.preferences.get_preference('globalChat') and client.get_handle() is not None:
                        if lookup_gchatmode(client.preferences) == 0:
                            client.get_handle().send_crypto_packet(packetFactory.TeamChatPacket(self.get_user_id(user.split("!")[0]), "[GIRC] %s" % user.split("!")[0], "* %s%s" % (client.preferences.get_preference('globalChatPrefix'), replace_irc_with_pso2(msg).decode('utf-8'))).build())
                        else:
                            client.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[GIRC] <%s> * %s" % (user.split("!")[0], "%s%s" % (client.preferences.get_preference('globalChatPrefix'), replace_irc_with_pso2(msg).decode('utf-8'))), 0x3).build())

        def send_global_message(self, ship, user, message, server=None):
            if not check_pso2_with_irc(message):
                return
            if server is None:
                self.msg(self.factory.channel, "[G-%02i] <%s> %s" % (ship, user, replace_pso2_with_irc(message)))
            else:
                self.msg(self.factory.channel, "(%s) [G-%02i] <%s> %s" % (server, ship, user, replace_pso2_with_irc(message)))

        def send_channel_message(self, message):
            self.msg(self.factory.channel, message)

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

        def clientConnectionFailed(self, connector, reason):
            connector.connect()


def lookup_gchatmode(client_preferences):
    if client_preferences['gchatMode'] is not -1:
        return client_preferences['gchatMode']
    return gchatSettings['displayMode']


@plugins.on_start_hook
def create_preferences():
    global ircMode
    if ircMode:
        global ircChannel
        global ircServer
        bot = GIRCFactory(ircChannel)
        reactor.connectTCP(ircServer[0], ircServer[1], bot)


# noinspection PyUnresolvedReferences
@plugins.on_initial_connect_hook
def check_config(user):
    global ircMode
    if user.playerId in data.clients.connectedClients:
        client_preferences = data.clients.connectedClients[user.playerId].preferences
        if not client_preferences.has_preference("globalChat"):
            client_preferences.set_preference("globalChat", True)
        if not client_preferences.has_preference("globalChatPrefix"):
            client_preferences.set_preference("globalChatPrefix", gchatSettings['prefix'])
        if client_preferences.get_preference('globalChat'):
            user.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Proxy] {yel}Global chat is enabled. Use %sg <Message> to chat, %sgoff to disable it, and %sgmode to toggle team/system chat mode." % (config.globalConfig.get_key('commandPrefix'), config.globalConfig.get_key('commandPrefix'), config.globalConfig.get_key('commandPrefix')),
                0x3).build())
        else:
            user.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Proxy] {yel}Global chat is disabled. Use %sgon to enable it, %sg <Message> to chat, and %sgmode to toggle team/system chat mode." % (config.globalConfig.get_key('commandPrefix'), config.globalConfig.get_key('commandPrefix'), config.globalConfig.get_key('commandPrefix')),
                0x3).build())
        if not client_preferences.has_preference("gchatMode"):
            client_preferences['gchatMode'] = -1


@plugins.CommandHook("gmode", "Sets your global chat display mode")
class GChatModeCommand(commands.Command):
    def call_from_client(self, client):
        if client.playerId is not None:
            client_preferences = data.clients.connectedClients[client.playerId].preferences
            if client_preferences['gchatMode'] == -1:
                client_preferences['gchatMode'] = 0
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Global chat will now come through team chat.", 0x3).build())
            elif client_preferences['gchatMode'] == 0:
                client_preferences['gchatMode'] = 1
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Global chat will now come through system chat.", 0x3).build())
            elif client_preferences['gchatMode'] == 1:
                client_preferences['gchatMode'] = -1
                if gchatSettings['displayMode'] == 0:
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Global chat will now come through team chat. (Default)", 0x3).build())
                else:
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Global chat will now come through system chat. (Default)", 0x3).build())


@plugins.CommandHook("gprefix", "Changes your chat prefix / color.")
class GPrefixCommand(commands.Command):
    def call_from_client(self, client):
        if client.playerId is not None:
            client_prefs = data.clients.connectedClients[client.playerId].preferences
            if len(self.args.split(" ", 1)) < 2:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. Usage: gprefix <Prefix or PSO2 Color Code>", 0x3).build())
                return
            prefix = self.args.split(" ", 1)[1]
            client_prefs['globalChatPrefix'] = prefix
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Your prefix has been set.", 0x3).build())


@plugins.CommandHook("irc")
class IRCCommand(commands.Command):
    def call_from_console(self):
        global ircMode
        global ircBot
        if ircMode and ircBot is not None:
            ircBot.sendLine(self.args.split(" ", 1)[1].encode('utf-8'))
            return "[IRC] >>> %s" % self.args.split(" ", 1)[1]


@plugins.CommandHook("ident")
class IdentCommand(commands.Command):
    def call_from_console(self):
        global ircMode
        global ircBot
        global ircServiceName
        global ircServicePass
        if ircMode and ircBot is not None:
            ircBot.msg(ircServiceName, "identify %s" % (ircServicePass))
            return "[IRC] Sent identify command to %s." % (ircServiceName)


@plugins.CommandHook("gon", "Enable global chat.")
class EnableGChat(commands.Command):
    def call_from_client(self, client):
        preferences = data.clients.connectedClients[client.playerId].preferences
        if not preferences['globalChat']:
            preferences['globalChat'] = True
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GlobalChat] Global chat enabled for you.", 0x3).build())
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GlobalChat] You already have global chat enabled.", 0x3).build())

    def call_from_console(self):
        if ircMode:
            global ircBot
            if ircBot is not None:
                ircBot.ircOutput = True
        return "[GlobalChat] Global chat enabled for Console."


@plugins.CommandHook("goff", "Disable global chat.")
class DisableGChat(commands.Command):
    def call_from_client(self, client):
        preferences = data.clients.connectedClients[client.playerId].preferences
        if preferences["globalChat"]:
            preferences['globalChat'] = False
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GlobalChat] Global chat disabled for you.", 0x3).build())
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GlobalChat] You already have global chat disabled.", 0x3).build())

    def call_from_console(self):
        if ircMode:
            global ircBot
            if ircBot is not None:
                ircBot.ircOutput = False
        return "[GlobalChat] Global chat disabled for Console."


@plugins.CommandHook("gmute", "[Admin Only] Mutes or somebody in gchat.", True)
class MuteSomebody(commands.Command):
    def call_from_client(self, client):
        """
        :param client: ShipProxy.ShipProxy
        """
        if len(self.args.split(" ", 1)) < 2:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. gmute <Player Name>").build())
            return
        user_to_mute = self.args.split(" ", 1)[1]
        if user_to_mute.isdigit() and int(user_to_mute) in data.clients.connectedClients:
            data.clients.connectedClients[int(user_to_mute)].preferences['chatMuted'] = True
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Muted %s." % user_to_mute, 0x3).build())
            return
        else:
            for player_id, player_data in data.players.playerList.iteritems():
                if player_data[0].rstrip("\0") == user_to_mute:
                    if player_id in data.clients.connectedClients:
                        data.clients.connectedClients[player_id].preferences['chatMuted'] = True
                        client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Muted %s." % player_data[0].rstrip("\0"), 0x3).build())
                        return
                    else:
                        client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0"), 0x3).build())
                        return

        client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s either is not connected or is not part of the proxy." % user_to_mute, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ", 1)) < 2:
            return "[Command] Invalid usage. gmute <Player Name>"
        user_to_mute = self.args.split(" ", 1)[1]
        if user_to_mute.isdigit() and int(user_to_mute) in data.clients.connectedClients:
            data.clients.connectedClients[int(user_to_mute)].preferences['chatMuted'] = True
            return "Muted %s by Player #" % user_to_mute
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = True
                    return "[Command] Muted %s." % player_data[0].rstrip("\0")
                else:
                    return "[Command] %s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0")
        return "[Command] %s either is not connected or is not part of the proxy." % user_to_mute


@plugins.CommandHook("gunmute", "[Admin Only] Mutes or unmutes somebody in gchat.", True)
class UnmuteSomebody(commands.Command):
    def call_from_client(self, client):
        """
        :param client: ShipProxy.ShipProxy
        """
        if len(self.args.split(" ", 1)) < 2:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. gunmute <Player Name>").build())
            return
        user_to_mute = self.args.split(" ", 1)[1]
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = False
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Unmuted %s." % player_data[0].rstrip("\0"), 0x3).build())
                else:
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0"), 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ", 1)) < 2:
            return "[Command] Invalid usage. gunmute <Player Name>"
        user_to_mute = self.args.split(" ", 1)[1]
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = False
                    return "[Command] Unmuted %s." % player_data[0].rstrip("\0")
                else:
                    return "[Command] %s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0")


@plugins.CommandHook("g", "Chat in global chat.")
class GChat(commands.Command):
    def call_from_client(self, client):
        global ircMode
        if not data.clients.connectedClients[client.playerId].preferences.get_preference('globalChat'):
            client.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[GlobalChat] You do not have global chat enabled, and can not send a global message.", 0x3).build())
            return
        if data.clients.connectedClients[client.playerId].preferences.has_preference("chatMuted") and data.clients.connectedClients[client.playerId].preferences['chatMuted']:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GChat] {red}You have been muted from GChat and can not talk in it. :(", 0x3).build())
            return
        print("[GlobalChat] <%s> %s" % (data.players.playerList[client.playerId][0], self.args[3:]))
        if redisEnabled:
                    PSO2PDConnector.db_conn.publish("plugin-message-gchat", json.dumps({'sender': 0, 'text': self.args[3:], 'server': PSO2PDConnector.connector_conf['server_name'], 'playerName': data.players.playerList[client.playerId][0], 'playerId': client.playerId, 'ship': data.clients.connectedClients[client.playerId].ship}))
        if ircMode:
            global ircBot
            if ircBot is not None:
                ircBot.send_global_message(data.clients.connectedClients[client.playerId].ship, data.players.playerList[client.playerId][0].encode('utf-8'), self.args[3:].encode('utf-8'))
        for client_data in data.clients.connectedClients.values():
            if client_data.preferences.get_preference('globalChat') and client_data.get_handle() is not None:
                if lookup_gchatmode(client_data.preferences) == 0:
                    client_data.get_handle().send_crypto_packet(packetFactory.TeamChatPacket(client.playerId, "[G-%02i] %s" % (data.clients.connectedClients[client.playerId].ship, data.players.playerList[client.playerId][0]), "%s%s" % (client_data.preferences.get_preference('globalChatPrefix'), self.args[3:])).build())
                else:
                    client_data.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[G-%02i] <%s> %s" % (data.clients.connectedClients[client.playerId].ship, data.players.playerList[client.playerId][0], "%s%s" % (client_data.preferences.get_preference('globalChatPrefix'), self.args[3:])), 0x3).build())

    def call_from_console(self):
        global ircMode
        if ircMode:
            global ircBot
            if ircBot is not None:
                ircBot.send_global_message(0, "Console", self.args[2:].encode('utf-8'))
        TCPacket = packetFactory.TeamChatPacket(0x999, "[GCONSOLE]", self.args[2:]).build()
        SMPacket = packetFactory.SystemMessagePacket("[GCONSOLE] %s%s" % (gchatSettings['prefix'], self.args[2:]), 0x3).build()
        for client in data.clients.connectedClients.values():
            if client.preferences.get_preference("globalChat") and client.get_handle() is not None:
                if lookup_gchatmode(client.preferences) == 0:
                    client.get_handle().send_crypto_packet(TCPacket)
                else:
                    client.get_handle().send_crypto_packet(SMPacket)
        return "[GlobalChat] <Console> %s" % sel
