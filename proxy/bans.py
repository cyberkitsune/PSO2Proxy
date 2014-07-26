import os
banList = []


def loadBans():
	global banList
	if not os.path.exists('banList.txt'):
		f = open('banList.txt', 'w+')
		f.close()
	banList = []
	f = open('banList.txt')
	bans = f.read()
	f.close()
	bans = bans.split(',')
	for b in bans:
		banList.append(b)
	print("[Bans] %i bans loaded!" % len(bans))