import json, os.path

configKeys = {'packetLogging' : False, 'myIpAddr': "0.0.0.0", 'bindIp' : "0.0.0.0", 'showBlockNamesAsIp' : False, 'noisy' : False, 'webapi' : False}

def loadConfig():
	global configKeys
	if not os.path.exists('cfg/pso2proxy.config.json'):
		os.makedirs('cfg/')
		makeDefaultConfig()
	f = open('cfg/pso2proxy.config.json', 'r')
	newcfg = f.read()
	configKeys = json.loads(newcfg)
	print("[ShipProxy] Config loaded!")



def makeDefaultConfig():
	global configKeys
	jsonEnc = json.dumps(configKeys, indent=1)
	f = open('cfg/pso2proxy.config.json', 'w')
	f.write(jsonEnc)
	f.close()

loadConfig()

packetLogging = configKeys['packetLogging']
myIpAddr = configKeys['myIpAddr']
bindIp = configKeys['bindIp']
showBlockNamesAsIp = configKeys['showBlockNamesAsIp']
noisy = configKeys['noisy']
webapi = configKeys['webapi']
