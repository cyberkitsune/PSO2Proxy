from twisted.internet import protocol, reactor, threads
import data.ships as ships
from config import myIpAddress


class BlockScraper(protocol.Protocol):
    def __init__(self):
        pass

    def connectionMade(self):
        port = self.transport.getHost().port
        print('[BlockQuery] %s:%i wants to load-balance on port %i!' % (
            self.transport.getPeer().host, self.transport.getPeer().port, port))
        if port in ships.shipList:
            d = threads.deferToThread(ships.manager.get_in_line, ships.shipList[port], port, myIpAddress)
            d.addCallback(self.got_ship)
        else:
            self.transport.loseConnection()

    def got_ship(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class BlockScraperFactory(protocol.Factory):
    def __init__(self):
        pass

    def buildProtocol(self, address):
        return BlockScraper()


class ShipAdvertiser(protocol.Protocol):
    def __init__(self):
        pass

    def connectionMade(self):
        print("[ShipStatus] Client connected " + str(self.transport.getPeer()) + "! Sending ship list packet...")
        self.transport.write(ships.scrape_ship_packet("210.189.208.1", 12199, myIpAddress))
        self.transport.loseConnection()


class ShipAdvertiserFactory(protocol.Factory):
    def __init__(self):
        pass

    def buildProtocol(self, address):
        return ShipAdvertiser()
