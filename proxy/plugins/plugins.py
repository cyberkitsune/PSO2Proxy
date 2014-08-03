packetFunctions = {}
commands = {}
onStart = []
onConnection = []
onConnectionLoss = []


class packetHook(object):
    def __init__(self, pktType, pktSubtype):
        self.pktType = pktType
        self.pktSubtype = pktSubtype

    def __call__(self, f):
        global packetFunctions
        if (self.pktType, self.pktSubtype) not in packetFunctions:
            packetFunctions[(self.pktType, self.pktSubtype)] = []
        packetFunctions[(self.pktType, self.pktSubtype)].append(f)


class commandHook(object):
    """docstring for commandHook"""

    def __init__(self, command):
        self.command = command

    def __call__(self, f):
        global commands
        commands[self.command] = f


def onStartHook(f):
    global onStart
    onStart.append(f)
    return f


def onConnectionHook(f):
    global onConnection
    onConnection.append(f)
    return f


def onConnectionLossHook(f):
    global onConnectionLoss
    onConnectionLoss.append(f)
    return f