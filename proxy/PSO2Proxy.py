#!/usr/bin/python

from twisted.internet import protocol, reactor, stdio
from twisted.protocols import basic
from twisted.python import log, logfile
from twisted.internet.endpoints import TCP4ServerEndpoint
from commands import commandList
from PSOCryptoUtils import PSO2RC4
import packetUtils, io, struct, time, bans, calendar, datetime, os, exceptions, sys, packets, traceback
import data.blocks as blocks
import data.ships as ships
import data.clients as clients
import plugins.plugins as pManager
from queryProtocols import BlockScraperFactory, ShipAdvertiserFactory
from config import packetLogging as logPackets
from config import myIpAddr as myIp
from config import bindIp as ifaceIp
from config import noisy as verbose
from config import webapi as webapi 

class ShipProxy(protocol.Protocol):
	peer = None
	psoClient = False
	bufPacket = None

	loaded = False
	changingBlocks = False

	connTimestamp = None
	playerId = None
	myUsername = None
	packetCount = 0
	readBuffer = ''
	c4crypto = None
	orphans = []

	def setPeer(self, peer):
		self.peer = peer

	def setIsClient(self, isclient):
		self.psoClient = isclient

	def connectionLost(self, reason):
		if self.peer is not None:
			self.peer.transport.loseConnection()
			self.peer = None
		if self.playerId is not None and not self.changingBlocks:
			clients.removeClient(self)
		if self.playerId is not None and self.psoClient:
			for f in pManager.onConnectionLossHook:
				f(self)
		if self.psoClient and self.myUsername is not None:
			if self.changingBlocks:
				print("[ShipProxy] %s is changing blocks." % self.myUsername)
			else:
				print("[ShipProxy] %s logged out." % self.myUsername)
		elif self.psoClient and self.myUsername is None:
			print("[ShipProxy] Client at %s lost connection." % self.transport.getPeer().host)

	def sendCryptoPacket(self, data):
		if self.c4crypto is not None and self.peer is not None:
			if logPackets: 
				with open('packets/%i.constucted.%s.bin' % (self.packetCount, self.transport.getPeer().host), 'wb') as f:
					f.write(data)
			if verbose:
				print("[ShipProxy] Sending %s a constucted packet..." % self.transport.getPeer().host)
			data = self.peer.c4crypto.encrypt(data)
			self.transport.write(data)


	def dataReceived(self, data):
		if verbose: print("[ShipProxy] [%i] Received data from %s!" % (self.packetCount, self.transport.getPeer().host,))

		encryptionEnabled = (self.c4crypto is not None)
		if encryptionEnabled:
			data = self.c4crypto.decrypt(data)
		self.readBuffer += data

		while len(self.readBuffer) >= 8:
			packetSize = struct.unpack_from('i', self.readBuffer)[0]
			packetType = struct.unpack_from('BB', self.readBuffer, 4)
			if verbose: print("[ShipProxy] [%i] Received packet with size %i, id %x:%x" % (self.packetCount, packetSize, packetType[0], packetType[1]))

			if len(self.readBuffer) < packetSize:
				if verbose: print("[ShipProxy] [%i] Buffer only contains %i, waiting for more data." % (self.packetCount, len(self.readBuffer)))
				break

			packet = self.readBuffer[:packetSize]
			self.readBuffer = self.readBuffer[packetSize:]
			if logPackets:
				if self.myUsername is not None:
					path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (self.myUsername, self.connTimestamp, self.packetCount, packetType[0], packetType[1], self.transport.getPeer().host)
					try:
						os.makedirs(os.path.dirname(path))
					except exceptions.OSError:
						pass
					with open(path, 'wb') as f:
						f.write(packet)
				else:
					#path = 'packets/orphan_packets/%s/%i.%x-%x.%s.bin' % (self.connTimestamp, self.packetCount, packetType[0], packetType[1], self.transport.getPeer().host)
					self.orphans.append({'data' : packet, 'count' : self.packetCount, 'type' : packetType[0], "sub" : packetType[1]})

			try:
				packet = packets.packetList[packetType](self, packet)
			except KeyError:
				if verbose: print("[ShipProxy] No packet function for id %x:%x, using default functionality..." % (packetType[0], packetType[1]))

			if (packetType[0], packetType[1]) in pManager.packetFunctions:
				for f in pManager.packetFunctions[(packetType[0], packetType[1])]:
					packet = f(self, packet)

			if packet is None:
				return

			if self.playerId is not None:
				if self.playerId not in clients.connectedClients: #Inital add
					clients.addClient(self)
					self.loaded = True
					for f in pManager.onConnectionHook:
        					f(self)
				elif self.loaded == False:
					clients.populateData(self)
					for f in pManager.onConnectionHook:
        					f(self)
			if logPackets:
				if self.myUsername is not None and len(self.orphans) > 0:
					count = 0
					while len(self.orphans) > 0:
						oPacket = self.orphans.pop()
						path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (self.myUsername, self.connTimestamp, oPacket['count'], oPacket['type'], oPacket['sub'], self.transport.getPeer().host)
						try:
							os.makedirs(os.path.dirname(path))
						except exceptions.OSError:
							pass
						with open(path, 'wb') as f:
							f.write(oPacket['data'])
						count += 1
					print('[ShipProxy] Flushed %i orphan packets for %s.' % (count, self.myUsername))

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
		print("[ShipProxy] Connected to block server!")
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
		print("[ShipProxy] Connection to server failed... %s" % (reason, ))
		self.server.transport.loseConnection()

class ProxyServer(ShipProxy):

    reactor = None

    def connectionMade(self):
        # Don't read anything from the connecting client until we have
        # somewhere to send it to.
        self.transport.pauseProducing()
        print("[ShipProxy] New client connected!")
        port = self.transport.getHost().port
        print("[ShipProxy] Client is looking for block on port %i..." % port)
        if port not in blocks.blockList:
        	print("[ShipProxy] Could not find a block for port %i in the cache! Defaulting to block 5..." % port)
        	port = 12205
        	addr = "210.189.208.21"
        else:
        	print("[ShipProxy] Found address %s for port %i, named %s" % (blocks.blockList[port][0], port, blocks.blockList[port][1]))
        	addr = blocks.blockList[port][0]
        self.setIsClient(True)
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
		try:
			command = line.split(' ')[0]
			if command in commandList:
				commandList[command](self, line)
		except:
			e = traceback.format_exc()
			print("[ShipProxy] Error Occured: %s" % e)
		self.transport.write('>>> ')
		
def main():
	global ifaceIp
	logFile = logfile.LogFile.fromFullPath('log/serverlog.log')
	log.addObserver(log.FileLogObserver(logFile).emit)
	print("===== PSO2Proxy v0 GIT =====")
	timestring = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
	print("[ServerStart] Trying to start server at %s" % timestring)
	if myIp == "0.0.0.0":
		print("==== ERROR 001 ====")
		print("You have NOT configured the IP address for PSO2Proxy!")
		print("Please edit cfg/pso2proxy.config.json and change myIpAddr to your IP public IP address (Not LAN address if you're on a LAN!) ")
		print("After you fix this, please restart PSO2Proxy.")
		sys.exit(0)
		return
	if ifaceIp == "0.0.0.0":
		ifaceIp = myIp

	if not os.path.isfile("keys/myKey.pem"):
		print("==== ERROR 002 ====")
		print("You do NOT have your local RSA private key installed to 'keys/myKey.pem'!")
		print("Please see README.md's section on RSA keys for more information.")
		print("After you fix this, please restart PSO2Proxy.")
		sys.exit(0)
		return
	
	if not os.path.isfile("keys/SEGAKey.pem"):
		print("==== ERROR 003 ====")
		print("You do NOT have a SEGA RSA public key installed to 'keys/SEGAKey.pem'!")
		print("Please see README.md's section on RSA keys for more information.")
		print("After you fix this, please restart PSO2Proxy.")
		sys.exit(0)
		return

	for shipNum in xrange(0, 10):
		qEndpoint = TCP4ServerEndpoint(reactor, 12000 + (100 * shipNum), interface=ifaceIp)
		qEndpoint.listen(BlockScraperFactory())
		sEndpoint = TCP4ServerEndpoint(reactor, 12099 + (100 * shipNum), interface=ifaceIp)
		sEndpoint.listen(ShipAdvertiserFactory())
		print("[ShipProxy] Bound port %i for ship %i query server!" % ((12000 + (100 * shipNum)), shipNum))
		bound = 0
		for blockNum in xrange(1,99):
			endpoint = TCP4ServerEndpoint(reactor, 12000 + (shipNum * 100) + blockNum, interface=ifaceIp)
			endpoint.listen(ProxyFactory())
			bound += 1
		print("[ShipProxy] Bound to %i ports for all blocks on ship %i!" % (bound, shipNum))
	bans.loadBans()
	stdio.StandardIO(ServerConsole())
	print("[ShipProxy] Loading plugins...")
	import glob
	for plug in glob.glob("plugins/*.py"):
		plug = plug[:-3]
		plug = plug.replace('/','.')
		print("[ShipProxy] Importing %s..." % plug)
		__import__(plug)
	for f in pManager.onStart:
		f()
	reactor.run()

if __name__ == "__main__":
	main()
