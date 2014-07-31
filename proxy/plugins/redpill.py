# redpill.py PSO2Proxy plugin
# For use with redpill.py flask webapp and website for packet logging and management
import sqlite, plugins

dbLocation = '/var/pso2-www/redpill/redpill.db'
enabled = False

if enabled:
	@plugins.onStartHook
	def redpillInit():
		print("[Redpill] Redpill initilizing with database %s." % dbLocation)

	@plugins.packetHook(0x11, 0x0)
	def loginPacketHook(context, packet):
		username = packet[0x8:0x48].decode('utf-8')
		username = username.rstrip('\0')
		if not user_exists(username):
			context.loseConnection()
			print("[Redpill] %s is not in the whitelist database. Hanging up." % username)

	@plugins.onConnectionHook
	def registerClient(client):
		pass

	@plugins.onConnectionLossHook
	def archivePackets(client):
		pass

	def getConn():
		conn = sqlite3.connect(dbLocation)
		conn.row_factory = sqlite3.Row
		return conn

	def user_exists(username):
		con = getConn()
		with con:
			cur = con.cursor()
			cur.execute("select * from users where username = ? COLLATE NOCASE", (username, ))
			check = cur.fetchone()
			if check == None:
				return False
			else:
				return True