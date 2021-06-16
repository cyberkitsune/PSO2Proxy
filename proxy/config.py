import json
import os.path
import subprocess
import yaml

brokenlist = list()


class YAMLConfig(object):
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
            self._config_values = yaml.load(f)
            f.close()
            self._validate_config()
        print("[Config] Config %s loaded!" % self.filename)

    def _save_config(self):
        f = open(self.filename, "w")
        yaml.dump(self._config_values, f, indent=1)
        f.close()

    def _make_default_config(self):
        try:
            os.makedirs(os.path.dirname(self.filename))
        except Exception as e:
            print("Error making folder %s because %s" % (os.path.dirname(self.filename), e))
            pass
        f = open(self.filename, "w")
        yaml.dump(self.default_keys, f, indent=1)
        f.close()
        print("[Config] Default config for %s created." % self.filename)
        self._load_config()

    def _validate_config(self):
        for key, value in self.default_keys.items():
            if key not in self._config_values:
                self._config_values[key] = value
                print("[Config] Added new default %s for config %s" % (key, self.filename))
        if self.strict_mode:
            for key in self._config_values.keys():
                if key not in self.default_keys:
                    del self._config_values[key]
                    print("[Config] Deleted invlid key %s for config %s" % (key, self.filename))
                else:
                    if self._config_values[key] is None:
                        self._config_values[key] = self.default_keys[key]
                        print("[Config] Resetting invalid key type for %s in config %s." % (key, self.filename))
        self._save_config()

    def _get_key(self, key):
        if key not in self._config_values:
            raise KeyError
        if str(type(self._config_values[key])) == "<type 'unicode'>":
            return self._config_values[key].encode('utf-8')
        else:
            return self._config_values[key]

    def set_key(self, key, value):
        self._config_values[key] = value
        self._save_config()

    def key_exists(self, key):
        if key in self._config_values:
            return True
        else:
            return False

    def __getitem__(self, item):
        return self._get_key(item)

    def __setitem__(self, key, value):
        self.set_key(key, value)


banList = []

globalConfig = YAMLConfig(
    "cfg/pso2proxy.config.yml",
    {
        'myIpAddr': "0.0.0.0",
        'bindIp': "0.0.0.0",
        'blockNameMode': 1,
        'noisy': False,
        'admins': [],
        'enabledShips': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'commandPrefix': '!'
    },
    True
)

blockNames = {}
ShipLabel = {}

proxy_ver = str(str(subprocess.Popen(["git", "describe", "--always"], stdout=subprocess.PIPE).communicate()[0]).rstrip("\n"))


def is_admin(sega_id):
    if sega_id in globalConfig['admins']:
        return True
    else:
        return False


def load_block_names():
    global blockNames
    if globalConfig['blockNameMode'] == 0:
        return "[ShipProxy] Blocks are not renamed"
    if os.path.exists("cfg/blocknames.resources.json"):
        f = open("cfg/blocknames.resources.json", 'r', encoding='utf-8')
        try:
            blockNames = json.load(f)
            f.close()
            return ("[ShipProxy] %s Block names loaded!" % len(blockNames))
        except ValueError:
            f.close()
            return ("[ShipProxy] Failed to load blockname file")

    else:
        return "[ShipProxy] BlockName file does not exists"


load_block_names()


def load_ship_names():
    global ShipLabel
    ShipLabel.clear()  # Clear list

    ShipLabel["Console"] = "Console"

    if os.path.exists("cfg/shipslabel.resources.json"):
        f = open("cfg/shipslabel.resources.json", 'r')
        try:
            for key, val in json.load(f, encoding='utf-8').items():
                ShipLabel[key] = val.encode("utf8", 'ignore')
            f.close()
            return ("[GlobalChat] %s ship labels names loaded!" % len(ShipLabel))
        except ValueError:
            f.close()
            return ("[GlobalChat] Failed to load ship  labels!")
    else:
        return "[GlobalChat] shipslabel file does not exists"


load_ship_names()


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
    return ("[Bans] %i bans loaded!" % len(bans))


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

myIpAddress = globalConfig['myIpAddr']
bindIp = globalConfig['bindIp']
blockNameMode = globalConfig['blockNameMode']
noisy = globalConfig['noisy']
admins = globalConfig['admins']
