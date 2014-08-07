import blocks
import config
import packetFactory

from ships import get_ship_from_port

connectedClients = {}
"""
:type connectedClients: dict[int, ClientData]
"""


class ClientData(object):
    """docstring for ClientData"""

    def __init__(self, ip_address, segaid, ship, handle):
        self.ipAddress = ip_address
        self.segaId = segaid
        self.handle = handle
        self.ship = ship
        self.preferences = ClientPreferences(segaid)

    def get_handle(self):
        """
        :rtype : ShipProxy
        """
        return self.handle

    def set_handle(self, handle):
        self.handle = handle


class ClientPreferences():
    def __init__(self, segaid):
        self._config = config.YAMLConfig("cfg/user.preferences.yml")
        self.segaid = segaid
        if not self._config.key_exists(segaid):
            self._config.set_key(segaid, {})

    def has_preference(self, preference):
        my_preferences = self._config.get_key(self.segaid)
        if preference in my_preferences:
            return True
        else:
            return False

    def get_preference(self, preference):
        my_preferences = self._config.get_key(self.segaid)
        if self.has_preference(preference):
            return my_preferences[preference]
        else:
            return None

    def set_preference(self, preference, value):
        my_preferences = self._config.get_key(self.segaid)
        my_preferences[preference] = value
        self._config.set_key(self.segaid, my_preferences)


def add_client(handle):
    connectedClients[handle.playerId] = ClientData(handle.transport.getPeer().host, handle.myUsername.rstrip('\0'), get_ship_from_port(handle.transport.getHost().port), handle)
    print('[Clients] Registered client %s (ID:%i) in online clients' % (handle.myUsername, handle.playerId))
    if config.is_player_id_banned(handle.playerId):
        print('[Bans] Player %s (ID:%i) is banned!' % (handle.myUsername, handle.playerId))
        handle.send_crypto_packet(packetFactory.SystemMessagePacket("You are banned from connecting to this PSO2Proxy.", 0x1).build())
        handle.transport.loseConnection()


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
