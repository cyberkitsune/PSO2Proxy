# redpill.py PSO2Proxy plugin
# For use with redpill.py flask webapp and website for packet logging and management
import sqlite, plugins, os, glob

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
		sid = client.myUsername
		timestamp = client.connTimestamp
		if sid is None or timestamp is None:
			print("[Redpill] Unable to check-in session, SID or timestamp is none.")
			return
		if not os.path.exists("packets/%s/%s/" % (sid, timestamp)):
			print("[Redpill] Could not check-in session for %s, timestamp %s does not exist" % (sid, timestamp))
			return

		packets = glob.glob("packets/%s/%s/*.bin" % (sid, timestamp))
		count = 0
		for packet in packets:


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

	def get_userid(username):
		con = getConn()
		with con:
			cur = con.cursor()
			cur.execute("select id from users where username = ?", (username, ))
			out = cur.fetchone()
			if out is None:
				return None:
			else:
				return out[0]

	def create_session(userid, timestamp):
		con = getConn()
		with con:
			cur = con.cursor()
			cur.execute("insert into sessions (user, timestamp, name, notes) VALUES (?,?,?,?) ", (userid, timestamp, "Unnamed Session %s" % timestamp, "No notes."))

	def get_session_id(userid, timestamp):
		con = getConn()
		with con:
			cur = con.cursor()
			cur.execute("select id from sessions where user = ? and timestamp = ?", (userid, timestamp))
			out = cur.fetchone()
			if out is None:
				return None
			else:
				return out