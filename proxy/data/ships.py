import socket
import io
import struct
import time

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

cachedBlocks = {}


def get_first_block(ship_port, destination_ip):
    if ship_port not in shipList:
        return None

    if ship_port not in cachedBlocks:
        cachedBlocks[ship_port] = {'time_scraped': time.time(), 'data': scrape_block_packet(shipList[ship_port], ship_port, destination_ip)}
        print("[BlockCache] Cached new block for ship %i, Holding onto it for a minute..." % ship_port)
        return cachedBlocks[ship_port]['data']

    last_time = cachedBlocks[ship_port]['time_scraped']
    current_time = time.time()
    if current_time > last_time + 60:
        cachedBlocks[ship_port] = {'time_scraped': time.time(), 'data': scrape_block_packet(shipList[ship_port], ship_port, destination_ip)}
        print("[BlockCache] Cached new block for ship %i, Holding onto it for a minute..." % ship_port)
    return cachedBlocks[ship_port]['data']


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
