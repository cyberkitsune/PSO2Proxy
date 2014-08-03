from twisted.internet import protocol, reactor, threads
import data.ships as ships
from config import myIpAddr
from twisted.python import log


class BlockScraper(protocol.Protocol):
    def connectionMade(self):
        port = self.transport.getHost().port
        print('[BlockQuery] %s:%i wants to load-balance on port %i!' % (
        self.transport.getPeer().host, self.transport.getPeer().port, port))
        if port in ships.shipList:
            d = threads.deferToThread(ships.manager.getInLine, ships.shipList[port], port, myIpAddr)
            d.addCallback(self.gotShip)
        else:
            self.transport.loseConnection()

    def gotShip(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class BlockScraperFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return BlockScraper()


class ShipAdvertiser(protocol.Protocol):
    def connectionMade(self):
        print("[ShipStatus] Client connected " + str(self.transport.getPeer()) + "! Sending ship list packet...")
        self.transport.write(ships.scrapeShipPacket("210.189.208.1", 12199, myIpAddr))
        self.transport.loseConnection()


class ShipAdvertiserFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return ShipAdvertiser()

		
