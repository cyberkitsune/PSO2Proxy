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

    def __call__(self, f):
        global commandList
        commandList[self.commandName] = [f, self.help_text, self.admin_only]


@CommandHandler("op", "Makes a player an admin. Admins Only.", True)
def op_player(sender, params):
    if not isinstance(sender, basic.LineReceiver):
        if len(params.split(" ")) < 2:
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}Not enough arguments. Usage: |op <segaid>",
                                                  0x3).build())
            return
        player = params.split(" ")[1]
        if not config.is_admin(player):
            config.globalConfig.set_key('admins', (config.globalConfig.get_key('admins')).append(player))
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {gre}%s added to admins successfully." % player,
                                                  0x3).build())
        else:
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}%s is already an admin!" % player, 0x3).build())
    else:
        if len(params.split(" ")) < 2:
            print("[ShipProxy] Not enough arguments. Usage: >>> op <segaid>")
            return
        player = params.split(" ")[1]
        if not config.is_admin(player):
            config.globalConfig.set_key('admins', (config.globalConfig.get_key('admins')).append(player))
            print("[ShipProxy] %s is now an admin!" % player)
        else:
            print("[ShipProxy] %s is already an admin!" % player)


@CommandHandler("deop", "Removes a player from the admin list. Admins Only.", True)
def op_player(sender, params):
    if not isinstance(sender, basic.LineReceiver):
        if len(params.split(" ")) < 2:
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}Not enough arguments. Usage: |deop <segaid>",
                                                  0x3).build())
            return
        player = params.split(" ")[1]
        if config.is_admin(player):
            config.globalConfig.set_key('admins', (config.globalConfig.get_key('admins')).remove(player))
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {gre}%s has been removed from admins successfully." % player,
                                                  0x3).build())
        else:
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Proxy] {red}%s is not an admin!" % player, 0x3).build())
    else:
        if len(params.split(" ")) < 2:
            print("[ShipProxy] Not enough arguments. Usage: >>> deop <segaid>")
            return
        player = params.split(" ")[1]
        if config.is_admin(player):
            config.globalConfig.set_key('admins', (config.globalConfig.get_key('admins')).remove(player))
            print("[ShipProxy] %s hes been removed from admins successfully!" % player)
        else:
            print("[ShipProxy] %s is not an admin!" % player)


@CommandHandler("help", "Displays this help page.")
def help_command(sender, params):
    if not isinstance(sender, basic.LineReceiver):
        string = "=== PSO2Proxy Client Commands ===\n"
        user_command_count = 0
        for command, cData in commandList.iteritems():
            if cData[1] is not None:
                user_command_count += 1
                string += "|%s - %s\n\n" % (command, cData[1])
        for command, cData in plugin_manager.commands.iteritems():
            if cData[1] is not None:
                user_command_count += 1
                string += "|%s - %s\n\n" % (command, cData[1])
        string += "=== %i commands in total. ===" % user_command_count
        sender.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())
    else:
        sender.transport.write("[Command] Hello Console! Valid commands: %s\n" % ', '.join(commandList.keys()))


@CommandHandler("count", "Returns the current player count in system chat.")
def count(sender, params):
    if not isinstance(sender, basic.LineReceiver):
        string = '[Command] There are %s users currently connected to your proxy.' % len(data.clients.connectedClients)
        sender.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x3).build())
    else:
        print("[ShipProxy] There are %s users currently on the proxy." % len(data.clients.connectedClients))


@CommandHandler("reloadbans")
def reload_bans(sender, params):
    if isinstance(sender, basic.LineReceiver):
        config.load_bans()


@CommandHandler("listbans", "Prints the ban list. Admins only.", True)
def list_bans(sender, params):
    if isinstance(sender, basic.LineReceiver):
        for ban in config.banList:
            print('[Bans] %s is banned.' % str(ban))
        print('[Bans] %i bans total.' % len(config.banList))
    else:
        string = "=== Ban List ===\n"
        for ban in config.banList:
            if 'segaId' in ban:
                string += "SEGA ID: %s " % ban['segaId']
            if 'playerId' in ban:
                string += "Player ID: %s" % ban['playerId']
            string += "\n"
        sender.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())


@CommandHandler("ban", "Bans somebody from the proxy. Admins only.", True)
def ban(sender, params):
    if isinstance(sender, basic.LineReceiver):
        args = params.split(' ')
        if len(args) < 3:
            print("[Command] Invalid usage! Proper usage, >>> ban <segaid/pid> <value>")
            return
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                print("[Command] %s is already banned!" % args[2])
                return
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                print('[Command] %s is already banned!' % args[2])
                return
            config.banList.append({'playerId': args[2]})
            config.save_bans()
        else:
            print("[Command] Invalid usage! Proper usage, >>> ban <segaid/pid> <value>")
            return
    else:
        args = params.split(' ')
        if len(args) < 3:
            sender.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |ban <segaid/pid> <value>", 0x3).build())
            return
        if args[1] == "segaid":
            if config.is_segaid_banned(args[2]):
                sender.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command]{red} %s is already banned!" % args[2], 0x3).build())
                return
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been banned." % args[2], 0x3).build())
            config.banList.append({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if config.is_player_id_banned(args[2]):
                sender.send_crypto_packet(
                    packetFactory.SystemMessagePacket('[Command]{red} %s is already banned!' % args[2], 0x3).build())
                return
            config.banList.append({'playerId': args[2]})
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been banned." % args[2], 0x3).build())
            config.save_bans()
        else:
            sender.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |ban <segaid/pid> <value>", 0x3).build())
            return


@CommandHandler("unban", "Unbans somebody from the proxy. Admins only.", True)
def ban(sender, params):
    if isinstance(sender, basic.LineReceiver):
        args = params.split(' ')
        if len(args) < 3:
            print("[Command] Invalid usage! Proper usage, >>> unban <segaid/pid> <value>")
            return
        if args[1] == "segaid":
            if not config.is_segaid_banned(args[2]):
                print("[Command] %s is not banned!" % args[2])
                return
            config.banList.remove({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if not config.is_player_id_banned(args[2]):
                print('[Command] %s is not banned!' % args[2])
                return
            config.banList.remove({'playerId': args[2]})
            config.save_bans()
        else:
            print("[Command] Invalid usage! Proper usage, >>> unban <segaid/pid> <value>")
            return
    else:
        args = params.split(' ')
        if len(args) < 3:
            sender.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |unban <segaid/pid> <value>", 0x3).build())
            return
        if args[1] == "segaid":
            if not config.is_segaid_banned(args[2]):
                sender.send_crypto_packet(
                    packetFactory.SystemMessagePacket("[Command]{red} %s is not banned!" % args[2], 0x3).build())
                return
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been unbanned." % args[2], 0x3).build())
            config.banList.remove({'segaId': args[2]})
            config.save_bans()
        elif args[1] == "pid":
            if not config.is_player_id_banned(args[2]):
                sender.send_crypto_packet(
                    packetFactory.SystemMessagePacket('[Command]{red} %s is not banned!' % args[2], 0x3).build())
                return
            config.banList.remove({'playerId': args[2]})
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] %s has been unbanned." % args[2], 0x3).build())
            config.save_bans()
        else:
            sender.send_crypto_packet(packetFactory.SystemMessagePacket(
                "[Command] {red}Invalid usage! Proper usage, |unban <segaid/pid> <value>", 0x3).build())
            return

@CommandHandler("kick", "Kicks a client from the proxy. Admins only.", True)
def kick(sender, params):
    if isinstance(sender, basic.LineReceiver):
        args = params.split(' ')
        if len(args) < 2:
            print("[Command] Invalid usage! Proper usage: >>> kick <playerId>")
            return
        if int(args[1]) in data.clients.connectedClients:
            data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
                packetFactory.SystemMessagePacket("You have been kicked from the proxy from the console.", 0x2).build())
            data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
            print("[Command] Kicked %s." % args[1])
        else:
            print("[Command] I couldn't find %s!" % args[1])
    else:
        args = params.split(' ')
        if len(args) < 2:
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {red}Invalid usage! Proper usage: |kick <playerId>",
                                                  0x3).build())
            return
        if int(args[1]) in data.clients.connectedClients:
            data.clients.connectedClients[int(args[1])].get_handle().send_crypto_packet(
                packetFactory.SystemMessagePacket("You have been kicked from the proxy by %s." % sender.myUsername,
                                                  0x2).build())
            data.clients.connectedClients[int(args[1])].get_handle().transport.loseConnection()
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {grn}Kicked %s." % args[1], 0x3).build())
        else:
            sender.send_crypto_packet(
                packetFactory.SystemMessagePacket("[Command] {red}I couldn't find %s!" % args[1], 0x3).build())


@CommandHandler("clients",
                "Lists all clients, SEGA IDs, and IP Addresses connected to the proxy. Admins only.", True)
def list_clients(sender, params):
    if isinstance(sender, basic.LineReceiver):
        print("[ClientList] === Connected Clients (%i total) ===" % len(data.clients.connectedClients))
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
            print("[ClientList] IP: %s SEGA ID: %s Player ID: %s Player Name: %s Block: %s" % (
                client_host, client_segaid, client_player_id, client_player_name, client_block))
    else:
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
        sender.send_crypto_packet(packetFactory.SystemMessagePacket(string, 0x2).build())


@CommandHandler("globalmsg", "Sends a global message to everyone on the server. Admins only.", True)
def global_message(sender, params):
    if isinstance(sender, basic.LineReceiver):
        if len(params.split(' ', 2)) < 3:
            print("[ShipProxy] Incorrect usage. Usage: >>> globalmsg  <message_type> <Message>")
            return
        mode = int(params.split(' ', 2)[1])
        message = params.split(' ', 2)[2]
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
                    packetFactory.SystemMessagePacket("{ora}[Proxy Global Message]{def} %s" % message, mode).build())
        print("[ShipProxy] Sent global message!")
    else:
        if len(params.split(' ', 2)) < 3:
            sender.send_crypto_packet(packetFactory.SystemMessagePacket("[ShipProxy] {red}Incorrect usage. Usage: |globalmsg  <message_type> <Message>", 0x3).build())
            return
        mode = int(params.split(' ', 2)[1])
        message = params.split(' ', 2)[2]
        for client in data.clients.connectedClients.values():
            if client.get_handle() is not None:
                client.get_handle().send_crypto_packet(
                    packetFactory.SystemMessagePacket("{ora}[Proxy Global Message]{def} %s" % message, mode).build())


@CommandHandler("exit")
def exit_proxy(sender, params):
    if isinstance(sender, basic.LineReceiver):
        print("[ShipProxy] Exiting...")
        reactor.callFromThread(reactor.stop)
