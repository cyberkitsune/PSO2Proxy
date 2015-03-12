from config import myIpAddress
from config import noisy as verbose
import data.ships as ships
import plugins.plugins
from twisted.internet import protocol
from twisted.internet import threads


class BlockScraper(protocol.Protocol):
    def __init__(self):
        pass

    def connectionMade(self):
        port = self.transport.getHost().port
        print('[BlockQuery] %s:%i wants to load-balance on port %i!' % (self.transport.getPeer().host, self.transport.getPeer().port, port))
        d = threads.deferToThread(ships.get_first_block, port, myIpAddress)
        d.addCallback(self.send_block_scrape)
        ships.get_first_block(port, myIpAddress)

    def send_block_scrape(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class BlockScraperFactory(protocol.Factory):
    noisy = False

    def __init__(self):
        self.noisy = verbose
        pass

    def buildProtocol(self, address):
        return BlockScraper()


class ShipAdvertiser(protocol.Protocol):
    def __init__(self):
        pass

    def connectionMade(self):
        for f in plugins.plugins.onQueryConnection:
            f(self)
        print("[ShipStatus] Client connected " + str(self.transport.getPeer()) + "! Sending ship list packet...")
        d = threads.deferToThread(ships.get_ship_query, myIpAddress)
        d.addCallback(self.send_ship_list)

    def send_ship_list(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class ShipAdvertiserFactory(protocol.Factory):
    noisy = False

    def __init__(self):
        self.noisy = verbose
        pass

    def buildProtocol(self, address):
        return ShipAdvertiser()
