import sqlite3
import yaml
import blocks
import config
import packetFactory
from twisted.internet.protocol import Protocol

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
        if self.handle is None:
            return None
        if isinstance(self.handle, Protocol):
            return self.handle
        return None

    def set_handle(self, handle):
        self.handle = handle


class SQLitePreferenceManager():

    user_preference_cache = {}

    def __init__(self):
        self._db_connection = sqlite3.connect("cfg/pso2proxy.userprefs.db")
        setup_cursor = self._db_connection.cursor()
        setup_cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, sega_id TEXT, data TEXT)")
        self._db_connection.row_factory = sqlite3.Row
        self._db_connection.commit()
        print("[Database] User preference database created!")

    def get_data_for_sega_id(self, sega_id):
        if not sega_id in self.user_preference_cache:
            self.user_preference_cache[sega_id] = self._get_user_data_from_db(sega_id)
        return self.user_preference_cache[sega_id]

    def _get_user_data_from_db(self, segaid):
        user_data = {}
        local_cursor = self._db_connection.cursor()
        local_cursor.execute("SELECT data FROM users WHERE sega_id = ?", (segaid, ))
        user_row = local_cursor.fetchone()
        if user_row is not None:
            user_data = yaml.load(user_row['data'])
        else:
            local_cursor.execute("INSERT INTO users (sega_id, data) VALUES  (?,?)", (segaid, yaml.dump({})))
        return user_data

    def _update_user_data_in_db(self, sega_id):
        if sega_id not in self.user_preference_cache:
            raise KeyError("User data isn't even cached, can't update data!")
        local_cursor = self._db_connection.cursor()
        local_cursor.execute("UPDATE users SET data = ? WHERE sega_id = ?", (yaml.dump(self.user_preference_cache[sega_id]), sega_id))
        self._db_connection.commit()

    def update_user_cache(self, sega_id, new_config):
        self.user_preference_cache[sega_id] = new_config
        self._update_user_data_in_db(sega_id)

    def close_db(self):
        self._db_connection.close()
        print("[Database] Connection closed!")

    def __del__(self):
        self.close_db()

dbManager = SQLitePreferenceManager()


class ClientPreferences():
    def __init__(self, segaid):
        self._config = dbManager.get_data_for_sega_id(segaid)
        self.segaid = segaid

    def has_preference(self, preference):
        if preference in self._config:
            return True
        else:
            return False

    def get_preference(self, preference):
        if preference in self._config:
            return self._config[preference]
        else:
            return None

    def set_preference(self, preference, value):
        self._config[preference] = value
        dbManager.update_user_cache(self.segaid, self._config)

    def __getitem__(self, item):
        return self.get_preference(item)

    def __setitem__(self, key, value):
        self.set_preference(key, value)

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
