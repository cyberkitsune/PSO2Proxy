import struct, io
import data.blocks as blocks
import data.players as players
import packetFactory
from PSOCryptoUtils import PSO2RSADecrypt, PSO2RC4, PSO2RSAEncrypt
import commands
import bans
from config import myIpAddr as ip

i0, i1, i2, i3 = ip.split(".")
rsaDecryptor = PSO2RSADecrypt("keys/myKey.pem")
rsaEncryptor = PSO2RSAEncrypt("keys/SEGAKey.pem")

# struct PacketHeader { int size; char type1, type2, field_6, field_7; };

packetList = {}

class packetHandler(object):
	def __init__(self, pktType, pktSubtype):
		self.pktType = pktType
		self.pktSubtype = pktSubtype

	def __call__(self, f):
		global packetList
		packetList[(self.pktType, self.pktSubtype)] = f

@packetHandler(0x11, 0x0)
def loginPacket(context, data):
	username = data[0x8:0x48].decode('utf-8')
	username = username.rstrip('\0')
	print("[LoginPacket] Logging player %s in..." % username)
	context.myUsername = username
	context.peer.myUsername = username
	if username in bans.banList:
		print("[Bans] %s is banned! Disconnecting..." % username)
		context.transport.loseConnection()
		context.peer.transport.loseConnection()
		return None
	return data

@packetHandler(0x11, 0xB)
def keyPacket(context, data):
	print("[KeyPacket] Decrypting RC4 key packet!")
	rsaBlob = data[0x8:0x88]
	unEncrypted = rsaDecryptor.decrypt(rsaBlob)
	if unEncrypted is None:
		print("[KeyPacket] Could not decrypt RSA for client %s, Perhaps their client's key is unmodified? Hanging up." % context.transport.getPeer().host)
		context.transport.loseConnection()
		return None
	print("[KeyPacket] Client %s RC4 key %s" % (context.transport.getPeer().host, ''.join("%02x " % b for b in bytearray(unEncrypted[0x10:0x20])),))
	context.c4crypto = PSO2RC4(unEncrypted[0x10:0x20])
	context.peer.c4crypto = PSO2RC4(unEncrypted[0x10:0x20])
	#Re-RSA packet
	blob = io.BytesIO()
	blob.write(data[:0x8])
	blob.write(rsaEncryptor.encrypt(unEncrypted))
	blob.write(data[0x88:len(data)])
	blob.flush()
	return blob.getvalue()

@packetHandler(0x11, 0x1)
def blockInfoPacket(context, data):
	data = bytearray(data)
	blockport = context.peer.transport.getHost().port
	if blockport in blocks.blockList:
		blockInfo = blocks.blockList[blockport]
		addrString = ('%s%s:%i' % ((blockInfo[1])[:6], blockInfo[0], blockport)).encode('utf-16le')
		struct.pack_into('%is' % len(addrString), data, 0x1C, addrString)
		if len(addrString) < 0x40:
			struct.pack_into('%ix' % (0x40 - len(addrString)), data, 0x1C + len(addrString))
	return str(data)

@packetHandler(0x11, 0x4f)
def teamRoomInfoPacket(context, data):
	data = bytearray(data)
	o1, o2, o3, o4 = struct.unpack_from('BBBB', buffer(data), 0x20)
	ipStr = "%i.%i.%i.%i" % (o1, o2, o3, o4)
	port = struct.unpack_from('H', buffer(data), 0x28)[0]
	if port not in blocks.blockList:
		print("[BlockPacket] Discovered a 'Team Room' block at %s:%i!" % (ipStr, port))
		blocks.blockList[port] = (ipStr, "Team Room", port)
	struct.pack_into('BBBB', data, 0x20, int(i0), int(i1), int(i2), int(i3))
	return str(data)

@packetHandler(0x11, 0x17)
def myRoomInfoPacket(context, data):
	data = bytearray(data)
	o1, o2, o3, o4 = struct.unpack_from('BBBB', buffer(data), 0x20)
	ipStr = "%i.%i.%i.%i" % (o1, o2, o3, o4)
	port = struct.unpack_from('H', buffer(data), 0x28)[0]
	if port not in blocks.blockList:
		print("[BlockPacket] Discovered a 'My Room' block at %s:%i!" % (ipStr, port))
		blocks.blockList[port] = (ipStr, "My Room", port)
	struct.pack_into('BBBB', data, 0x20, int(i0), int(i1), int(i2), int(i3))
	return str(data)

@packetHandler(0x7,0x0)
def chatHandler(context, data):
	pId = struct.unpack_from('I', data, 0x8)[0]
	message = data[0x1C:].decode('utf-16') # This is technically improper. Should use the xor byte to check string length (See packetReader)
	if pId == 0: # Prolly the wrong way to check, but check if a PSO2 client sent this packet
		if message[0] == '!':
			command = (message.split(' ')[0])[1:] # Get the first word (the command) and strip the '!''
			if command in commands.commandList:
				commands.commandList[command](context, message) # Lazy...
			else:
				context.sendCryptoPacket(packetFactory.ChatPacket(context.playerId, "[Proxy] %s is not a command!" % command).build())
			return None
		return data
	if pId in players.playerList:
		name = players.playerList[pId][0]
	else:
		name = "ID:%i" % pId
	print("[ChatPacket] <%s> %s" % (name, message))
	return data

@packetHandler(0x11,0x10)
def blockListPacket(context, data):
	data = bytearray(data)
	print("[BlockList] Got block list! Updating local cache and rewriting packet...")
	# Jump to 0x28, 0x88 sep
	pos = 0x28
	while pos < len(data) and data[pos] != 0:
		name = data[pos:pos+0x40].decode('utf-16')
		o1, o2, o3, o4, port = struct.unpack_from('BBBBH', buffer(data), pos+0x40)
		ipStr = "%i.%i.%i.%i" % (o1, o2, o3, o4)
		if port not in blocks.blockList:
			print("[BlockList] Discovered new block %s at addr %s:%i! Recording..." % (name, ipStr, port))
		blocks.blockList[port] = (ipStr, name)
		blockstring = ("%s%s:%i" % (name[:6], ipStr, port)).encode('utf-16le')
		struct.pack_into('%is' % len(blockstring), data, pos, blockstring)
		if len(blockstring) < 0x40:
			struct.pack_into('%ix' % (0x40 - len(blockstring)), data, pos + len(blockstring))
		struct.pack_into('BBBB', data, pos+0x40, int(i0), int(i1), int(i2), int(i3))
		pos += 0x88

	return str(data)


@packetHandler(0x11, 0x13)
def blockQueryResponse(context, data):
	data = bytearray(data)
	struct.pack_into('BBBB', data, 0x14, int(i0), int(i1), int(i2), int(i3))
	print("[ShipProxy] rewriting block ip address in query response.")
	return str(data)


@packetHandler(0xF, 0xD)
def playerInfoPacket(context, data):
	pId = struct.unpack_from('I', data, 0x8)[0] # TUPLESSS
	if context.peer.playerId is None:
		context.peer.playerId = pId
	return data

@packetHandler(0x1c, 0x1f)
def playerNamePacket(context, data):
	pId = struct.unpack_from('I', data, 0xC)[0]
	if pId not in players.playerList:
		pName = data[0x14:0x56].decode('utf-16')
		print("[PlayerData] Found new player %s with player ID %i" % (pName, pId))
		players.playerList[pId] = (pName,) # For now
	return data
