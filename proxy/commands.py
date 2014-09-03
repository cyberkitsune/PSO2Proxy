import cProfile
import calendar
import glob
import pstats
import datetime
import shutil
import sys

from ShipProxy import ShipProxy
from twisted.protocols import basic
from twisted.internet import reactor

import plugins.plugins as plugin_manager
import packetFactory
import config
import data.clients
import data.players
import data.blocks

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
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket("[Command] {red}That command cannot be run in-game.", 0x3).build())

    def call_from_console(self):
        return "[Command] That command can only be run in-game."

@CommandHandler("op", "[Admin Only] Makes a player an admin.", True)
class OpCommand(Command):
    def call_from_client(self, client):
        if len(self.args.split(" ")) < 2:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}op <SegaID>)", 0x3).build())
            return
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.append(player)
            config.globalConfig.set_key('admins', current_admins)
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Client] {gre}%s is now an admin." % player, 0x3).build())
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Client] {red}%s is already an admin." % player, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ")) < 2:
            return "[Command] Invalid usage. \n(Usage: op <SegaID>)"
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.append(player)
            config.globalConfig.set_key('admins', current_admins)
            return "[Command] %s is now an admin." % player
        else:
            return "[Command] %s is already an admin." % player

@CommandHandler("deop", "[Admin Only] Removes a player from admin.", True)
class DeopCommand(Command):
    def call_from_client(self, client):
        if len(self.args.split(" ")) < 2:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}deop <SegaID>)", 0x3).build())
            return
        player = self.args.split(" ")[1]
        if config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.remove(player)
            config.globalConfig.set_key('admins', current_admins)
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Client] {gre}%s is no-longer an admin." % player, 0x3).build())
        else:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Client] {red}%s is not an admin." % player, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ")) < 2:
            return "[Command] Invalid usage. \n(Usage: deop <SegaID>"
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.remove(player)
            config.globalConfig.set_key('admins', current_admins)
            return "[Command] %s is no longer an admin!" % player
        else:
            return "[Command] %s is not an admin." % player

@CommandHandler("help", "Prints a list of proxy commands.")
class HelpCommand(Command):
    def call_from_client(self, client):
        string = "=== PSO2Proxy Commands ===\n"
        user_command_count = 0
        for command, cData in commandList.iteritems():
            if cData[1] is not None:
                user_command_count += 1
                string += "%s%s - %s\n\n" % (config.globalConfig.get_key('commandPrefix'), command, cData[1])
        for command, cData in plugin_manager.commands.iteritems():
            if cData[1] is not None:
                user_command_count += 1
                string += "%s%s - %s\n\n" % (config.globalConfig.get_key('commandPrefix'), command, cData[1])
        string += "=== %i commands in total. ===" % user_command_count
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        return "=== PSO2Proxy Commands ===\n -- %s\n -- %s\n=== PSO2Proxy Commands ===" % ('\n -- '.join(commandList.keys()), '\n -- '.join(plugin_manager.commands.keys()))
        
@CommandHandler("maxplayers", "Prints the value of max connections allowed to the proxy.")
class HelpCommand(Command):
    def call_from_client(self, client):
	if config.globalConfig.get_key('maxConnections') == 0:
	  string = "[Command] This server does not limit the maximum number of connections."
	  client.send_crypto_packet(
	    packetFactory.SystemMessagePacket(string, 0x3).build())
	else:
	  string = "[Command] This server allows a maximum of %s client(s) to connect." % (config.globalConfig.get_key('maxConnections'))
	  client.send_crypto_packet(
	    packetFactory.SystemMessagePacket(string, 0x3).build())

    def call_from_console(self):
	if config.globalConfig.get_key('maxConnections') == 0:
	  return "[Command] This server does not limit the maximum number of connections."
	else:
	  return "[Command] This server allows a maximum of %s client(s) to connect." % (config.globalConfig.get_key('maxConnections'))

@CommandHandler("count", "Prints number of connected clients.")
class CountCommand(Command):
    def call_from_client(self, client):
        string = '[Comamnd] There are %s user(s) currently connected to the proxy.\nUse {command_prefix}maxplayers to check how many slots are available on this server.' % len(data.clients.connectedClients)
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket(string, 0x3).build())

    def call_from_console(self):
        return "[Comamnd] There are %s user(s) currently connected to the proxy.\nUse {command_prefix}maxplayers to check how many slots are available on this server." % len(data.clients.connectedClients)

@CommandHandler("reloadbans")
class ReloadBans(Command):
    def call_from_console(self):
        config.load_bans()

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
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        output = ""
        for ban in config.banList:
            output += '[Command] %s is banned.\n' % str(ban)
        output += '[Command] %i bans total.' % len(config.banList)
        return output

@CommandHandler("ban", "[Admin Only] Bans a player from the proxy.", True)
class Ban(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 3:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}ban <SegaID/PlayerID> <value>)", 0x3).build())
            return
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                client.send_crypto_packet(
		  packetFactory.SystemMessagePacket("[Client] {red}%s is already banned." % args[2], 0x3).build())
                return
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Client] {gre}%s has been banned." % args[2], 0x3).build())
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                client.send_crypto_packet(
		  packetFactory.SystemMessagePacket('[Client] {red} %s is already banned!' % args[2], 0x3).build())
                return
            config.banList.append({'playerId': args[2]})
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Client] %s has been banned." % args[2], 0x3).build())
            config.save_bans()
        else:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}ban <SegaID/PlayerID> <value>)", 0x3).build())
            return

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 3:
            return "[Command] Invalid usage. \n(Usage: ban <SegaID/PlayerID> <value>)"
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
            return "[Command] Invalid usage. \n(Usage: ban <SegaID/PlayerID> <value>)"

@CommandHandler("unban", "[Admin Only] Unbans a player from the proxy.", True)
class Unban(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 3:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}unban <SegaID/PlayerID> <value>)", 0x3).build())
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
            if not config.is_player_id_banned(args[2]):
                client.send_crypto_packet(
		  packetFactory.SystemMessagePacket('[Command] {red}%s is not banned.' % args[2], 0x3).build())
                return
            config.banList.remove({'playerId': args[2]})
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {gre}%s has been unbanned." % args[2], 0x3).build())
            config.save_bans()
        else:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}unban <SegaID/PlayerID> <value>)", 0x3).build())
            return

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 3:
            return "[Command] Invalid usage. \n(Usage: unban <SegaID/PlayerID> <value>)"
        if args[1] == "segaid":
            if not config.is_segaid_banned(args[2]):
                return "[Command] %s is not banned." % args[2]
            config.banList.remove({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if not config.is_player_id_banned(args[2]):
                return '[Command] %s is not banned.' % args[2]
            config.banList.remove({'playerId': args[2]})
            config.save_bans()
        else:
            return "[Command] Invalid usage. \n(Usage: unban <SegaID/PlayerID> <value>)"

@CommandHandler("kick", "[Admin Only] Disconnects a player from the proxy.", True)
class Kick(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 2:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}kick <PlayerID>)", 0x3).build())
            return
        if args[1].isdigit():
            if args[1] in data.clients.connectedClients:
                if data.clients.connectedClients[int(args[1])].get_handle() is not None:
                    data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
		      packetFactory.SystemMessagePacket("[Proxy] You have been disconnected from the proxy by an admin.", 0x2).build())
                    data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
                    client.send_crypto_packet(
		      packetFactory.SystemMessagePacket("[Command] {gre}Disconnected %s." % args[1], 0x3).build())
                else:
                    return "[Command] {red}Could not find client %s." % args[1]
            else:
        	    client.send_crypto_packet(
		      packetFactory.SystemMessagePacket("[Command] {red}Could not find client %s." % args[1], 0x3).build())
        else:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Argument must be a number.", 0x3).build())

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 2:
            return "[Command] Invalid usage. \n(Usage: kick <PlayerID>)"
        if args[1].isdigit():
            if args[1] in data.clients.connectedClients:
                if data.clients.connectedClients[int(args[1])].get_handle() is not None:
                    data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
		      packetFactory.SystemMessagePacket("[Proxy] You have been disconnected from the proxy by an admin.", 0x1).build())
                    data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
                    return "[Command] Disconnected %s." % args[1]
                else:
                    return "[Command] Could not find client %s." % args[1]
            else:
                return "[Command] Could not find client %s." % args[1]
    	else:
    	   return "[Command] Argument must be a number."

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
        pclient.send_crypto_packet(
	  packetFactory.SystemMessagePacket(string, 0x2).build())

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
            string += "[%s]\n - IP: %s \n - SEGA ID: %s \n - Player ID: %s \n - Ship: %s \n - Block: %s \n \n" % (client_player_name, client_host, client_segaid, client_player_id, client_ship, client_block)
        return string

@CommandHandler("globalmsg", "[Admin Only] Sends a global message to all clients on the proxy.", True)
class GlobalMessage(Command):
    def call_from_client(self, client):
        message = None
        print(self.args)
        if len(self.args.split(' ', 1)) < 2:
            client.send_crypto_packet(
	      packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. \n(Usage: {command_prefix}globalmsg  <message>)", 0x3).build())
            return
        message = self.args.split(' ', 1)[1]
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
		  packetFactory.SystemMessagePacket("[Proxy Global Message] %s" % message, 0x0).build())

    def call_from_console(self):
        message = None
        if len(self.args.split(' ', 1)) < 2:
            return "[Command] Invalid usage. \n(Usage: globalmsg <message>)"
        try:
            mode = int(self.args.split(' ', 2)[1])
        except ValueError:
            mode = 0x0
            message = self.args.split(' ', 1)[1]
        if message is None:
            message = self.args.split(' ', 2)[2]
        SMPacket = packetFactory.SystemMessagePacket("[Proxy Global Message] %s" % message, mode).build();
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(SMPacket)
        return "[Command] Sent global message."

@CommandHandler("exit")
class Exit(Command):
    def call_from_console(self):
        reactor.callFromThread(reactor.stop)
        return "[Proxy] Stopping proxy server..."

@CommandHandler("reloadblocknames")
class ReloadBlockNames(Command):
    def call_from_console(self):
        config.load_block_names()
        return

profile = None
@CommandHandler("profile")
class Profiler(Command):
    def call_from_console(self):
        global profile
        if profile is None:
            profile = cProfile.Profile()
            profile.enable()
            SMPacket = packetFactory.SystemMessagePacket("[Proxy Global Message] Profiling mode has been enabled, expect lag while this runs.", 0x0).build()
            for client in data.clients.connectedClients.values():
                if client.get_handle() is not None:
                    client.get_handle().send_crypto_packet(SMPacket)
            return "[Command] Profiling has been enabled."
        else:
            profile.disable()
            out = open("profile_%s.txt" % calendar.timegm(datetime.datetime.utcnow().utctimetuple()), 'w')
            sort_by = 'cumulative'
            ps = pstats.Stats(profile, stream=out).sort_stats(sort_by)
            ps.print_stats()
            shutil.copy(out.name, "latest_profile.txt")
            out.close()
            profile = None
            SMPacket = packetFactory.SystemMessagePacket("[Proxy Global Message] Profiling mode has been disabled, any lag caused by this should subside.", 0x0).build()
            for client in data.clients.connectedClients.values():
                if client.get_handle() is not None:
                    client.get_handle().send_crypto_packet(SMPacket)
            return "[Profiling] Profiling has been disabled, results written to disk."

@CommandHandler("reloadplugin")
class ReloadPlugins(Command):
    def call_from_console(self):
        if len(self.args.split(' ')) < 2:
            return "[Command] Invalid usage. \n(Usage: reloadplugin <Plugin Name>)"
        if self.args[1] not in sys.modules:
            return "That plugin is not loaded."
        output = "[Command] Reloading plugin: %s..." % self.args[1]
        reload(sys.modules[self.args[1]])
        output += "[Command] Plugin reloaded!\n"
        return output