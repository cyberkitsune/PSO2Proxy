import calendar
import cProfile
import data.blocks
import data.clients
import data.players
import datetime
import pstats
import shutil
import sys
from twisted.internet import reactor
from twisted.python import rebuild

useFaulthandler = True

try:
    import faulthandler
except ImportError:
    useFaulthandler = False

import config
import packetFactory
import plugins.plugins as plugin_manager
from ShipProxy import ShipProxy


commandList = {}


class CommandHandler(object):
    def __init__(self, command_name, help_text=None, admin_conly=False):
        self.commandName = command_name
        self.help_text = help_text
        self.admin_only = admin_conly

    def __call__(self, command_class):
        global commandList
        commandList[self.commandName] = [command_class, self.help_text, self.admin_only]


class Command(object):
    def __init__(self, args=None):
        self.args = args

    def call_from_client(self, client):
        """
        :param client: ShipProxy.ShipProxy
        """
        client.send_crypto_packet
        (
            packetFactory.SystemMessagePacket
            (
                "[Command] {red}That command cannot be run in-game.",
                0x3
            ).build()
        )

    def call_from_console(self):
        return "[Command] That command can only be run in-game."


@CommandHandler("op", "[Admin Only] Makes a player an admin.", True)
class OpCommand(Command):
    def call_from_client(self, client):
        if len(self.args.split(" ")) < 2:
            client.send_crypto_packet
            (
                packetFactory.SystemMessagePacket
                (
                    "[Proxy] {red}Invalid usage.\n(Usage: %sop <SegaID>)".format(
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig['admins']
            current_admins.append(player)
            config.globalConfig.set_key('admins', current_admins)
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {gre}%s is now an admin." % player,
                                                  0x3).build())
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}%s is already an admin." % player, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ")) < 2:
            return "[ShipProxy] Invalid usage. (Usage: op <SegaID>)"
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig['admins']
            current_admins.append(player)
            config.globalConfig.set_key('admins', current_admins)
            return "[ShipProxy] %s is now an admin." % player
        else:
            return "[ShipProxy] %s is already an admin." % player


@CommandHandler("deop", "[Admin Only] Removes a player from admin.", True)
class DeopCommand(Command):
    def call_from_client(self, client):
        if len(self.args.split(" ")) < 2:
            client.send_crypto_packet
            (
                packetFactory.SystemMessagePacket
                (
                    "[Proxy] {}Invalid usage.\n(Usage: {}deop <SegaID>)".format(
                        "{red}",
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return
        player = self.args.split(" ")[1]
        if config.is_admin(player):
            current_admins = config.globalConfig['admins']
            current_admins.remove(player)
            config.globalConfig.set_key('admins', current_admins)
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {gre}%s is no longer an admin." % player,
                                                  0x3).build())
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}%s is not an admin." % player, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ")) < 2:
            return "[ShipProxy] Invalid usage. (Usage: deop <SegaID>"
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig['admins']
            current_admins.remove(player)
            config.globalConfig.set_key('admins', current_admins)
            return "[ShipProxy] %s is no longer an admin." % player
        else:
            return "[ShipProxy] %s is not an admin." % player


@CommandHandler("help", "Displays a list of commands.")
class HelpCommand(Command):
    def call_from_client(self, client):
        string = "=== PSO2Proxy Commands ===\n"
        user_command_count = 0
        for command, cData in sorted(commandList.iteritems()):
            if cData[1] is not None:
                if cData[2] is not None:
                    if not cData[2]:
                        user_command_count += 1
                        string += "%s%s - %s\n\n" % (config.globalConfig['commandPrefix'], command, cData[1])
                else:
                    user_command_count += 1
                    string += "%s%s - %s\n\n" % (config.globalConfig['commandPrefix'], command, cData[1])
        for command, cData in sorted(plugin_manager.commands.iteritems()):
            if cData[1] is not None:
                if cData[2] is not None:
                    if not cData[2]:
                        user_command_count += 1
                        string += "%s%s - %s\n\n" % (config.globalConfig['commandPrefix'], command, cData[1])
                else:
                    user_command_count += 1
                    string += "%s%s - %s\n\n" % (config.globalConfig['commandPrefix'], command, cData[1])
        string += "{}suhelp - [Admin Only] Display proxy administrator command list.\n\n".format
        (
            config.globalConfig['commandPrefix']
        )
        # i add this manually because don't know how to get specific command.
        string += "=== %i commands in total ===" % user_command_count
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        return "=== PSO2Proxy Commands ===\n -- {}\n -- {}\n=== PSO2Proxy Commands ===".format
        (
            '\n -- '.join(commandList.keys()),
            '\n -- '.join(plugin_manager.commands.keys())
        )


@CommandHandler("suhelp", "[Admin Only] Display proxy administrator command list.", True)
class HelpCommandADM(Command):
    def call_from_client(self, client):
        string = "=== PSO2Proxy Commands ===\n"
        user_command_count = 0
        for command, cData in sorted(commandList.iteritems()):
            if cData[1] is not None:
                if cData[2] is not None:
                    if cData[2]:
                        user_command_count += 1
                        string += "%s%s - %s\n\n" % (config.globalConfig['commandPrefix'], command, cData[1])
        for command, cData in sorted(plugin_manager.commands.iteritems()):
            if cData[1] is not None:
                if cData[2] is not None:
                    if cData[2]:
                        user_command_count += 1
                        string += "%s%s - %s\n\n" % (config.globalConfig['commandPrefix'], command, cData[1])
        string += "=== %i commands in total ===" % user_command_count
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())


@CommandHandler("count", "Prints number of connected clients.")
class CountCommand(Command):
    def call_from_client(self, client):
        string = '[Command] There are %s user(s) currently connected to the proxy.' % len(data.clients.connectedClients)
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x3).build())

    def call_from_console(self):
        return "[ShipProxy] There are %s user(s) currently connected to the proxy." % len(data.clients.connectedClients)


@CommandHandler("reloadbans")
class ReloadBans(Command):
    def call_from_console(self):
        return config.load_bans()


@CommandHandler("listbans", "[Admin Only] Prints a list of banned users.", True)
class ListBans(Command):
    def call_from_client(self, client):
        string = "=== Ban List ===\n"
        for ban in config.banList:
            if 'segaId' in ban:
                string += "SEGA ID: %s " % ban['segaId']
            if 'playerId' in ban:
                string += "Player ID: %s" % ban['playerId']
            string += "\n"
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        output = ""
        for ban in config.banList:
            output += '[Bans] %s is banned.\n' % str(ban)
        output += '[Bans] %i bans total.' % len(config.banList)
        return output


@CommandHandler("ban", "[Admin Only] Bans a player from the proxy.", True)
class Ban(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 3:
            client.send_crypto_packet
            (
                packetFactory.SystemMessagePacket
                (
                    "[Command] {}Invalid usage.\n(Usage: {}ban <SegaID/PlayerID> <value>)".format(
                        "{red}",
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command] {red}%s is already banned." % args[2], 0x3).build())
                return
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {gre}%s has been banned." % args[2], 0x3).build())
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket('[Command] {red}%s is already banned.' % args[2], 0x3).build())
                return
            config.banList.append({'playerId': args[2]})
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {gre}%s has been banned." % args[2], 0x3).build())
            config.save_bans()
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |ban <segaid/pid> <value>", 0x3).build())
            return

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 3:
            return "[Command] Invalid usage. (Usage: ban <SegaID/PlayerID> <value>)"
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                return "[Command] %s is already banned." % args[2]
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                return '[Command] %s is already banned.' % args[2]
            config.banList.append({'playerId': args[2]})
            config.save_bans()
        else:
            return "[Command] Invalid usage. (Usage: ban <SegaID/PlayerID> <value>)"


@CommandHandler("unban", "[Admin Only] Unbans a player from the proxy.", True)
class Unban(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 3:
            client.send_crypto_packet
            (
                packetFactory.SystemMessagePacket
                (
                    "[Command] {}Invalid usage.\n(Usage: {}unban <SegaID/PlayerID> <value>)".format(
                        "{red",
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return
        if args[1] == "segaid":
            if not config.is_segaid_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command] {red}%s is not banned." % args[2], 0x3).build())
                return
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {gre}%s has been unbanned." % args[2], 0x3).build())
            config.banList.remove({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if not config.is_player_id_banned(int(args[2])):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket('[Command]{red} %s is not banned.' % args[2], 0x3).build())
                return
            config.banList.remove({'playerId': unicode(args[2])})
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {gre}%s has been unbanned." % args[2], 0x3).build())
            config.save_bans()
        else:
            client.send_crypto_packet
            (
                packetFactory.SystemMessagePacket
                (
                    "[Command] {red}Invalid usage. \n(Usage: %sunban <SegaID/PlayerID> <value>)".foramt
                    (
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 3:
            return "[Command] Invalid usage. (Usage: unban <SegaID/PlayerID> <value>)"
        if args[1] == "segaid":
            if not config.is_segaid_banned(args[2]):
                return "[Command] %s is not banned!" % args[2]
            config.banList.remove({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if not config.is_player_id_banned(args[2]):
                return '[Command] %s is not banned!' % args[2]
            config.banList.remove({'playerId': args[2]})
            config.save_bans()
        else:
            return "[Command] Invalid usage. (Usage: unban <SegaID/PlayerID> <value>)"


@CommandHandler("kick", "[Admin Only] Disconnects a player from the proxy.", True)
class Kick(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 2:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket
                (
                    "[Command] {}Invalid usage.\n(Usage: {}kick <PlayerID>)".format
                    (
                        "{red}",
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return
        if not args[1].isdigit():
            return "[Command] {red}%s is not an number." % args[1]
        if int(args[1]) in data.clients.connectedClients:
            if data.clients.connectedClients[int(args[1])].get_handle() is not None:
                data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Proxy] {yel}You have been disconnected from the proxy by an admin.",
                                                      0x2).build())
                data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command] {gre}%s has been disconnected." % args[1], 0x3).build())
            else:
                return "[Command] {red}%s could not be found." % args[1]
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {red}%s could not be found." % args[1], 0x3).build())

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 2:
            return "[Command] Invalid usage. (Usage: kick <PlayerID>)"
        if not args[1].isdigit():
            return "[Command] {red}%s is not a number." % args[1]
        if int(args[1]) in data.clients.connectedClients:
            if data.clients.connectedClients[int(args[1])].get_handle() is not None:
                data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet
                (
                    packetFactory.SystemMessagePacket
                    (
                        "[Proxy] You have been disconnected from the proxy by an admin.",
                        0x1
                    ).build()
                )
                data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
                return "[Command] %s has been disconnected." % args[1]
            else:
                return "[Command] %s could not be found." % args[1]
        else:
            return "[Command] %s could not be found." % args[1]


@CommandHandler("clients", "[Admin Only] Prints a list of all connected clients.", True)
class ListClients(Command):
    def call_from_client(self, pclient):
        string = "=== Connected Clients: %i ===\n" % len(data.clients.connectedClients)
        for ip, client in data.clients.connectedClients.iteritems():
            client_handle = client.get_handle()
            if client_handle is None:
                continue
            client_host = client_handle.transport.getPeer().host
            client_segaid = client_handle.myUsername
            if client_segaid is None:
                continue
            client_segaid = client_segaid.rstrip('\0')
            client_player_id = client_handle.playerId
            if client_player_id in data.players.playerList:
                client_player_name = data.players.playerList[client_player_id][0].rstrip('\0')
            else:
                client_player_name = None
            client_ship = None
            client_block = None
            block_number = client_handle.transport.getHost().port
            if block_number in data.blocks.blockList:
                client_ship = data.clients.get_ship_from_port(block_number)
                client_block = data.blocks.blockList[block_number][1].rstrip('\0')
            string += "[%s]\n - IP: %s \n - SEGA ID: %s \n - Player ID: %s \n - Ship: %s \n - Block: %s \n \n" % (
                client_player_name, client_host, client_segaid, client_player_id, client_ship, client_block)
        pclient.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        string = "=== Connected Clients: %i ===\n" % len(data.clients.connectedClients)
        for ip, client in data.clients.connectedClients.iteritems():
            client_handle = client.get_handle()
            if client_handle is None:
                continue
            client_host = client_handle.transport.getPeer().host
            client_segaid = client_handle.myUsername
            if client_segaid is None:
                continue
            client_segaid = client_segaid.rstrip('\0')
            client_player_id = client_handle.playerId
            if client_player_id in data.players.playerList:
                client_player_name = data.players.playerList[client_player_id][0].rstrip('\0')
            else:
                client_player_name = None
            client_ship = None
            client_block = None
            if isinstance(client_handle, ShipProxy):
                block_number = client_handle.transport.getHost().port
                if block_number in data.blocks.blockList:
                    client_ship = data.clients.get_ship_from_port(block_number)
                    client_block = data.blocks.blockList[block_number][1].rstrip('\0')
            string += "[%s]\n - IP: %s \n - SEGA ID: %s \n - Player ID: %s \n - Ship: %s \n - Block: %s \n \n" % (
                client_player_name, client_host, client_segaid, client_player_id, client_ship, client_block)
        return string


@CommandHandler("globalmsg", "[Admin Only] Sends a global message to all clients on the proxy.", True)
class GlobalMessage(Command):
    def call_from_client(self, client):
        message = None
        print(self.args)
        if len(self.args.split(' ', 1)) < 2:
            client.send_crypto_packet
            (
                packetFactory.SystemMessagePacket
                (
                    "[Command] {}Invalid usage.\n(Usage: {}globalmsg  <message>)".format
                    (
                        "{red}",
                        config.globalConfig['commandPrefix']
                    ),
                    0x3
                ).build()
            )
            return
        message = self.args.split(' ', 1)[1]
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Proxy Global Message] %s" % message, 0x0).build())

    def call_from_console(self):
        message = None
        if len(self.args.split(' ', 1)) < 2:
            return "[Command] Invalid usage. (Usage: globalmsg <message>)"
        try:
            mode = int(self.args.split(' ', 2)[1])
        except ValueError:
            mode = 0x0
            message = self.args.split(' ', 1)[1]

        if message is None:
            message = self.args.split(' ', 2)[2]
        SMPacket = packetFactory.SystemMessagePacket("[Proxy Global Message] %s" % message, mode).build()
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(SMPacket)
        return "[Command] Sent global message!"


@CommandHandler("exit")
class Exit(Command):
    def call_from_console(self):
        reactor.callFromThread(reactor.stop)
        return "[ShipProxy] Stopping proxy server..."


@CommandHandler("reloadblocknames")
class ReloadBlockNames(Command):
    def call_from_console(self):
        return config.load_block_names()


@CommandHandler("reloadshiplabels")
class ReloadShipLables(Command):
    def call_from_console(self):
        return config.load_ship_names()


profile = None


@CommandHandler("profile", "[Admin Only] Turn on profiling mode", True)
class Profiler(Command):
    def call_from_console(self):
        global profile
        if profile is None:
            profile = cProfile.Profile()
            profile.enable()
            SMPacket = packetFactory.SystemMessagePacket
            (
                "[Proxy Notice] Profiling mode has been enabled, expect lag while this runs.",
                0x0
            ).build()
            for client in data.clients.connectedClients.values():
                if client.get_handle() is not None:
                    client.get_handle().send_crypto_packet(SMPacket)
            return "[Profiling] Profiling has been enabled."
        else:
            profile.disable()
            out = open("profile_%s.txt" % calendar.timegm(datetime.datetime.utcnow().utctimetuple()), 'w')
            sort_by = 'cumulative'
            ps = pstats.Stats(profile, stream=out).sort_stats(sort_by)
            ps.print_stats()
            shutil.copy(out.name, "latest_profile.txt")
            out.close()
            profile = None
            SMPacket = packetFactory.SystemMessagePacket
            (
                "[Proxy Notice] Profiling mode has been disabled, any lag caused by this should subside.",
                0x0
            ).build()
            for client in data.clients.connectedClients.values():
                if client.get_handle() is not None:
                    client.get_handle().send_crypto_packet(SMPacket)
            return "[Profiling] Profiling has been disabled, results written to disk."


@CommandHandler("reloadplugin", "[Admin Only] Reload one plugin", True)
class ReloadPlugins(Command):
    def call_from_console(self):
        if len(self.args.split(' ')) < 2:
            return "[Command] Invalid usage. (Usage: reloadplugin <Plugin Name>)"
        modulearg = self.args.split(' ')[1]
        if modulearg not in sys.modules.keys():
            return "That plugin (%s) is not loaded." % modulearg
        output = "[ShipProxy] Reloading plugin: %s..." % modulearg
        rebuild.rebuild(sys.modules[modulearg])
        output += "[ShipProxy] Plugin reloaded!\n"
        return output


if useFaulthandler:
    @CommandHandler("dumptraceback", "[Admin Only] Dump stacktrack of Proxy", True)
    class Fault(Command):
        def call_from_console(self):
            faulthandler.dump_traceback(file=open('log/tracestack.log', 'w+'), all_threads=True)
            return "[Trackback] dumpped state of Proxy"
