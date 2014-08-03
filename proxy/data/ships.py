import socket
import io
import struct
import time
from threading import Thread

from twisted.python import log

import blocks


shipList = {
    12100: "210.189.208.1",
    12200: "210.189.208.16",
    12300: "210.189.208.31",
    12400: "210.189.208.46",
    12500: "210.189.208.61",
    12600: "210.189.208.76",
    12700: "210.189.208.91",
    12800: "210.189.208.106",
    12900: "210.189.208.121",
    12000: "210.189.208.136",
}


class BlockScrapingManager(object):
    def __init__(self):
        global shipList
        self.lines = {}
        for port, address in shipList.iteritems():
            self.lines[port] = BlockLine(address, port)
            self.lines[port].start()
            self.shuttingDown = False

    def get_in_line(self, ship_ip, ship_port, destination_ip):
        line = self.lines[ship_port]
        identifier = line.get_next_identifier()
        line.requests.append({'identifier': identifier, 'shipIp': ship_ip, 'shipPort': ship_port, 'dstIp': destination_ip})
        print("[BlockLine] Request #%i got in line." % identifier)
        while identifier not in line.results:
            time.sleep(1)
            if self.shuttingDown:
                line.requests.remove({'identifier': identifier, 'shipIp': ship_ip, 'shipPort': ship_port, 'dstIp': destination_ip})
                return None
        prize = line.results[identifier]
        print("[BlockLine] Request #%i got their prize." % identifier)
        del line.results[identifier]
        return prize

    def close_lines(self):
        for line in self.lines:
            self.lines[line].active = False
            self.shuttingDown = True


class BlockLine(Thread):
    def __init__(self, address, port):
        super(BlockLine, self).__init__()
        self.address = address
        self.port = port
        print("[Line] Created line for port %i" % port)

        self.bCount = 0
        self.lB = 0
        self.requests = []
        self.results = {}
        self.identifier = 0
        self.active = True

    def run(self):
        print("[BlockLine] Thread for port %i started." % self.port)
        while self.active:
            if not self.active:
                return
            if self.lB >= 60 and self.bCount > 0:
                self.bCount = 0
                self.lB = 0
                print("[BlockLine] [%i] Re-enabled burst mode early." % self.port)
            if len(self.requests) > 0:
                current_request = self.requests.pop(0)
                # print("[BlockLine] [%i] Starting on request #%i" % (self.port, currReq['identifier']))
                data = None
                try:
                    data = scrape_block_packet(current_request['shipIp'], current_request['shipPort'], current_request['dstIp'])
                except:
                    pass
                self.results[current_request['identifier']] = data
                print("[BlockLine] [%i] Finished request #%i!" % (self.port, current_request['identifier']))
                self.bCount += 1
                if self.bCount > 5:
                    print("[BlockLine] [%i] Burst complete, waiting 1min. (%i left in line.)" % (
                        self.port, len(self.requests)))
                    for x in xrange(1, 60):
                        time.sleep(1)
                        if not self.active:
                            return
                    self.bCount = 0
            else:
                time.sleep(.1)
                if self.bCount > 0:
                    self.lB += .1

        print("[BlockLine] Thread for port %i ended." % self.port)

    def get_next_identifier(self):
        self.identifier += 1
        return self.identifier


def scrape_block_packet(ship_ip, ship_port, destination_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.msg("[BlockQuery] Scraping %s:%i for a initial block..." % (ship_ip, ship_port))
    s.connect((ship_ip, ship_port))
    data = io.BytesIO()
    data.write(s.recv(4))
    actual_size = struct.unpack_from('i', data.getvalue(), 0x0)[0]
    data.write(s.recv(actual_size - 4))
    s.close()
    data.flush()
    data = bytearray(data.getvalue())
    name = data[0x24:0x64].decode('utf-16le')
    o1, o2, o3, o4, port = struct.unpack_from('BBBBH', buffer(data), 0x64)
    ip_string = '%i.%i.%i.%i' % (o1, o2, o3, o4)
    if port not in blocks.blockList:
        log.msg("[BlockList] Discovered new block %s at addr %s:%i! Recording..." % (name, ip_string, port))
        blocks.blockList[port] = (ip_string, name)
    o1, o2, o3, o4 = destination_ip.split(".")
    struct.pack_into('BBBB', data, 0x64, int(o1), int(o2), int(o3), int(o4))
    return str(data)


manager = BlockScrapingManager()


def scrape_ship_packet(ship_ip, ship_port, destination_ip):
    o1, o2, o3, o4 = destination_ip.split(".")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.msg("[ShipQuery] Scraping %s:%i for ship status..." % (ship_ip, ship_port))
    s.connect((ship_ip, ship_port))
    data = io.BytesIO()
    data.write(s.recv(4))
    actual_size = struct.unpack_from('i', data.getvalue(), 0x0)[0]
    data.write(s.recv(actual_size - 4))
    s.close()
    data.flush()
    data = bytearray(data.getvalue())
    # Hardcoded ship count, fix this!
    pos = 0x10
    for x in xrange(1, 10):
        struct.pack_into('BBBB', data, pos + 0x20, int(o1), int(o2), int(o3), int(o4))
        pos += 0x34
    return str(data)
