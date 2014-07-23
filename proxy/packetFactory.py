import io, struct

class Packet(object):
	"""docstring for PacketFactory"""
	def __init__(self, pId, subId, flag1, flag2, data):
		self.pId = pId
		self.subId = subId
		self.flag1 = flag1
		self.flag2 = flag2
		self.data = data
	def build(self):
		buf = bytearray()
		buf += struct.pack('i', (len(self.data) + 0x8))
		buf += struct.pack('BBBB', self.pId, self.subId, self.flag1, self.flag2)
		buf += (self.data)
		return str(buf)

class PlayerHeader(object):
	"""docstring for PlayerHeader"""
	def __init__(self, playerId=0x0, _4=0x0, _8=0x4, _A=0x0):
		self.playerId = playerId
		self._4 = _4
		self._8 = _8
		self._A = _A
	
	def build(self):
		buf = bytearray()
		buf += struct.pack('<IIHH', self.playerId, self._4, self._8, self._A)
		return buf
		
		


class ChatPacket(object):
	def __init__(self, senderId, message):
		self.senderId = senderId
		self.message = message

	def build(self):
		buf = bytearray()
		buf += PlayerHeader(self.senderId).build()
		buf += struct.pack('xx') # TODO: FIXME
		buf += struct.pack('<H', 0) # TODO: FIXME
		# Magical xor man
		charLength = len(self.message + '\0')
		xor = (charLength + 0x44) ^ 0x9D3F
		buf += struct.pack('<I', xor)
		buf += (self.message + '\0').encode('utf-16le')
		buf += struct.pack('xx') #pad!
		return Packet(0x7, 0x0, 0x44, 0x0, buf).build()



		


		