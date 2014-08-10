import config
import data.clients
import plugins
import packetFactory
from pprint import pformat
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers

from commands import Command

eqnotice_config = config.YAMLConfig("cfg/EQ_Notice.config.yml", {'enabled': True, 'timer' : 600, 'URL': "http://acf.me.uk/Public/PSO2EQ/pso2eq.txt" },  True)

#stored_ETag = ''
#stored_Last-Modified = ''

eq_mode = eqnotice_config.get_key('enabled')
eq_URL = eqnotice_config.get_key('URL')
tasksec = eqnotice_config.get_key('timer')

agent = Agent(reactor)

def EQBody(body, ship = 0):
    print 'Response body:'
    print body

def EQResponse(response, ship = 0):
    print 'Response version:', response.version
    print 'Response code:', response.code
    print 'Response phrase:', response.phrase
    print 'Response headers:'
    print pformat(list(response.headers.getAllRawHeaders()))
    d = readBody(response)
    d.addCallback(EQBody, 0)
    return d

def CheckupURL():
   HTTPHeader0 = Headers({'User-Agent': ['PSO2Proxy']})
#
#   if stored_ETag:
#       HTTPHeader.addRawHeader("If-None-Match", stored_ETag)
#   if stored_Last-Modified:
#       HTTPHeader.addRawHeader("If-Modified-Since", stored_Last-Modified)
#
   EQ0 = agent.request('GET', eq_URL, HTTPHeader0, None)
   EQ0.addCallback(EQResponse, 0)

@plugins.on_start_hook
def on_start():
    taskrun = task.LoopingCall(CheckupURL)
    print("!!! WARNING !!!")
    print("You have EQ_Notice.py outside of the WIP plugins folder! This means it is ON!")
    print("This plugin is still a work in progress!")
    print("Please be careful!")
    print("!!! WARNING !!!")
    if eq_mode:
        taskrun.start(tasksec) # call every 60 seconds
    else:
        print("EQ Notice is disabled by config")

@plugins.on_initial_connect_hook
def create_preferences(client):
    """
    :type client: ShipProxy
    """
    if client.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[client.playerId].preferences
        if not user_prefs.has_preference('eqnotice'):
            user_prefs.set_preference('eqnotice', True)

@plugins.CommandHook("eqnotice", "Toggles display of EQ notices from PSO2es source")
class ToggleTranslate(Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].preferences
            user_prefs.set_preference('eqnotice', not user_prefs.get_preference('eqnotice'))
            if user_prefs.get_preference('eqnotice'):
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[EQ Notice] Enabled EQ notices.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[EQ Notice] Disabled Eq notices.", 0x3).build())

    def call_from_console(self):
        if taskrun.running:
            taskrun.stop()
            print("[EQ] Stop EQ Notice Ticker")
        else:
            #stored_ETag = ""
            #stored_Last-Modified = ""
            taskrun.start(tasksec)
            print("[EQ] Started EQ Notice Ticker")
        
