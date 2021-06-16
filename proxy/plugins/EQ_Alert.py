# -*- coding: utf-8 -*-
from commands import Command
import config
import data.clients as clients
from datetime import datetime
import json
import packetFactory
import plugins.proxyplugins as plugins
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

eqalert_config = config.YAMLConfig(
    "cfg/EQ_Alert.config.yml",
    {
        'enabled': True,
        'timer': 80,
        'debug': False,
        'api': "http://pso2.acf.me.uk/api/eq.json",
        '0': True, '1': True, '2': True, '3': True, '4': True,
        '5': True, '6': True, '7': True, '8': True, '9': True,
        'ircShip': 1, 'User-Agent': "PSO2Proxy"
    },
    True
)

# HTTP Headers
ETag_Header = ""
Modified_Header = ""
# HTTP Modified in time
Modified_time = ""
# HTTP Data
HTTP_Data = ""
# Hour of EQ
hour_eq = ['', '', '', '', '', '', '', '', '', '']
# EQ Data
data_eq = ['', '', '', '', '', '', '', '', '', '']

taskrun = []

eq_mode = eqalert_config['enabled']
tasksec = eqalert_config['timer']
debug = eqalert_config['debug']


def logdebug(message):
    if debug:
        print ("[EQ Alert Debug] %s" % message)


def EQBody(body):  # 0 is ship1
    try:
        APIData = json.loads(str(body.decode("utf-8")))
    except Exception as e:  # If we can't load a JSON then something went wrong with the API
        print("[EQ Alert] Bad API response, %s" % e)
        return

    try:
        APIResponse = APIData[0]
    except Exception as e:
        logdebug("Falling back")
        APIResponse = APIData

    global HTTP_Data

    if HTTP_Data == APIResponse:
        logdebug("API data has not changed.")
        return  # Don't do anything if the data hasn't changed
    logdebug("New data from API.")
    HTTP_Data = APIResponse

    for ship in config.globalConfig['enabledShips']:
        if eqalert_config.key_exists(str(ship)):

            try:
                hour_eq[ship] = APIResponse['JST']
            except Exception as e:
                print("[EQ Alert] Unable to get data, %s" % e)
                return

            try:  # We need to check these in the proper order
                if not APIResponse['Ship' + str(ship + 1)] == "":  # Check the Ship first
                    data_eq[ship] = APIResponse['Ship' + str(ship + 1)] + " at " + hour_eq[ship] + " JST."
                elif not APIResponse['HalfHour'] == "":  # Check what's coming at :30 next
                    data_eq[ship] = APIResponse['HalfHour'] + " at half past."
                elif not APIResponse['OneLater'] == "":  # Check responses for all ships
                    data_eq[ship] = APIResponse['OneLater'] + " at " + hour_eq[ship] + " JST."
                elif not APIResponse['TwoLater'] == "":  # Check what's coming in 2 hours
                    data_eq[ship] = APIResponse['TwoLater'] + " in two hours."
                elif not APIResponse['ThreeLater'] == "":  # Finally check what's coming in 3 hours
                    data_eq[ship] = APIResponse['ThreeLater'] + " in three hours."
                else:  # If all of the above are blank then there's no EQ for this Ship
                    data_eq[ship] = ""
            except KeyError as e:
                print("[EQ Alert] Could not find key, %s" % e)
                return
            except Exception as e:
                print("[EQ Alert] Unable to get data, %s" % e)
                return

            if not data_eq[ship] == "" and "no Emergency Quests" not in data_eq[ship]:
                logdebug("Ship %d: %s" % (ship + 1, data_eq[ship]))

                logdebug("Time  : %s" % (datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')))

                print("[EQ Alert] Sending players alert on Ship %02d : %s" % (ship + 1, data_eq[ship]))
                SMPacket = packetFactory.SystemMessagePacket("[Proxy] Incoming EQ Report: %s" % (data_eq[ship]), 0x0).build()
                if useGlobalChat:
                    if eqalert_config.key_exists('ircShip'):
                        ircShip = eqalert_config['ircShip']  # Get the Ship to send notices for on IRC
                        if GlobalChat.ircMode and GlobalChat.ircBot is not None and ship == ircShip:
                            msg = "[EQ Alert Ship %02d] Incoming EQ Report: %s" % (ship + 1, data_eq[ship])
                            GlobalChat.ircBot.send_channel_message(msg.encode('utf-8'))
                for client in clients.connectedClients.values():
                    try:
                        chandle = client.get_handle()
                        if (
                            chandle is not None and
                            client.preferences.get_preference('eqalert') and
                            ship == (client.preferences.get_preference('eqalert_ship') - 1)
                        ):
                            chandle.send_crypto_packet(SMPacket)
                    except AttributeError:
                        logdebug("Ship %d: Found a dead client, skipping" % (ship + 1))


def EQResponse(response):
    global ETag_Header
    global Modified_time
    if response.code == 304:
        return
    logdebug("HTTP Status: " + str(response.code))
    if response.code != 200:
        return
    logdebug("Checking URL Headers...")
    logdebug(pformat(list(response.headers.getAllRawHeaders())))
    if response.headers.hasHeader('ETag'):
        ETag_Header = response.headers.getRawHeaders('ETag')[0]
    else:
        ETag_Header = None
    if response.headers.hasHeader('Last-Modified'):
        Modified_Header = response.headers.getRawHeaders('Last-Modified')[0]
        Modified_time = datetime.strptime(Modified_Header, "%a, %d %b %Y %H:%M:%S %Z")
    else:
        Modified_Header = None
        Modified_time = None
    d = readBody(response)
    d.addCallback(EQBody)
    d.addErrback(log.err)
    return d


def CheckupURL():
    if eqalert_config.key_exists('User-Agent'):  # We need to send a User-Agent
        HTTPHeader0 = Headers({'User-Agent': [eqalert_config['User-Agent']]})
    else:
        HTTPHeader0 = Headers({'User-Agent': ['PSO2Proxy']})
    if eqalert_config.key_exists('api'):
        eq_URL = eqalert_config['api']
    else:
        eq_URL = None
    if eq_URL:
        HTTPHeaderX = HTTPHeader0.copy()
        if ETag_Header:
            HTTPHeaderX.addRawHeader('If-None-Match', ETag_Header)
        if Modified_Header:
            HTTPHeaderX.addRawHeader('If-Modified-Since', Modified_Header)
        EQ0 = agent.request(bytes('GET', encoding='utf8'), bytes(eq_URL, encoding='utf8'), HTTPHeaderX)
        EQ0.addCallback(EQResponse)
        EQ0.addErrback(log.err)


@plugins.on_start_hook
def on_start():
    global taskrun
    taskrun = task.LoopingCall(CheckupURL)
    try:
        pool.cachedConnectionTimeout = (tasksec / 2) + tasksec + 1
        pool.retryAutomatically = False
    except Exception as e:
        print("[EQ Alert] No pool, please update Twisted, %s" % e)

    if eq_mode:
        taskrun.start(tasksec)  # call every 60 seconds
    else:
        print("[EQ Alert] EQ Alert has been disabled in the config.")


@plugins.on_initial_connect_hook
def notify_and_config(client):
    """
    :type client: ShipProxy.ShipProxy
    """
    client_preferences = clients.connectedClients[client.playerId].preferences
    if not client_preferences.has_preference("eqalert"):
        client_preferences.set_preference("eqalert", True)
    ship = clients.get_ship_from_port(client.transport.getHost().port) - 1
    if not client_preferences.has_preference("eqalert_ship"):
        client_preferences.set_preference("eqalert_ship", 2)  # good default
    if ship == 10:
        ship = client_preferences.get_preference('eqalert_ship') - 1
    else:
        client_preferences.set_preference("eqalert_ship", (ship + 1))  # record the real ship
    if client_preferences.get_preference('eqalert') and not data_eq[ship] == "":
        SMPacket = packetFactory.SystemMessagePacket("[EQ Alert] Incoming EQ Report: %s" % (data_eq[ship]), 0x0).build()
        client.send_crypto_packet(SMPacket)


@plugins.CommandHook("checkeq", "Displays the latest EQ Alert from the API.")
class RequestEQNoitce(Command):
    def call_from_client(self, client):
        client_preferences = clients.connectedClients[client.playerId].preferences
        ship = (client_preferences.get_preference('eqalert_ship') - 1)
        if not data_eq[ship] == "":
            SMPacket = packetFactory.SystemMessagePacket("[EQ Alert] Incoming EQ Report: %s" % (data_eq[ship]), 0x0).build()
        else:
            SMPacket = packetFactory.SystemMessagePacket("[EQ Alert] There is no incoming EQ.", 0x0).build()
        client.send_crypto_packet(SMPacket)

    def call_from_console(self):
        try:
            args = self.args.split(' ')
            shipArg = int(args[1]) - 1
        except Exception as e:
            return("[EQ Alert] Please enter the ship number to check. %s" % e)
        if 0 <= shipArg <= 9:
            if not data_eq[shipArg] == "":
                return("[EQ Alert] Incoming EQ Report: %s" % (data_eq[shipArg]))
            else:
                return("[EQ Alert] There is no incoming EQ.")
        else:
            return("[EQ Alert] Please enter a valid ship number.")


@plugins.CommandHook("eqalert", "Toggles whether EQ alerts will be displayed.")
class ToggleEQNoitce(Command):
    def call_from_client(self, client):
        if client.playerId in clients.connectedClients:
            user_prefs = clients.connectedClients[client.playerId].preferences
            user_prefs.set_preference('eqalert', not user_prefs.get_preference('eqalert'))
            if user_prefs.get_preference('eqalert'):
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[EQ Alert] Enabled EQ alerts.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[EQ Alert] Disabled EQ alerts.", 0x3).build())

    def call_from_console(self):
        if taskrun.running:
            taskrun.stop()
            return "[EQ Alert] Stopped EQ Alert Ticker."
        else:
            taskrun.start(tasksec)
            return "[EQ Alert] Started EQ Alert Ticker."
