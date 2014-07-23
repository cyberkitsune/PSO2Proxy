from twisted.internet import protocol, reactor, stdio
from twisted.protocols import basic
from twisted.python import log, logfile
from twisted.internet.endpoints import TCP4ServerEndpoint
from commands import commandList
from PSOCryptoUtils import PSO2RC4
import packetUtils, io, struct, time, bans, calendar, datetime, os, exceptions, sys, packets
import data.blocks as blocks
import data.ships as ships
import data.clients as clients
from queryProtocols import BlockScraperFactory, ShipAdvertiserFactory
from config import packetLogging as logPackets
from config import myIpAddr as myIp

class ShipProxy(protocol.Protocol):
	noisy = False
	peer = None
	psoClient = False
	bufPacket = None

	connTimestamp = None
	playerId = None
	myUsername = None
	packetCount = 0
	readBuffer = ''
	c4crypto = None

	def setPeer(self, peer):
		self.peer = peer

	def setIsClient(self, isclient):
		self.psoClient = isclient

	def connectionLost(self, reason):
		if self.peer is not None:
			self.peer.transport.loseConnection()
			self.peer = None
		if self.psoClient:
			clients.removeClient(self)
		if self.psoClient and self.myUsername is not None:
			log.msg("[ShipProxy] %s logged out or changed blocks." % self.myUsername)
		elif self.psoClient and self.myUsername is None:
			log.msg("[ShipProxy] Client at %s lost connection." % self.transport.getPeer().host)

	def sendCryptoPacket(self, data):
		if self.c4crypto is not None:
			if logPackets: 
				with open('packets/%i.constucted.%s.bin' % (self.packetCount, self.transport.getPeer().host), 'wb') as f:
					f.write(data)
			data = self.peer.c4crypto.encrypt(data)
			self.transport.write(data)


	def dataReceived(self, data):
		if self.noisy: log.msg("[ShipProxy] [%i] Received data from %s!" % (self.packetCount, self.transport.getPeer().host,))

		encryptionEnabled = (self.c4crypto is not None)
		if encryptionEnabled:
			data = self.c4crypto.decrypt(data)
		self.readBuffer += data

		while len(self.readBuffer) >= 8:
			packetSize = struct.unpack_from('i', self.readBuffer)[0]
			packetType = struct.unpack_from('BB', self.readBuffer, 4)
			if self.noisy: log.msg("[ShipProxy] [%i] Received packet with size %i, id %x:%x" % (self.packetCount, packetSize, packetType[0], packetType[1]))

			if len(self.readBuffer) < packetSize:
				if self.noisy: log.msg("[ShipProxy] [%i] Buffer only contains %i, waiting for more data." % (self.packetCount, len(self.readBuffer)))
				break

			packet = self.readBuffer[:packetSize]
			self.readBuffer = self.readBuffer[packetSize:]
			if logPackets and self.myUsername is not None:
				path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (self.myUsername, self.connTimestamp, self.packetCount, packetType[0], packetType[1], self.transport.getPeer().host)
				try:
					os.makedirs(os.path.dirname(path))
				except exceptions.OSError:
					pass
				with open(path, 'wb') as f:
					f.write(packet)

			try:
				packet = packets.packetList[packetType](self, packet)
			except KeyError:
				if self.noisy: log.msg("[ShipProxy] No packet function for id %x:%x, using default functionality..." % (packetType[0], packetType[1]))

			if packet is None:
				return

			if encryptionEnabled:
				packet = self.c4crypto.encrypt(packet)
			else:
				# check if encryption was newly enabled while parsing this packet
				# if it was, then decrypt any packets that may be waiting in the buffer
				if self.c4crypto is not None:
					encryptionEnabled = True
					self.readBuffer = self.c4crypto.decrypt(self.readBuffer)


			self.peer.transport.write(packet)

			self.packetCount += 1
			self.peer.packetCount = self.packetCount


class ProxyClient(ShipProxy):
	def connectionMade(self):
		self.peer.setPeer(self)
		log.msg("[ShipProxy] Connected to block server!")
		utctime = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
		self.connTimestamp = utctime
		self.peer.connTimestamp = utctime
		self.peer.transport.resumeProducing()

class ProxyClientFactory(protocol.ClientFactory):

	protocol = ProxyClient

	def setServer(self, server):
		self.server = server

	def buildProtocol(self, *args, **kw):
		prot = protocol.ClientFactory.buildProtocol(self, *args, **kw)
		prot.setPeer(self.server)
		return prot

	def clientConnectionFailed(self, connector, reason):
		log.msg("[ShipProxy] Connection to server failed... %s" % (reason, ))
		self.server.transport.loseConnection()

class ProxyServer(ShipProxy):

    reactor = None

    def connectionMade(self):
        # Don't read anything from the connecting client until we have
        # somewhere to send it to.
        self.transport.pauseProducing()
        log.msg("[ShipProxy] New client connected!")
        port = self.transport.getHost().port
        log.msg("[ShipProxy] Client is looking for block on port %i..." % port)
        if port not in blocks.blockList:
        	log.msg("[ShipProxy] Could not find a block for port %i in the cache! Defaulting to block 5..." % port)
        	port = 12205
        	addr = "210.189.208.21"
        else:
        	log.msg("[ShipProxy] Found address %s for port %i, named %s" % (blocks.blockList[port][0], port, blocks.blockList[port][1]))
        	addr = blocks.blockList[port][0]
        self.setIsClient(True)
        clients.addClient(self)

        client = ProxyClientFactory()
        client.setServer(self)

        self.reactor = reactor
        self.reactor.connectTCP(addr, port, client)


class ProxyFactory(protocol.Factory):
    """Factory for port forwarder."""

    protocol = ProxyServer

    def buildProtocol(self, addr):
    	return ProxyServer()

class ServerConsole(basic.LineReceiver):
	from os import linesep as delimiter
	
	def connectionMade(self):
		self.transport.write('>>> ')

	def lineReceived(self, line):
		command = line.split(' ')[0]
		if command in commandList:
			commandList[command](self, line)
		self.transport.write('>>> ')
		
def main():
	logFile = logfile.LogFile.fromFullPath('serverlog.log')
	log.startLogging(sys.stdout)
	log.addObserver(log.FileLogObserver(logFile).emit)
	log.msg("===== PSO2Proxy v0 GIT =====")
	timestring = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
	log.msg("[ServerStart] Trying to start server at %s" % timestring)
	if myIp == "0.0.0.0":
		log.msg("==== ERROR 001 ====")
		log.msg("You have NOT configured the IP address for PSO2Proxy!")
		log.msg("Please edit config.py and change myIpAddr to your IP public IP address (Not LAN address if you're on a LAN!) ")
		log.msg("After you fix this, please restart PSO2Proxy.")
		sys.exit(0)
		return

	if not os.path.isfile("keys/myKey.pem"):
		log.msg("==== ERROR 002 ====")
		log.msg("You do NOT have your local RSA private key installed to 'keys/myKey.pem'!")
		log.msg("Please see README.md's section on RSA keys for more information.")
		log.msg("After you fix this, please restart PSO2Proxy.")
		sys.exit(0)
		return
	
	if not os.path.isfile("keys/SEGAKey.pem"):
		log.msg("==== ERROR 003 ====")
		log.msg("You do NOT have a SEGA RSA public key installed to 'keys/SEGAKey.pem'!")
		log.msg("Please see README.md's section on RSA keys for more information.")
		log.msg("After you fix this, please restart PSO2Proxy.")
		sys.exit(0)
		return

	for shipNum in xrange(0, 10):
		qEndpoint = TCP4ServerEndpoint(reactor, 12000 + (100 * shipNum), interface=myIp)
		qEndpoint.listen(BlockScraperFactory())
		sEndpoint = TCP4ServerEndpoint(reactor, 12099 + (100 * shipNum), interface=myIp)
		sEndpoint.listen(ShipAdvertiserFactory())
		log.msg("[ShipProxy] Bound port %i for ship %i query server!" % ((12000 + (100 * shipNum)), shipNum))
		bound = 0
		for blockNum in xrange(1,99):
			endpoint = TCP4ServerEndpoint(reactor, 12000 + (shipNum * 100) + blockNum, interface=myIp)
			endpoint.listen(ProxyFactory())
			bound += 1
		log.msg("[ShipProxy] Bound to %i ports for all blocks on ship %i!" % (bound, shipNum))
	bans.loadBans()
	stdio.StandardIO(ServerConsole())
	reactor.run()

if __name__ == "__main__":
	main()
