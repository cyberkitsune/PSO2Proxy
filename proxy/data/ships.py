import socket, io, struct, blocks

shipList = {
	12100 : "210.189.208.1",
	12200 : "210.189.208.16",
	12300 : "210.189.208.31",
	12400 : "210.189.208.46",
	12500 : "210.189.208.61",
	12600 : "210.189.208.76",
	12700 : "210.189.208.91",
	12800 : "210.189.208.106",
	12900 : "210.189.208.121",
	12000 : "210.189.208.136",
}

def scrapeBlockPacket(shipIp, shipPort, dstIp):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("[BlockQuery] Scraping %s:%i for a initial block..." % (shipIp, shipPort))
	s.connect((shipIp, shipPort))
	data = io.BytesIO()
	data.write(s.recv(4))
	realsize = struct.unpack_from('i', data.getvalue(), 0x0)[0]
	data.write(s.recv(realsize - 4))
	s.close()
	data.flush()
	data = bytearray(data.getvalue())
	name = data[0x24:0x64].decode('utf-16le')
	o1, o2, o3, o4, port = struct.unpack_from('BBBBH', buffer(data), 0x64)
	ipStr = '%i.%i.%i.%i' % (o1, o2, o3, o4)
	if port not in blocks.blockList:
		print("[BlockList] Discovered new block %s at addr %s:%i! Recording..." % (name, ipStr, port))
		blocks.blockList[port] = (ipStr, name)
	o1, o2, o3, o4 = dstIp.split(".")
	struct.pack_into('BBBB', data, 0x64, int(o1), int(o2), int(o3), int(o4))
	return str(data)

def scrapeShipPacket(shipIp, shipPort, dstIp):
	o1, o2, o3, o4 = dstIp.split(".")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("[ShipQuery] Scraping %s:%i for ship status..." % (shipIp, shipPort))
	s.connect((shipIp, shipPort))
	data = io.BytesIO()
	data.write(s.recv(4))
	realsize = struct.unpack_from('i', data.getvalue(), 0x0)[0]
	data.write(s.recv(realsize - 4))
	s.close()
	data.flush()
	data = bytearray(data.getvalue())
	#Hardcoded ship count, fix this!
	pos = 0x10
	for x in xrange(1,10):
		struct.pack_into('BBBB', data, pos+0x20, int(o1), int(o2), int(o3), int(o4))
		pos += 0x34
	return str(data)
