from twisted.internet import protocol, threads
import data.ships as ships
from config import myIpAddress
import plugins.plugins
from config import noisy as verbose


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
        d = threads.deferToThread(ships.scrape_ship_packet, "210.189.208.1", 12199, myIpAddress)
        d.addCallback(self.send_ship_list)

    def send_ship_list(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class ShipAdvertiserFactory(protocol.Factory):
    def __init__(self):
        self.noisy = verbose
        pass

    def buildProtocol(self, address):
        return ShipAdvertiser()
