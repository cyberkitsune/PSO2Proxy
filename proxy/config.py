import json, os.path

banList = []

configKeys = {'packetLogging': False, 'myIpAddr': "0.0.0.0", 'bindIp': "0.0.0.0", 'blockNameMode': 0, 'noisy': False,
              'webapi': False}

blockNames = {}


def load_config():
    global configKeys
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
    print("[ShipProxy] Config loaded!")
    if os.path.exists('cfg/blocknames.config.json'):
        b = open('cfg/blocknames.config.json', 'r')
        block_json = b.read()
        blockNames = json.loads(block_json)
        print('[ShipProxy] Block names loaded!')


def make_default_config():
    global configKeys
    json_encoded = json.dumps(configKeys, indent=1)
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
