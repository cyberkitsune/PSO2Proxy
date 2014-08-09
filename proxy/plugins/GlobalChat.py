import plugins
import packetFactory
import data.clients
import data.players

from PSO2DataTools import replace_irc_with_pso2, replace_pso2_with_irc
from config import YAMLConfig
import config
from commands import Command

ircSettings = YAMLConfig("cfg/gchat-irc.config.yml",
                         {'enabled': False, 'nick': "PSO2IRCBot", 'server': '', 'port': 6667, 'channel': "", 'autoexec': []}, True)

ircMode = ircSettings.get_key('enabled')
ircNick = ircSettings.get_key('nick')
ircServer = (ircSettings.get_key('server'), ircSettings.get_key('port'))
ircChannel = ircSettings.get_key('channel')

gchatSettings = YAMLConfig("cfg/gchat.config.yml", {'displayMode': 0, 'prefix': ''}, True)

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
            for command in ircSettings.get_key('autoexec'):
                self.sendLine(command)
                print("[IRC-AUTO] >>> %s" % command)
            self.join(self.factory.channel)
            print("[GlobalChat] Joined %s" % self.factory.channel)
            ircBot = self

        def privmsg(self, user, channel, msg):
            if channel == self.factory.channel:
                print("[GlobalChat] [IRC] <%s> %s" % (user.split("!")[0], replace_irc_with_pso2(msg).decode('utf-8')))
                for client in data.clients.connectedClients.values():
                    if client.preferences.get_preference('globalChat') and client.get_handle() is not None:
                        if gchatSettings['displayMode'] == 0:
                            client.get_handle().send_crypto_packet(
                                packetFactory.TeamChatPacket(self.get_user_id(user.split("!")[0]), "[GIRC] %s" % user.split("!")[0], "%s%s" % (gchatSettings['prefix'], replace_irc_with_pso2(msg).decode('utf-8'))).build())
                        else:
                            client.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[GIRC] <%s> %s" % (user.split("!")[0], "%s%s" % (gchatSettings['prefix'], replace_irc_with_pso2(msg).decode('utf-8'))), 0x3).build())
            else:
                print("[IRC] <%s> %s" % (user, msg))

        def noticed(self, user, channel, message):
            print("[IRC] [NOTICE] %s %s" % (user, message))

        def action(self, user, channel, msg):
            if channel == self.factory.channel:
                print("[GlobalChat] [IRC] * %s %s" % (user, replace_irc_with_pso2(msg).decode('utf-8')))
                for client in data.clients.connectedClients.values():
                    if client.preferences.get_preference('globalChat') and client.get_handle() is not None:
                        if gchatSettings['displayMode'] == 0:
                            client.get_handle().send_crypto_packet(
                                packetFactory.TeamChatPacket(self.get_user_id(user.split("!")[0]), "[GIRC] %s" % user.split("!")[0], "* %s%s" % (gchatSettings['prefix'], replace_irc_with_pso2(msg).decode('utf-8'))).build())
                        else:
                            client.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[GIRC] <%s> * %s" % (user.split("!")[0], "%s%s" % (gchatSettings['prefix'], replace_irc_with_pso2(msg).decode('utf-8'))), 0x3).build())

        def send_global_message(self, ship, user, message):
            self.msg(self.factory.channel, "[G-%02i] <%s> %s" % (ship, user, replace_pso2_with_irc(message)))

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
        if client_preferences.get_preference('globalChat'):
            user.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Proxy] {red}Global chat is enabled, use %sg <Message> to chat and %sgoff to disable it." % (config.globalConfig.get_key('commandPrefix'), config.globalConfig.get_key('commandPrefix')),
                0x3).build())
        else:
            user.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Proxy] {red}Global chat is disabled, use %sgon to enable it and use %sg <Message> to chat." % (config.globalConfig.get_key('commandPrefix'), config.globalConfig.get_key('commandPrefix')),
                0x3).build())


@plugins.CommandHook("irc")
class IRCCommand(Command):
    def call_from_console(self):
        global ircMode
        global ircBot
        if ircMode and ircBot is not None:
            ircBot.sendLine(self.args.split(" ", 1)[1])
            return "[IRC] >>> %s" % self.args.split(" ", 1)[1]


@plugins.CommandHook("gon", "Enable global chat.")
class EnableGChat(Command):
    def call_from_client(self, client):
        preferences = data.clients.connectedClients[client.playerId].preferences
        preferences.set_preference("globalChat", True)
        client.send_crypto_packet(
            packetFactory.SystemMessagePacket("[GlobalChat] Global chat enabled for you.", 0x3).build())


@plugins.CommandHook("goff", "Disable global chat.")
class DisableGChat(Command):
    def call_from_client(self, client):
        preferences = data.clients.connectedClients[client.playerId].preferences
        preferences.set_preference("globalChat", False)
        client.send_crypto_packet(
            packetFactory.SystemMessagePacket("[GlobalChat] Global chat disabled for you.", 0x3).build())


@plugins.CommandHook("gmute", "Mutes or somebody in gchat. Admin Only!", True)
class MuteSomebody(Command):
    def call_from_client(self, client):
        """
        :param client: ShipProxy.ShipProxy
        """
        if len(self.args.split(" ", 1)) < 2:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. gmute <Player Name>").build())
            return
        user_to_mute = self.args.split(" ", 1)[1]
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = True
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {grn}Muted %s." % player_data[0].rstrip("\0"), 0x3).build())
                else:
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0"), 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ", 1)) < 2:
            return "[Command] Invalid usage. gmute <Player Name>"
        user_to_mute = self.args.split(" ", 1)[1]
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = True
                    return "[Command] Muted %s." % player_data[0].rstrip("\0")
                else:
                    return "[Command] %s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0")


@plugins.CommandHook("gunmute", "Mutes or unmutes somebody in gchat. Admin Only!", True)
class UnmuteSomebody(Command):
    def call_from_client(self, client):
        """
        :param client: ShipProxy.ShipProxy
        """
        if len(self.args.split(" ", 1)) < 2:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. gmute <Player Name>").build())
            return
        user_to_mute = self.args.split(" ", 1)[1]
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = False
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {grn}Unmuted %s." % player_data[0].rstrip("\0"), 0x3).build())
                else:
                    client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0"), 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ", 1)) < 2:
            return "[Command] Invalid usage. gmute <Player Name>"
        user_to_mute = self.args.split(" ", 1)[1]
        for player_id, player_data in data.players.playerList.iteritems():
            if player_data[0].rstrip("\0") == user_to_mute:
                if player_id in data.clients.connectedClients:
                    data.clients.connectedClients[player_id].preferences['chatMuted'] = False
                    return "[Command] Unuted %s." % player_data[0].rstrip("\0")
                else:
                    return "[Command] %s either is not connected or is not part of the proxy." % player_data[0].rstrip("\0")



@plugins.CommandHook("g", "Chat in global chat.")
class GChat(Command):
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
        if ircMode:
            global ircBot
            if ircBot is not None:
                ircBot.send_global_message(data.clients.connectedClients[client.playerId].ship,
                    data.players.playerList[client.playerId][0].encode('utf-8'), self.args[3:].encode('utf-8'))
        for client_data in data.clients.connectedClients.values():
            if client_data.preferences.get_preference('globalChat') and client_data.get_handle() is not None:
                if gchatSettings['displayMode'] == 0:
                    client_data.get_handle().send_crypto_packet(packetFactory.TeamChatPacket(client.playerId, "[G-%02i] %s" % (data.clients.connectedClients[client.playerId].ship, data.players.playerList[client.playerId][0]), "%s%s" % (gchatSettings['prefix'], self.args[3:])).build())
                else:
                    client_data.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[G-%02i] <%s> %s" % (data.clients.connectedClients[client.playerId].ship, data.players.playerList[client.playerId][0], "%s%s" % (gchatSettings['prefix'], self.args[3:])), 0x3).build())

    def call_from_console(self):
        global ircMode
        if ircMode:
            global ircBot
            if ircBot is not None:
                ircBot.send_global_message(0, "Console", self.args[:2].encode('utf-8'))
        for client in data.clients.connectedClients.values():
            if client.preferences.get_preference("globalChat") and client.get_handle() is not None:
                if gchatSettings['displayMode'] == 0:
                    client.get_handle().send_crypto_packet(
                        packetFactory.TeamChatPacket(0x999, "[GCONSOLE]", self.args[2:]).build())
                else:
                    client.get_handle().send_crypto_packet(packetFactory.SystemMessagePacket("[GCONSOLE] %s%s" % (gchatSettings['prefix'], self.args[2:]), 0x3).build())
        return "[GlobalChat] <Console> %s" % self.args[2:]

