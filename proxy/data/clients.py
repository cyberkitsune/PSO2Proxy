import blocks
import config
import packetFactory

connectedClients = {}


class ClientData(object):
    """docstring for ClientData"""

    def __init__(self, ip_address, segaid, handle):
        self.ipAddress = ip_address
        self.segaId = segaid
        self.handle = handle
        self.preferences = {}

    def get_handle(self):
        return self.handle

    def set_handle(self, handle):
        self.handle = handle

    def get_preferences(self):
        return self.preferences

    def set_preferences(self, preferences):
        self.preferences = preferences


def add_client(handle):
    connectedClients[handle.playerId] = ClientData(handle.transport.getPeer().host, handle.myUsername.rstrip('\0'),
                                                   handle)
    print('[Clients] Registered client %s (ID:%i) in online clients' % (handle.myUsername, handle.playerId))
    if config.is_player_id_banned(handle.playerId):
        print('[Bans] Player %s (ID:%i) is banned!' % (handle.myUsername, handle.playerId))
        handle.sendCryptoPacket(packetFactory.SystemMessagePacket("You are banned from connecting to this PSO2Proxy.", 0x1).build())
        handle.transport.loseConnection()
    handle.sendCryptoPacket(packetFactory.SystemMessagePacket("Welcome to PSO2Proxy! There are currently %i clients connected. Use |help for help!", 0x3).build())


def remove_client(handle):
    print("[Clients] Removing client %s (ID:%i) from online clients" % (handle.myUsername, handle.playerId))
    del connectedClients[handle.playerId]


def populate_data(handle):
    client_data = connectedClients[handle.playerId]
    client_data.handle = handle
    handle.myUsername = client_data.segaId
    handle.peer.myUsername = client_data.segaId
    if handle.transport.getHost().port in blocks.blockList:
        block_name = blocks.blockList[handle.transport.getHost().port][1]
    else:
        block_name = None
    print("[ShipProxy] %s has successfully changed blocks to %s!" % (handle.myUsername, block_name))
    handle.loaded = True
