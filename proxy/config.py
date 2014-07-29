import json, os.path

configKeys = {'packetLogging' : False, 'myIpAddr': "0.0.0.0", 'bindIp' : "0.0.0.0", 'blockNameMode' : 0, 'noisy' : False, 'webapi' : False}

blockNames = {}

def loadConfig():
	global configKeys
	global blockNames
	if not os.path.exists('cfg/pso2proxy.config.json'):
		try:
			os.makedirs('cfg/')
		except:
			pass
		makeDefaultConfig()
	f = open('cfg/pso2proxy.config.json', 'r')
	newcfg = f.read()
	f.close()
	configKeys = json.loads(newcfg)
	print("[ShipProxy] Config loaded!")
	if os.path.exists('cfg/blocknames.config.json'):
		b = open('cfg/blocknames.config.json', 'r')
		bStr = b.read()
		blockNames = json.loads(bStr)
		print('[ShipProxy] Block names loaded!')



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
blockNameMode = configKeys['blockNameMode']
noisy = configKeys['noisy']
webapi = configKeys['webapi']
