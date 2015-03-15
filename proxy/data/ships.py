import blocks
from config import bindIp
from config import myIpAddress as myIp
import io
import socket
import struct
import sys
import time
from twisted.internet import endpoints
from twisted.internet import reactor
from twisted.python import log


blockShipList = {
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
    13000: "210.189.208.181",  # SHARED SHIP
}

queryShipArr = [(12199, "210.189.208.1"),
                (12299, "210.189.208.16"),
                (12399, "210.189.208.31"),
                (12499, "210.189.208.46"),
                (12599, "210.189.208.61"),
                (12699, "210.189.208.76"),
                (12799, "210.189.208.91"),
                (12899, "210.189.208.106"),
                (12999, "210.189.208.121"),
                (12099, "210.189.208.136")]
curShipIndex = 0


def get_ship_from_port(port):
    port_string = str(port)
    if int(port_string[1]) == 3:
        return 11
    ship_num = int(port_string[2])
    if ship_num == 0:
        ship_num = 10
    return ship_num

cachedBlocks = {}


def get_first_block(ship_port, destination_ip):
    if ship_port not in blockShipList:
        return None

    if ship_port not in cachedBlocks:
        cachedBlocks[ship_port] = {'time_scraped': time.time(), 'data': scrape_block_packet(blockShipList[ship_port], (ship_port if (ship_port != 13000) else 12000), destination_ip)}
        print("[BlockCache] Cached new block for ship %i, Holding onto it for 5 minutes..." % ship_port)
        return cachedBlocks[ship_port]['data']

    last_time = cachedBlocks[ship_port]['time_scraped']
    current_time = time.time()
    if current_time > last_time + (60 * 3):
        cachedBlocks[ship_port] = {'time_scraped': time.time(), 'data': scrape_block_packet(blockShipList[ship_port], (ship_port if (ship_port != 13000) else 12000), destination_ip)}
        print("[BlockCache] Cached new block for ship %i, Holding onto it for 5 minutes..." % ship_port)
    return cachedBlocks[ship_port]['data']


def get_ship_query(my_ip_address):
    global curShipIndex, queryShipArr
    ship_port, ship_address = queryShipArr[curShipIndex]
    data = scrape_ship_packet(ship_address, ship_port, my_ip_address)
    curShipIndex += 1
    if curShipIndex >= len(queryShipArr):
        curShipIndex = 0
    return data


def scrape_block_packet(ship_ip, ship_port, destination_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.msg("[BlockQuery] Scraping %s:%i for a initial block..." % (ship_ip, ship_port))
    s.settimeout(30)
    try:
        s.connect((ship_ip, ship_port))
    except socket.error as e:
        log.msg("[BlockQuery] Scraping %s:%i connect return an error: %s" % (ship_ip, ship_port, e))
        return None
    except Exception as e:
        log.msg("[BlockQuery] Scraping %s:%i connect return an error: %s" % (ship_ip, ship_port, sys.exc_info()[0]))
        return None
    data = io.BytesIO()
    try:
        data.write(s.recv(4))
    except socket.error as e:
        log.msg("[BlockQuery] Scraping %s:%i write return an error: %s" % (ship_ip, ship_port, e))
        return None
    except Exception as e:
        log.msg("[BlockQuery] Scraping %s:%i write return an error: %s" % (ship_ip, ship_port, sys.exc_info()[0]))
        return None
    actual_size = struct.unpack_from('i', data.getvalue(), 0x0)[0]
    try:
        data.write(s.recv(actual_size - 4))
    except socket.error as e:
        log.msg("[BlockQuery] Scraping %s:%i recv return an error: %s" % (ship_ip, ship_port, e))
        return None
    except Exception as e:
        log.msg("[BlockQuery] Scraping %s:%i recv return an error: %s" % (ship_ip, ship_port, sys.exc_info()[0]))
        return None
    s.close()
    data.flush()
    data = bytearray(data.getvalue())
    name = data[0x24:0x64].decode('utf-16le')
#   namelog = name.encode('ascii', errors='ignore').rstrip('\0')
    o1, o2, o3, o4, port = struct.unpack_from('BBBBH', buffer(data), 0x68)
    ip_string = '%i.%i.%i.%i' % (o1, o2, o3, o4)
    if ship_ip == blockShipList[13000]:  # Shared ship hack
        port += 1000   # Bump port up to 13000
        struct.pack_into('H', data, (0x68 + 0x04), port)
    if port not in blocks.blockList:
        # log.msg("[BlockList] Discovered new block %s at addr %s:%i! Recording..." % (namelog, ip_string, port))
        blocks.blockList[port] = (ip_string, name)
    if port not in blocks.listeningPorts:
        from ShipProxy import ProxyFactory
        if bindIp == "0.0.0.0":
            interface_ip = myIp
        else:
            interface_ip = bindIp
        block_endpoint = endpoints.TCP4ServerEndpoint(reactor, port, interface=interface_ip)
#       twisted.internet.error.CannotListenError: Couldn't listen on 0.0.0.0:12468: [Errno 98] Address already in use.
        block_endpoint.listen(ProxyFactory())
        print("[ShipProxy] Opened listen socked on port %i for new ship." % port)
        blocks.listeningPorts.append(port)
    o1, o2, o3, o4 = destination_ip.split(".")
    struct.pack_into('BBBB', data, 0x68, int(o1), int(o2), int(o3), int(o4))
    return str(data)


def scrape_ship_packet(ship_ip, ship_port, destination_ip):
    o1, o2, o3, o4 = destination_ip.split(".")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.msg("[ShipQuery] Scraping %s:%i for ship status..." % (ship_ip, ship_port))
    s.settimeout(30)
    try:
        s.connect((ship_ip, ship_port))
    except socket.error as e:
        log.msg("[ShipQuery] Scraping %s:%i connnect return an error: %s" % (ship_ip, ship_port, e))
        return None
    except Exception as e:
        log.msg("[ShipQuery] Scraping %s:%i connect return an error: %s" % (ship_ip, ship_port, sys.exc_info()[0]))
        return None
    data = io.BytesIO()
    try:
        data.write(s.recv(4))
    except socket.error as e:
        log.msg("[ShipQuery] Scraping %s:%i recv return an error: %s" % (ship_ip, ship_port, e))
        return None
    except Exception as e:
        log.msg("[ShipQuery] Scraping %s:%i recv return an error: %s" % (ship_ip, ship_port, sys.exc_info()[0]))
        return None
    actual_size = struct.unpack_from('i', data.getvalue(), 0x0)[0]
    try:
        data.write(s.recv(actual_size - 4))
    except socket.error as e:
        log.msg("[ShipQuery] Scraping %s:%i write return an error: %s" % (ship_ip, ship_port, e))
        return None
    except Exception as e:
        log.msg("[ShipQuery] Scraping %s:%i wrtie return an error: %s" % (ship_ip, ship_port, sys.exc_info()[0]))
        return None
    s.close()
    data.flush()
    data = bytearray(data.getvalue())
    # Hardcoded ship count, fix this!
    pos = 0x10
    for x in xrange(1, 10):
        struct.pack_into('BBBB', data, pos + 0x20, int(o1), int(o2), int(o3), int(o4))
        pos += 0x34
    return str(data)
