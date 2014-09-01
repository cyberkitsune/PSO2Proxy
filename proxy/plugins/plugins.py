packetFunctions = {}
commands = {}
rawPacketFunctions = []
onStart = []
onConnection = []
onConnectionLoss = []
onQueryConnection = []
onClientRemove = []
onInitialConnection = []


class PacketHook(object):
    def __init__(self, packet_type, packet_subtype):
        self.pktType = packet_type
        self.pktSubtype = packet_subtype

    def __call__(self, f):
        global packetFunctions
        if (self.pktType, self.pktSubtype) not in packetFunctions:
            packetFunctions[(self.pktType, self.pktSubtype)] = []
        packetFunctions[(self.pktType, self.pktSubtype)].append(f)


class CommandHook(object):
    """docstring for commandHook"""

    def __init__(self, command, help_text=None, admin_only=False):
        self.command = command
        self.help_text = help_text
        self.admin_only = admin_only

    def __call__(self, command_class):
        global commands
        commands[self.command] = [command_class, self.help_text, self.admin_only]


def on_start_hook(f):
    global onStart
    onStart.append(f)
    return f


def on_query_connection_hook(f):
    global onQueryConnection
    onQueryConnection.append(f)
    return f


def on_connection_hook(f):
    global onConnection
    onConnection.append(f)
    return f


def on_connection_lost_hook(f):
    global onConnectionLoss
    onConnectionLoss.append(f)
    return f


def on_client_remove_hook(f):
    global onClientRemove
    onClientRemove.append(f)
    return f


def on_initial_connect_hook(f):
    global onInitialConnection
    onInitialConnection.append(f)
    return f


def raw_packet_hook(f):
    global rawPacketFunctions
    rawPacketFunctions.append(f)
    return f
