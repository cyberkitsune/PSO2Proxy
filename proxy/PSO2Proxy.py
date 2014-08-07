#!/usr/bin/python

import struct
import time
import calendar
import datetime
import os
import sys
import traceback
import config

from twisted.internet import protocol, reactor, stdio
from twisted.protocols import basic
from twisted.python import log, logfile
from twisted.internet.endpoints import TCP4ServerEndpoint

from commands import commandList
import packets
import data.blocks as blocks
import data.clients as clients
import plugins.plugins as plugin_manager
from queryProtocols import BlockScraperFactory, ShipAdvertiserFactory
from config import myIpAddress as myIp
from config import bindIp
from config import noisy as verbose  # // Do this better


class ShipProxy(protocol.Protocol):
    def __init__(self):
        pass

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

    extendedData = {}

    def set_peer(self, peer):
        self.peer = peer

    def set_is_client(self, is_client):
        self.psoClient = is_client

    def connectionLost(self, reason=protocol.connectionDone):
        if self.peer is not None:
            self.peer.transport.loseConnection()
            self.peer = None
        if self.playerId is not None and not self.changingBlocks:
            for f in plugin_manager.onClientRemove:
                f(self)
            clients.remove_client(self)
        if self.playerId is not None and self.psoClient:
            for f in plugin_manager.onConnectionLoss:
                f(self)
        if self.psoClient and self.myUsername is not None:
            if self.changingBlocks:
                print("[ShipProxy] %s is changing blocks." % self.myUsername)
            else:
                print("[ShipProxy] %s logged out." % self.myUsername)
        elif self.psoClient and self.myUsername is None:
            print("[ShipProxy] Client at %s lost connection." % self.transport.getPeer().host)

    def send_crypto_packet(self, data):
        if self.c4crypto is not None and self.peer is not None:
            if verbose:
                print("[ShipProxy] Sending %s a constructed packet..." % self.transport.getPeer().host)
            data = self.peer.c4crypto.encrypt(data)
            self.transport.write(data)

    def dataReceived(self, data):
        if verbose:
            print("[ShipProxy] [%i] Received data from %s!" % (self.packetCount, self.transport.getPeer().host,))

        encryption_enabled = (self.c4crypto is not None)
        if encryption_enabled:
            data = self.c4crypto.decrypt(data)
        self.readBuffer += data

        while len(self.readBuffer) >= 8:
            packet_size = struct.unpack_from('i', self.readBuffer)[0]
            packet_type = struct.unpack_from('BB', self.readBuffer, 4)
            if verbose:
                print("[ShipProxy] [%i] Received packet with size %i, id %x:%x" % (
                    self.packetCount, packet_size, packet_type[0], packet_type[1]))

            if len(self.readBuffer) < packet_size:
                if verbose:
                    print("[ShipProxy] [%i] Buffer only contains %i, waiting for more data." % (
                        self.packetCount, len(self.readBuffer)))
                break

            packet = self.readBuffer[:packet_size]
            self.readBuffer = self.readBuffer[packet_size:]

            if packet is not None:
                for f in plugin_manager.rawPacketFunctions:
                    packet = f(self, packet, packet_type[0], packet_type[1])

            try:
                packet_handler = packets.packetList[packet_type]
                packet = packet_handler(self, packet)
            except KeyError:
                if verbose:
                    print("[ShipProxy] No packet function for id %x:%x, using default functionality..." % (
                        packet_type[0], packet_type[1]))

            if (packet_type[0], packet_type[1]) in plugin_manager.packetFunctions:
                for f in plugin_manager.packetFunctions[(packet_type[0], packet_type[1])]:
                    if packet is not None:
                        packet = f(self, packet)

            if packet is None:
                return

            if self.playerId is not None:
                if self.playerId not in clients.connectedClients:  # Inital add
                    clients.add_client(self)
                    self.loaded = True
                    for f in plugin_manager.onInitialConnection:
                        f(self)
                elif not self.loaded:
                    clients.populate_data(self)
                    for f in plugin_manager.onConnection:
                        f(self)

            if encryption_enabled:
                packet = self.c4crypto.encrypt(packet)
            else:
                # check if encryption was newly enabled while parsing this packet
                # if it was, then decrypt any packets that may be waiting in the buffer
                if self.c4crypto is not None:
                    encryption_enabled = True
                    self.readBuffer = self.c4crypto.decrypt(self.readBuffer)

            self.peer.transport.write(packet)

            self.packetCount += 1
            self.peer.packetCount = self.packetCount


class ProxyClient(ShipProxy):
    def connectionMade(self):
        self.peer.set_peer(self)
        print("[ShipProxy] Connected to block server!")
        utctime = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        self.connTimestamp = utctime
        self.peer.connTimestamp = utctime
        self.peer.transport.resumeProducing()


class ProxyClientFactory(protocol.ClientFactory):
    def __init__(self):
        self.protocol = ProxyClient
        self.server = None

    def set_server(self, server):
        self.server = server

    def buildProtocol(self, *args, **kw):
        the_protocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        the_protocol.set_peer(self.server)
        return the_protocol

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
            address = "210.189.208.21"
        else:
            print("[ShipProxy] Found address %s for port %i, named %s" % (
                blocks.blockList[port][0], port, blocks.blockList[port][1]))
            address = blocks.blockList[port][0]
        self.set_is_client(True)
        client = ProxyClientFactory()
        client.set_server(self)

        self.reactor = reactor
        self.reactor.connectTCP(address, port, client)


class ProxyFactory(protocol.Factory):
    """Factory for port forwarder."""

    def __init__(self):
        self.protocol = ProxyServer

    def buildProtocol(self, address):
        return ProxyServer()


class ServerConsole(basic.LineReceiver):
    def __init__(self):
        self.delimiter = os.linesep

    def connectionMade(self):
        self.transport.write('>>> ')

    def lineReceived(self, line):
        try:
            command = line.split(' ')[0]
            if command != "":
                if command in commandList:
                    f = commandList[command][0]
                    out = f(line).call_from_console()
                    if out is not None:
                        print(out)
                elif command in plugin_manager.commands:
                    plugin_f = plugin_manager.commands[command][0]
                    out = plugin_f(line).call_from_console()
                    if out is not None:
                        print(out)
                else:
                    print("[Command] Command %s not found!" % command)
        except:
            e = traceback.format_exc()
            print("[ShipProxy] Error Occurred: %s" % e)
        self.transport.write('>>> ')


def main():
    if not os.path.exists("log/"):
        os.makedirs("log/")
    log_file = logfile.LogFile.fromFullPath('log/serverlog.log')
    log.addObserver(log.FileLogObserver(log_file).emit)
    print("===== PSO2Proxy vGIT %s =====" % config.proxy_ver)
    time_string = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    print("[ServerStart] Trying to start server at %s" % time_string)
    if myIp == "0.0.0.0":
        print("==== ERROR 001 ====")
        print("You have NOT configured the IP address for PSO2Proxy!")
        print(
            "Please edit cfg/pso2proxy.config.yml and change myIpAddr to your IP public IP address "
            "(Not LAN address if you're on a LAN!) ")
        print("After you fix this, please restart PSO2Proxy.")
        sys.exit(0)
    if bindIp == "0.0.0.0":
        interface_ip = myIp
    else:
        interface_ip = bindIp

    if not os.path.isfile("keys/myKey.pem"):
        print("==== ERROR 002 ====")
        print("You do NOT have your local RSA private key installed to 'keys/myKey.pem'!")
        print("Please see README.md's section on RSA keys for more information.")
        print("After you fix this, please restart PSO2Proxy.")
        sys.exit(0)

    if not os.path.isfile("keys/SEGAKey.pem"):
        print("==== ERROR 003 ====")
        print("You do NOT have a SEGA RSA public key installed to 'keys/SEGAKey.pem'!")
        print("Please see README.md's section on RSA keys for more information.")
        print("After you fix this, please restart PSO2Proxy.")
        sys.exit(0)

    for shipNum in range(0, 10):  # PSO2 Checks all ships round robin, so sadly for max compatibility we have to open these no matter what ships are enabled...
        ship_endpoint = TCP4ServerEndpoint(reactor, 12099 + (100 * shipNum), interface=interface_ip)
        ship_endpoint.listen(ShipAdvertiserFactory())

    for shipNum in config.globalConfig.get_key('enabledShips'):
        query_endpoint = TCP4ServerEndpoint(reactor, 12000 + (100 * shipNum), interface=interface_ip)
        query_endpoint.listen(BlockScraperFactory())
        print("[ShipProxy] Bound port %i for ship %i query server!" % ((12000 + (100 * shipNum)), shipNum))
        bound = 0
        for blockNum in xrange(1, 99):
            endpoint = TCP4ServerEndpoint(reactor, 12000 + (shipNum * 100) + blockNum, interface=interface_ip)
            endpoint.listen(ProxyFactory())
            bound += 1
        print("[ShipProxy] Bound to %i ports for all blocks on ship %i!" % (bound, shipNum))
    stdio.StandardIO(ServerConsole())
    print("[ShipProxy] Loading plugins...")
    import glob

    for plug in glob.glob("plugins/*.py"):
        plug = plug[:-3]
        plug = plug.replace('/', '.')
        print("[ShipProxy] Importing %s..." % plug)
        __import__(plug)
    for f in plugin_manager.onStart:
        f()
    reactor.run()


if __name__ == "__main__":
    main()
