import blocks
import config
import packetFactory
import sqlite3
import twisted
import yaml
from threading import Lock

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
        :rtype : ShipProxy.ShipProxy
        """
        if self.handle is None:
            return None
        if isinstance(self.handle, twisted.internet.protocol.Protocol) and hasattr(self.handle.transport, 'socket'):
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
        self._db_lock = Lock()
        print("[Database] User preference database created!")

    def get_data_for_sega_id(self, sega_id):
        if not (sega_id in self.user_preference_cache):
            self.user_preference_cache[sega_id] = self._get_user_data_from_db(sega_id)
        return self.user_preference_cache[sega_id]

    def _get_user_data_from_db(self, segaid):
        user_data = {}
        self._db_lock.acquire(True)
        local_cursor = self._db_connection.cursor()
        local_cursor.execute("SELECT data FROM users WHERE sega_id = ?", (str(segaid), ))
        user_row = local_cursor.fetchone()
        if user_row is not None:
            user_data = yaml.load(user_row['data'])
        else:
            local_cursor.execute("INSERT INTO users (sega_id, data) VALUES  (?,?)", (str(segaid), yaml.dump({})))
        self._db_lock.release()
        return user_data

    def _update_user_data_in_db(self, sega_id):
        if sega_id not in self.user_preference_cache:
            raise KeyError("User data isn't even cached, can't update data!")
        self._db_lock.acquire(True)
        local_cursor = self._db_connection.cursor()
        local_cursor.execute("UPDATE users SET data = ? WHERE sega_id = ?", (yaml.dump(self.user_preference_cache[sega_id]), str(sega_id)))
        self._db_connection.commit()
        self._db_lock.release()

    def update_user_cache(self, sega_id, new_config):
        self.user_preference_cache[sega_id] = new_config
        self._update_user_data_in_db(sega_id)

    def get_db_size(self):
        self._db_lock.acquire(True)
        local_cursor = self._db_connection.cursor()
        local_cursor.execute("SELECT COUNT(*) FROM users")
        self._db_lock.release()
        return local_cursor.fetchone()[0]

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

    def __del__(self):
        dbManager.update_user_cache(self.segaid, self._config) # Incase it doesn't stick I guess


def add_client(handle):
    try:
        l_my_username = handle.myUsername.rstrip('\0')
    except AttributeError:
        l_my_username = handle.myUsername

    connectedClients[handle.playerId] = ClientData(handle.transport.getPeer().host, l_my_username, get_ship_from_port(handle.transport.getHost().port), handle)
    print('[Clients] Registered client %s (ID:%i) in online clients' % (l_my_username, handle.playerId))
    if config.is_player_id_banned(handle.playerId):
        print('[Bans] Player %s (ID:%i) is banned!' % (l_my_username, handle.playerId))
        handle.send_crypto_packet(packetFactory.SystemMessagePacket("You are banned from connecting to this PSO2Proxy.", 0x1).build())
        handle.transport.loseConnection()


def remove_client(handle):
    print("[Clients] Removing client %s (ID:%i) from online clients" % (handle.myUsername, handle.playerId))
    if handle.playerId in connectedClients:
        del connectedClients[handle.playerId]
    else:
        print("[Clients] client %s (ID:%i) is not in list" % (handle.myUsername, handle.playerId))


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
