banList = []


def loadBans():
	global banList
	banList = []
	f = open('banList.txt')
	bans = f.read()
	f.close()
	bans = bans.split(',')
	for b in bans:
		banList.append(b)
	print("[Bans] %i bans loaded!" % len(bans))