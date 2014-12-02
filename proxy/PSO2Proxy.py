#!/usr/bin/python
from twisted.internet import epollreactor
epollreactor.install()

import time
import os
import sys
import traceback
import config

useFaulthandler = True
try:
    import faulthandler
except ImportError:
    useFaulthandler = False

from twisted.internet import reactor, stdio
from twisted.protocols import basic
from twisted.python import log, logfile
from twisted.internet.endpoints import TCP4ServerEndpoint

from commands import commandList
import data
import data.clients as clients
import plugins.plugins as plugin_manager
from queryProtocols import BlockScraperFactory, ShipAdvertiserFactory
from config import myIpAddress as myIp
from config import bindIp


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
    reactor.suggestThreadPoolSize(30)  # We got 2 cores, screw it!
    reactor.run()
    data.clients.dbManager.close_db()


if __name__ == "__main__":
    if not os.path.exists("log/"):
        os.makedirs("log/")
    if useFaulthandler:
        faulthandler.enable(file=open('log/tracestack.log', 'w+'), all_threads=True)
        #faulthandler.dump_traceback_later()
    main()
