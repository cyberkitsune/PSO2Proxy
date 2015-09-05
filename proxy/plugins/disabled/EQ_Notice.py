# -*- coding: utf-8 -*-
from commands import Command
import config
import data.clients as clients
from datetime import datetime
import json
import os.path
import packetFactory
import plugins
from pprint import pformat
from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import task
from twisted.python import log
from twisted.web.client import Agent
from twisted.web.client import RedirectAgent
from twisted.web.http_headers import Headers


try:
    import GlobalChat
    useGlobalChat = True
except ImportError:
    useGlobalChat = False

try:
    from twisted.web.client import readBody
except ImportError:
    class SimpleBodyProtocol(protocol.Protocol):
        def __init__(self, status, message, deferred):
            self.deferred = deferred
            self.dataBuffer = []

        def dataReceived(self, data):
            self.dataBuffer.append(data)

        def connectionLost(self, reason):
            self.deferred.callback(b''.join(self.dataBuffer))

    def readBody(response):
        d = defer.Deferred()
        response.deliverBody(SimpleBodyProtocol(response.code, response.phrase, d))
        return d

try:
    from twisted.web.client import HTTPConnectionPool
    pool = HTTPConnectionPool(reactor)
    pool._factory.noisy = False
    agent = RedirectAgent(Agent(reactor, pool=pool))
except ImportError:
    agent = RedirectAgent(Agent(reactor))

eqnotice_config = config.YAMLConfig("cfg/EQ_Notice.config.yml", {'enabled': True, 'timer': 60, 'debug': False, '1': "http://acf.me.uk/Public/PSO2EQ/pso2eq.txt"}, True)

# HTTP Headers
ETag_Headers     = ['', '', '', '', '', '', '', '', '', '']
Modified_Headers = ['', '', '', '', '', '', '', '', '', '']
# HTTP Modified in time
Modified_time    = ['', '', '', '', '', '', '', '', '', '']
# HTTP Data
HTTP_Data        = ['', '', '', '', '', '', '', '', '', '']
# was "【1時間前】" in the data?
ishour_eq        = [False, False, False, False, False, False, False, False, False, False]
# Hour of EQ
hour_eq          = ['', '', '', '', '', '', '', '', '', '']
# Mins of EQ
mins_eq          = ['', '', '', '', '', '', '', '', '', '']
# EQ Data
data_eq          = ['', '', '', '', '', '', '', '', '', '']
# EQ Data
msg_eq           = ['', '', '', '', '', '', '', '', '', '']

eqJP             = []
taskrun          = []

eq_mode = eqnotice_config.get_key('enabled')
tasksec = eqnotice_config.get_key('timer')
debug = eqnotice_config.get_key('debug')


def logdebug(message):
    if debug:
        print ("[EQ Notice Debug] %s" % message)


def load_eqJP_names():
    global eqJP
    RESloaded = False
    if os.path.exists("cfg/eqJP_custom.resources.json"):
        RESloaded = True
        f = open("cfg/eqJP_custom.resources.json", 'r')
        try:
            eqJP = json.load(f, "utf-8")
        except ValueError:
            print ("[EQ Notice] Bad custom resource file, falling back")
            RESloaded = False
        f.close()
    if not RESloaded and os.path.exists("cfg/eqJP.resources.json"):
        f = open("cfg/eqJP.resources.json", 'r')
        try:
            eqJP = json.load(f, "utf-8")
        except ValueError:
            print ("[EQ Notice] Bad resources file, blank mapping")
        f.close()
    if not eqJP:
        return
    for ship in config.globalConfig.get_key('enabledShips'):
        eqJPd = eqJP.get(data_eq[ship])
        if eqJPd:  # Is there a mapping?
            msg_eq[ship] = "%s (JP: %s@%s:%s JST)" % (eqJPd, data_eq[ship], hour_eq[ship], mins_eq[ship])
        else:
            msg_eq[ship] = "JP: %s@%s:%s JST" % (data_eq[ship], hour_eq[ship], mins_eq[ship])


def cutup_EQ(message, ship=0):
    cutstr = u"分【PSO2】"
    cutlen = message.rfind(cutstr)
    if (cutlen is not -1):
        message = message[cutlen + 7:len(message)]
    return message


def ishour_EQ(message):
    # Notices do have this string anymore
    return True
    hourstr = u"【1時間前】 Ship"
    if message.find(hourstr) is not -1:
        return True
    return False


def findhour_EQ(message):
    hrstr = u"時"
    hridx = message.rfind(hrstr)
    if hridx is -1:
        return ""
    return message[hridx - 2:hridx]


def findmins_EQ(message):
    hrstr = u"分"
    hridx = message.find(hrstr)
    if hridx is -1:
        return ""
    return message[hridx - 2:hridx]


def cleanup_EQ(message, ship):  # 0 is ship1
    ishour_eq[ship] = ishour_EQ(message)
    hour_eq[ship] = findhour_EQ(message)
    mins_eq[ship] = findmins_EQ(message)
    return cutup_EQ(message).rstrip("\n")


def old_seconds(td):
    return td.seconds + td.days * 24 * 3600


def check_if_EQ_old(ship):
    if not Modified_Headers[ship]:
        return False
    timediff = (datetime.utcnow() - Modified_time[ship])
    if ishour_eq[ship]:
        if old_seconds(timediff) > 55 * 60:
            return True
    else:
        return True
    return False


def EQBody(body, ship):  # 0 is ship1
    unibody = unicode(body, 'utf-8-sig', 'replace')
    if not unibody.strip() or unibody.strip() == "null":
        logdebug("Ship %d: no data, clearing EQ data" % (ship + 1))
        data_eq[ship] = None
        return
    logdebug("Ship %d's Body: %s" % (ship + 1, unibody))
    if HTTP_Data[ship] == body:
        logdebug("Ship %d: Still have the same data" % (ship + 1))
        return  # same data, do not react on it
    logdebug("Ship %d: have the new data" % (ship + 1))
    HTTP_Data[ship] = body

    data_eq[ship] = cleanup_EQ(unibody, ship)

    logdebug("Ship %d: %s@%s:%s JST" % (ship + 1, data_eq[ship], hour_eq[ship], mins_eq[ship]))

    logdebug("Time  : %s" % (datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')))
    logdebug("Ship %d: %s" % (ship + 1, Modified_Headers[ship]))

    old_eq = check_if_EQ_old(ship)
    if old_eq:
        logdebug("Ship %d EQ is old" % (ship + 1))
        return
    logdebug("Ship %d: EQ is new" % (ship + 1))

    load_eqJP_names()  # Reload file

    print("[EQ Notice] Sending players MSG on Ship %02d : %s" % (ship + 1, msg_eq[ship]))
    SMPacket = packetFactory.SystemMessagePacket("[Proxy] Incoming EQ Report from PSO2es: %s" % (msg_eq[ship]), 0x0).build()
    if useGlobalChat:
        if GlobalChat.ircMode and GlobalChat.ircBot is not None:
            msg = "[EQ Notice Ship %02d] Incoming EQ Report from PSO2es: %s" % (ship + 1, msg_eq[ship])
            GlobalChat.ircBot.send_channel_message(msg.encode('utf-8'))
    for client in clients.connectedClients.values():
        try:
            chandle = client.get_handle()
            if chandle is not None and client.preferences.get_preference('eqnotice') and ship == (client.preferences.get_preference('eqnotice_ship') - 1):
                chandle.send_crypto_packet(SMPacket)
        except AttributeError:
            logdebug("Ship %d: Got a dead client, skipping" % (ship + 1))


def EQResponse(response, ship=-1):  # 0 is ship1
    if response.code == 304:
        return
    logdebug("Ship %d: HTTP Status %d" % (ship + 1, response.code))
    if response.code != 200:
        return
    logdebug("Ship %d: Checking URL Headers" % (ship + 1))
    logdebug(pformat(list(response.headers.getAllRawHeaders())))
    if response.headers.hasHeader('ETag'):
        ETag_Headers[ship] = response.headers.getRawHeaders('ETag')[0]
    else:
        ETag_Headers[ship] = None
    if response.headers.hasHeader('Last-Modified'):
        Modified_Headers[ship] = response.headers.getRawHeaders('Last-Modified')[0]
        Modified_time[ship] = datetime.strptime(Modified_Headers[ship], "%a, %d %b %Y %H:%M:%S %Z")
    else:
        Modified_Headers[ship] = None
        Modified_time[ship] = None
    d = readBody(response)
    d.addCallback(EQBody, ship)
    d.addErrback(log.err)
    return d


def CheckupURL():
    HTTPHeader0 = Headers({'User-Agent': ['PSO2Proxy']})
    load_eqJP_names()  # Reload file
    for shipNum in config.globalConfig.get_key('enabledShips'):
        if eqnotice_config.key_exists(str(shipNum)):
            eq_URL = eqnotice_config.get_key(str(shipNum))
        else:
            eq_URL = None
        if eq_URL:
            HTTPHeaderX = HTTPHeader0.copy()
            if ETag_Headers[shipNum]:
                HTTPHeaderX.addRawHeader('If-None-Match', ETag_Headers[shipNum])
            if Modified_Headers[shipNum]:
                HTTPHeaderX.addRawHeader('If-Modified-Since', Modified_Headers[shipNum])
            EQ0 = agent.request('GET', eq_URL, HTTPHeaderX)
            EQ0.addCallback(EQResponse, shipNum)
            EQ0.addErrback(log.err)


@plugins.on_start_hook
def on_start():
    global taskrun
    taskrun = task.LoopingCall(CheckupURL)
    try:
        pool.cachedConnectionTimeout = (tasksec / 2) + tasksec + 1
        pool.retryAutomatically = False
    except Exception as e:
        print("[EQ Notice] No pool, please update Twisted, %s" % e)

    if eq_mode:
        taskrun.start(tasksec)  # call every 60 seconds
    else:
        print("EQ Notice is disabled by config")


@plugins.on_initial_connect_hook
def notify_and_config(client):
    """
    :type client: ShipProxy.ShipProxy
    """
    client_preferences = clients.connectedClients[client.playerId].preferences
    if not client_preferences.has_preference("eqnotice"):
        client_preferences.set_preference("eqnotice", True)
    ship = clients.get_ship_from_port(client.transport.getHost().port) - 1
    if not client_preferences.has_preference("eqnotice_ship"):
        client_preferences.set_preference("eqnotice_ship", 2)  # good default
    if ship == 10:
        ship = client_preferences.get_preference('eqnotice_ship') - 1
    else:
        client_preferences.set_preference("eqnotice_ship", (ship + 1))  # record the real ship
    if client_preferences.get_preference('eqnotice') and data_eq[ship] and not check_if_EQ_old(ship):
        SMPacket = packetFactory.SystemMessagePacket("[Proxy] Incoming EQ Report from PSO2es: %s" % (msg_eq[ship]), 0x0).build()
        client.send_crypto_packet(SMPacket)


@plugins.CommandHook("checkeq", "Redisplay of EQ notices from PSO2es sources")
class RequestEQNoitce(Command):
    def call_from_client(self, client):
        client_preferences = clients.connectedClients[client.playerId].preferences
        ship = (client_preferences.get_preference('eqnotice_ship') - 1)
        if data_eq[ship] and not check_if_EQ_old(ship):
            SMPacket = packetFactory.SystemMessagePacket("[Proxy] Incoming EQ Report from PSO2es: %s" % (msg_eq[ship]), 0x0).build()
        else:
            SMPacket = packetFactory.SystemMessagePacket("[Proxy] No new EQ Report from PSO2es", 0x0).build()
        client.send_crypto_packet(SMPacket)

    def call_from_console(self):
        try:
            args = self.args.split(' ')
            shipArg = int(args[1]) - 1
        except Exception as e:
            return("[EQ Notice] Please enter the ship number to check. %s" % e)
        if 0 <= shipArg <= 9:
            if data_eq[shipArg] and not check_if_EQ_old(shipArg):
                return("[EQ_Notice] Incoming EQ Report from PSO2es: %s" % (msg_eq[shipArg]))
            else:
                return("[EQ_Notice] No new EQ Report from PSO2es.")
        else:
            return("[EQ_Notice] Please enter a valid ship number.")


@plugins.CommandHook("eqnotice", "Toggles display of EQ notices from PSO2es sources")
class ToggleEQNoitce(Command):
    def call_from_client(self, client):
        if client.playerId in clients.connectedClients:
            user_prefs = clients.connectedClients[client.playerId].preferences
            user_prefs.set_preference('eqnotice', not user_prefs.get_preference('eqnotice'))
            if user_prefs.get_preference('eqnotice'):
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[EQ Notice] Enabled EQ notices.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[EQ Notice] Disabled EQ notices.", 0x3).build())

    def call_from_console(self):
        if taskrun.running:
            taskrun.stop()
            return "[EQ Notice] Stop EQ Notice Ticker"
        else:
            taskrun.start(tasksec)
            return "[EQ Notice] Started EQ Notice Ticker"
