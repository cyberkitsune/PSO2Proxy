# redpill.py PSO2Proxy plugin
# For use with redpill.py flask webapp and website for packet logging and management
import sqlite3, plugins, os, glob, tarfile, shutil, cProfile, pstats, StringIO

dbLocation = '/var/pso2-www/redpill/redpill.db'
enabled = True

if enabled:
	@plugins.onStartHook
	def redpillInit():
		print("[Redpill] Redpill initilizing with database %s." % dbLocation)

	@plugins.packetHook(0x11, 0x0)
	def loginPacketHook(context, packet):
		username = packet[0x8:0x48].decode('utf-8')
		username = username.rstrip('\0')
		con = getConn()
		with con:
			if get_userid(con, username) is None:
				context.transport.loseConnection()
				print("[Redpill] %s is not in the whitelist database. Hanging up." % username)
		return packet

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
		if not os.path.exists("packets/%s/%i/" % (sid, timestamp)):
			print("[Redpill] Could not check-in session for %s, timestamp %i does not exist" % (sid, timestamp))
			return

		profile = cProfile.Profile()
		profile.enable()
		con = getConn()
		with con:
			sessionId = create_session(con, get_userid(con, sid), timestamp)
			packets = glob.glob("packets/%s/%i/*.bin" % (sid, timestamp))
			count = 0
			for packet in packets:
				order, typeSub, pSender, dotbin = packet.split(".")
				pType, pSubType = typeSub.split("-")
				if pSender == "C":
					pFrom = 0
				if pSender == "S":
					pFrom = 1
				pID = get_packetId(con, int(pType, 16), int(pSubType, 16))
				if pID is None:
					pID = create_packet(con, int(pType, 16), int(pSubType, 16), get_userid(con, sid))
				add_sessionData(con, sessionId, pID, pFrom)
				incr_packetCount(con, pID)
				count += 1
			print("[Redpill] Checked in session %i for %s with %i packets" % (timestamp, sid, count))
			tar = tarfile.open("packets/%s/%i.tar.gz" % (sid, timestamp), "w:gz")
			tar.add("packets/%s/%i/" % (sid, timestamp), arcname="%i" % timestamp)
			tar.close()
			shutil.rmtree("packets/%s/%i/" % (sid, timestamp))
			print("[Redpill] Archived as %i.tar.gz and deleted base folder." % timestamp)
		profile.disable()
		s = StringIO.StringIO()
		sortby = 'cumulative'
		ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
		ps.print_stats()
		print s.getvalue()



	def getConn():
		conn = sqlite3.connect(dbLocation)
		conn.row_factory = sqlite3.Row
		return conn

	def get_userid(con, username):
		cur = con.cursor()
		cur.execute("select id from users where segaid = ?", (username, ))
		out = cur.fetchone()
		if out is None:
			return None
		else:
			return out[0]

	def create_session(con, userid, timestamp):
		cur = con.cursor()
		cur.execute("insert into sessions (user, timestamp, name, notes) VALUES (?,?,?,?) ", (userid, timestamp, "Unnamed Session %s" % timestamp, "No notes."))
		return cur.lastrowid

	def get_session_id(con, userid, timestamp):
		cur = con.cursor()
		cur.execute("select id from sessions where user = ? and timestamp = ?", (userid, timestamp))
		out = cur.fetchone()
		if out is None:
			return None
		else:
			return out[0]

	def add_sessionData(con, sessionId, packetId, sentFrom):
		cur = con.cursor()
		cur.execute("insert into session_data (sessionID, sentFrom, packetId, notes) values (?,?,?,?)", (sessionId, int(sentFrom), packetId, "No notes."))

	def get_packetId(con, pType, subType):
		cur = con.cursor()
		cur.execute("select id from packets where type = ? and subType = ?", (pType, subType))
		out = cur.fetchone()
		if out is None:
			return None
		else:
			return out[0]

	def incr_packetCount(con, packetId):
		cur = con.cursor()
		cur.execute("update packets set count=count+1 where id = ?", (packetId,))

	def create_packet(con, pType, subType, logger):
		cur = con.cursor()
		cur.execute("insert into packets (type, subType, firstLoggedBy, count) values (?, ?, ?, 0)", (pType, subType, logger))
		return cur.lastrowid
