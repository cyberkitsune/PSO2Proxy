import json
import os.path

banList = []

defaultConfigKeys = {'packetLogging': False, 'myIpAddr': "0.0.0.0", 'bindIp': "0.0.0.0", 'blockNameMode': 0,
                     'noisy': False,
                     'webapi': False, 'admins': []}

configKeys = {}

blockNames = {}


def load_config():
    global configKeys
    global defaultConfigKeys
    global blockNames
    if not os.path.exists('cfg/pso2proxy.config.json'):
        try:
            os.makedirs('cfg/')
        except:
            pass
        make_default_config()
    f = open('cfg/pso2proxy.config.json', 'r')
    new_config = f.read()
    f.close()
    configKeys = json.loads(new_config)
    configKeys = verify_config_keys(configKeys)
    print("[ShipProxy] Config loaded!")
    f = open('cfg/pso2proxy.config.json', 'w')
    f.write(json.dumps(configKeys, indent=1))
    f.close()
    if os.path.exists('cfg/blocknames.resource.json'):
        b = open('cfg/blocknames.resource.json', 'r')
        block_json = b.read()
        blockNames = json.loads(block_json)
        print('[ShipProxy] Block names loaded!')


def is_admin(sega_id):
    global configKeys
    if sega_id in configKeys['admins']:
        return True
    else:
        return False


def save_config():
    f = open('cfg/pso2proxy.config.json', 'w')
    f.write(json.dumps(configKeys, indent=1))
    f.close()
    print("[ShipProxy] Config saved!")


def verify_config_keys(config_dict):
    global defaultConfigKeys
    for key, value in defaultConfigKeys.iteritems():
        if key not in config_dict:
            config_dict[key] = value
            print("[Config] Adding default option for config key %s as it did not exist before." % key)
    return config_dict


def make_default_config():
    global configKeys
    json_encoded = json.dumps(defaultConfigKeys, indent=1)
    f = open('cfg/pso2proxy.config.json', 'w')
    f.write(json_encoded)
    f.close()


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


load_config()
load_bans()

packetLogging = configKeys['packetLogging']
myIpAddress = configKeys['myIpAddr']
bindIp = configKeys['bindIp']
blockNameMode = configKeys['blockNameMode']
noisy = configKeys['noisy']
webapi_enabled = configKeys['webapi']
admins = configKeys['admins']