packetFunctions = {}
commands = {}
onStart = []
onConnection = []
onConnectionLoss = []


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

    def __init__(self, command):
        self.command = command

    def __call__(self, f):
        global commands
        commands[self.command] = f


def on_start_hook(f):
    global onStart
    onStart.append(f)
    return f


def on_connection_hook(f):
    global onConnection
    onConnection.append(f)
    return f


def on_connection_lost_hook(f):
    global onConnectionLoss
    onConnectionLoss.append(f)
    return f