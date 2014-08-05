import json
import os.path


class JSONConfig(object):
    _config_values = {}

    def __init__(self, filename, default_keys={}, strict_mode=False):
        self.filename = filename
        self.default_keys = default_keys
        self.strict_mode = strict_mode
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.filename):
            self._make_default_config()
        else:
            f = open(self.filename, 'r')
            self._config_values = json.load(f)
            f.close()
            self._validate_config()
        print("[Config] Config %s loaded!" % self.filename)

    def _save_config(self):
        f = open(self.filename, "w")
        json.dump(self._config_values, f, indent=1)
        f.close()

    def _make_default_config(self):
        try:
            os.makedirs(self.filename)
        except:
            pass
        f = open(self.filename, "w")
        json.dump(self.default_keys, f, indent=1)
        f.close()
        print("[Config] Default config for %s created." % self.filename)

    def _validate_config(self):
        for key, value in self.default_keys.iteritems():
            if key not in self._config_values:
                self._config_values[key] = value
                print("[Config] Added new default %s for config %s" % (key, self.filename))
        if self.strict_mode:
            for key in self.default_keys.keys():
                if key not in self.default_keys:
                    del self._config_values[key]
                    print("[Config] Deleted invlid key %s for config %s" % (key, self.filename))
        self._save_config()

    def get_key(self, key):
        if key not in self._config_values:
            raise KeyError
        return self._config_values[key]

    def set_key(self, key, value):
        self._config_values[key] = value
        self._save_config()

    def key_exists(self, key):
        if key in self._config_values:
            return True
        else:
            return False


banList = []

globalConfig = JSONConfig("cfg/pso2proxy.config.json",
                          {'packetLogging': False, 'myIpAddr': "0.0.0.0", 'bindIp': "0.0.0.0", 'blockNameMode': 0,
                           'noisy': False, 'admins': []}, True)

blockNames = {}


def is_admin(sega_id):
    if sega_id in globalConfig.get_key('admins'):
        return True
    else:
        return False


def load_bans():
    global banList
    if not os.path.exists('cfg/pso2proxy.bans.json'):
        f = open('cfg/pso2proxy.bans.json', 'w')
        f.write(json.dumps(banList))
        f.close()
    f = open('cfg/pso2proxy.bans.json', 'r')
    bans = f.read()
    f.close()
    banList = json.loads(bans)
    print("[Bans] %i bans loaded!" % len(bans))


def save_bans():
    global banList
    f = open('cfg/pso2proxy.bans.json', 'w')
    f.write(json.dumps(banList))
    f.close()
    print("[Bans] %i bans saved!" % len(banList))


def is_segaid_banned(segaid):
    global banList
    for ban in banList:
        if 'segaId' in ban:
            if ban['segaId'] == segaid:
                return True
    return False


def is_player_id_banned(player_id):
    global banList
    for ban in banList:
        if 'playerId' in ban:
            if int(ban['playerId']) == player_id:
                return True
    return False


load_bans()

packetLogging = globalConfig.get_key('packetLogging')
myIpAddress = globalConfig.get_key('myIpAddr')
bindIp = globalConfig.get_key('bindIp')
blockNameMode = globalConfig.get_key('blockNameMode')
noisy = globalConfig.get_key('noisy')
admins = globalConfig.get_key('admins')