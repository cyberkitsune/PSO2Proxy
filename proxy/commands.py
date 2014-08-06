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
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}This command can not be run from the console.", 0x3).build())

    def call_from_console(self):
        return "[Command] This command can not be run from here."


@CommandHandler("op", "Makes a player an admin. Admins Only.", True)
class OpCommand(Command):
    def call_from_client(self, client):
        if len(self.args.split(" ")) < 2:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}Not enough arguments. Usage: |op <segaid>",
                                                  0x3).build())
            return
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.append(player)
            config.globalConfig.set_key('admins', current_admins)
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {gre}%s added to admins successfully." % player,
                                                  0x3).build())
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}%s is already an admin!" % player, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ")) < 2:
            return "[ShipProxy] Not enough arguments. Usage: >>> op <segaid>"
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.append(player)
            config.globalConfig.set_key('admins', current_admins)
            return "[ShipProxy] %s is now an admin!" % player
        else:
            return "[ShipProxy] %s is already an admin!" % player


@CommandHandler("deop", "Removes a player from the admin list. Admins Only.", True)
class DeopCommand(Command):
    def call_from_client(self, client):
        if len(self.args.split(" ")) < 2:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}Not enough arguments. Usage: |deop <segaid>",
                                                  0x3).build())
            return
        player = self.args.split(" ")[1]
        if config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.remove(player)
            config.globalConfig.set_key('admins', current_admins)
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {gre}%s removed from admins successfully." % player,
                                                  0x3).build())
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}%s is not an admin!" % player, 0x3).build())

    def call_from_console(self):
        if len(self.args.split(" ")) < 2:
            return "[ShipProxy] Not enough arguments. Usage: >>> deop <segaid>"
        player = self.args.split(" ")[1]
        if not config.is_admin(player):
            current_admins = config.globalConfig.get_key('admins')
            current_admins.remove(player)
            config.globalConfig.set_key('admins', current_admins)
            return "[ShipProxy] %s is no longer an admin!" % player
        else:
            return "[ShipProxy] %s is not an admin!" % player


@CommandHandler("help", "Displays this help page.")
class HelpCommand(Command):
    def call_from_client(self, client):
        string = "=== PSO2Proxy Client Commands ===\n"
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
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        return "[Command] Hello Console! Valid commands: %s%s\n" % (', '.join(commandList.keys()), ', '.join(plugin_manager.commands.keys()))


@CommandHandler("count", "Returns the current player count in system chat.")
class CountCommand(Command):
    def call_from_client(self, client):
        string = '[Command] There are %s users currently connected to your proxy.' % len(data.clients.connectedClients)
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x3).build())

    def call_from_console(self):
        return "[ShipProxy] There are %s users currently on the proxy." % len(data.clients.connectedClients)


@CommandHandler("reloadbans")
class ReloadBans(Command):
    def call_from_console(self):
        config.load_bans()


@CommandHandler("listbans", "Prints the ban list. Admins only.", True)
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


@CommandHandler("ban", "Bans somebody from the proxy. Admins only.", True)
class Ban(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 3:
            client.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |ban <segaid/pid> <value>", 0x3).build())
            return
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command]{red} %s is already banned!" % args[2], 0x3).build())
                return
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been banned." % args[2], 0x3).build())
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket('[Command]{red} %s is already banned!' % args[2], 0x3).build())
                return
            config.banList.append({'playerId': args[2]})
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been banned." % args[2], 0x3).build())
            config.save_bans()
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |ban <segaid/pid> <value>", 0x3).build())
            return

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 3:
            return "[Command] Invalid usage! Proper usage, >>> ban <segaid/pid> <value>"
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                return "[Command] %s is already banned!" % args[2]
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                return '[Command] %s is already banned!' % args[2]
            config.banList.append({'playerId': args[2]})
            config.save_bans()
        else:
            return "[Command] Invalid usage! Proper usage, >>> ban <segaid/pid> <value>"


@CommandHandler("unban", "Unbans somebody from the proxy. Admins only.", True)
class Unban(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 3:
            client.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |unban <segaid/pid> <value>", 0x3).build())
            return
        if args[1] == "segaid":
            if not config.is_segaid_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command]{red} %s is not banned!" % args[2], 0x3).build())
                return
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been unbanned." % args[2], 0x3).build())
            config.banList.remove({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if not config.is_player_id_banned(args[2]):
                client.send_crypto_packet(
                    packetFactory.SystemMessagePacket('[Command]{red} %s is not banned!' % args[2], 0x3).build())
                return
            config.banList.remove({'playerId': args[2]})
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been unbanned." % args[2], 0x3).build())
            config.save_bans()
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |unban <segaid/pid> <value>", 0x3).build())
            return

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 3:
            return "[Command] Invalid usage! Proper usage, >>> unban <segaid/pid> <value>"
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
            return "[Command] Invalid usage! Proper usage, >>> unban <segaid/pid> <value>"


@CommandHandler("kick", "Kicks a client from the proxy. Admins only.", True)
class Kick(Command):
    def call_from_client(self, client):
        args = self.args.split(' ')
        if len(args) < 2:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {red}Invalid usage! Proper usage: |kick <playerId>",
                                                  0x3).build())
            return
        if int(args[1]) in data.clients.connectedClients:
            data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
                packetFactory.SystemMessagePacket("You have been kicked from the proxy by %s." % client.myUsername,
                                                  0x2).build())
            data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {grn}Kicked %s." % args[1], 0x3).build())
        else:
            client.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {red}I couldn't find %s!" % args[1], 0x3).build())

    def call_from_console(self):
        args = self.args.split(' ')
        if len(args) < 2:
            return "[Command] Invalid usage! Proper usage: >>> kick <playerId>"
        if int(args[1]) in data.clients.connectedClients:
            data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
                packetFactory.SystemMessagePacket("You have been kicked from the proxy from the console.", 0x1).build())
            data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
            return "[Command] Kicked %s." % args[1]
        else:
            return "[Command] I couldn't find %s!" % args[1]


@CommandHandler("clients", "Lists all clients, SEGA IDs, and IP Addresses connected to the proxy. Admins only.", True)
class ListClients(Command):
    def call_from_client(self, client):
        string = "[ClientList] === Connected Clients (%i total) ===\n" % len(data.clients.connectedClients)
        for ip, client in data.clients.connectedClients.iteritems():
            client_handle = client.get_handle()
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
            block_number = client_handle.transport.getHost().port
            if block_number in data.blocks.blockList:
                client_block = data.blocks.blockList[block_number][1].rstrip('\0')
            else:
                client_block = None
            string += "[ClientList] IP: %s SEGA ID: %s Player ID: %s Player Name: %s Block: %s\n" % (
                client_host, client_segaid, client_player_id, client_player_name, client_block)
        client.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())

    def call_from_console(self):
        string = "[ClientList] === Connected Clients (%i total) ===\n" % len(data.clients.connectedClients)
        for ip, client in data.clients.connectedClients.iteritems():
            client_handle = client.get_handle()
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
            block_number = client_handle.transport.getHost().port
            if block_number in data.blocks.blockList:
                client_block = data.blocks.blockList[block_number][1].rstrip('\0')
            else:
                client_block = None
            string += "[ClientList] IP: %s SEGA ID: %s Player ID: %s Player Name: %s Block: %s\n" % (
                client_host, client_segaid, client_player_id, client_player_name, client_block)
        return string


@CommandHandler("globalmsg", "Sends a global message to everyone on the server. Admins only.", True)
class GlobalMessage(Command):
    def call_from_client(self, client):
        message = None
        if len(self.args.split(' ', 1)) < 2:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[ShipProxy] {red}Incorrect usage. Usage: |globalmsg  <message_type> <Message>", 0x3).build())
            return

        try:
            mode = int(client.split(' ', 2)[1])
        except ValueError:
            mode = 0x0
            message = self.args.split(' ', 1)[1]

        if message is not None:
            message = client.split(' ', 2)[2]
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Proxy Global Message] %s" % message, mode).build())

    def call_from_console(self):
        if len(self.args.split(' ', 2)) < 3:
            return "[ShipProxy] Incorrect usage. Usage: >>> globalmsg  <message_type> <Message>"
        mode = int(self.args.split(' ', 2)[1])
        message = self.args.split(' ', 2)[2]
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Proxy Global Message] %s" % message, mode).build())
        return "[ShipProxy] Sent global message!"


@CommandHandler("exit")
class Exit(Command):
    def call_from_console(self):
        reactor.callFromThread(reactor.stop)
        return "[ShipProxy] Exiting..."

@CommandHandler("reloadblocknames")
class ReloadBlockNames(Command):
    def call_from_console(self):
        config.load_block_names()
        return