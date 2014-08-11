# -*- coding: utf-8 -*-

import config
import data.clients
import plugins
import packetFactory
import json
import os.path
from pprint import pformat
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from config import globalConfig

from commands import Command

eqnotice_config = config.YAMLConfig("cfg/EQ_Notice.config.yml", {'enabled': True, 'timer' : 600
,'0': ""
,'1': "http://acf.me.uk/Public/PSO2EQ/pso2eq.txt"
,'2': ""
,'3': ""
,'4': ""
,'5': ""
,'6': ""
,'7': ""
,'8': ""
,'9': ""
},  True)

#HTTP Headers
ETag_Headers     = ['','','','','','','','','','']
Modified_Headers = ['','','','','','','','','','']
#HTTP Data
HTTP_Data        = ['','','','','','','','','','']
#was "【1時間前】" in the data?
ishour_eq =          [0,0,0,0,0,0,0,0,0,0]
#Hour of EQ
hour_eq        = ['','','','','','','','','','']
#Mins of EQ
mins_eq        = ['','','','','','','','','','']
#EQ Data
data_eq        = ['','','','','','','','','','']

eqJP           = []

eq_mode = eqnotice_config.get_key('enabled')
tasksec = eqnotice_config.get_key('timer')

agent = Agent(reactor)

#Sample:	Ship02 08時00分【PSO2】第三採掘基地ダーカー接近予告
#Sample:	【1時間前】 Ship02 05時00分【PSO2】惑星リリーパ　作戦予告
#Sample:	【1時間前】 Ship02 11時00分【PSO2】旧マザーシップ　作戦予告
#Sample:	Ship02 11時00分【PSO2】旧マザーシップ　作戦予告

def load_eqJP_names():
    global eqJP
    if os.path.exists("cfg/eqJP.resources.json"):
        f = open("cfg/eqJP.resources.json", 'r')
        eqJP = json.load(f, "utf-8")
        f.close()


def cutup_EQ(message, ship = 0):
    cutstr = u"分【PSO2】"
    cutlen = message.rfind(cutstr)
    if (cutlen is not -1):
       message = message[cutlen+7:len(message)]
    return message

def ishour_EQ(message):
    hourstr = u"【1時間前】 Ship"
    if message.find(hourstr) is not -1:
        return 1
    return 0

def findhour_EQ(message):
    hrstr = u"時"
    hridx = message.find(hrstr)
    if hridx is -1:
       return ""
    return message[hridx-2:hridx]

def findmins_EQ(message):
    hrstr = u"分"
    hridx = message.find(hrstr)
    if hridx is -1:
       return ""
    return message[hridx-2:hridx]

def cleanup_EQ(message, ship): # 0 is ship1
    ishour_eq[ship] = ishour_EQ(message)
    hour_eq[ship] = findhour_EQ(message)
    mins_eq[ship] = findmins_EQ(message)
    return cutup_EQ(message).rstrip("\n")

def EQBody(body, ship): # 0 is ship1
    if HTTP_Data[ship] == body:
       return; # same data, do not react on it
    HTTP_Data[ship] == body

    data_eq[ship] = cleanup_EQ(unicode(body, 'utf-8-sig', 'replace'), ship)

    load_eqJP_names() # Reload file
    eqJPd = dict(eqJP).get(data_eq[ship])
    if eqJPd is not None: # Is there a mapping?
        msg = u'{} (JP: {}@{}:{} JST)'.format(eqJPd, data_eq[ship], hour_eq[ship], mins_eq[ship])
    else:
        msg = u'JP: {}@{}:{} JST'.format(data_eq[ship], hour_eq[ship], mins_eq[ship])

    print("[EQ_Notice] Ship %02d : %s" % (ship+1, msg))
    SMPacket = packetFactory.SystemMessagePacket("[EQ_Notice] %s" % (msg), 0x0).build()
    for client in data.clients.connectedClients.values():
       if client.preferences.get_preference('eqnotice') and client.get_handle() is not None and (ship == 0 or ship == data.clients.get_ship_from_port(cleint.transport.getHost().port)):
           client.get_handle().send_crypto_packet(SMPacket)

def EQResponse(response, ship = -1): # 0 is ship1
    #print pformat(list(response.headers.getAllRawHeaders()))
    if response.code != 200:
       return
    #print response.code
    if response.headers.hasHeader('ETag'):
       ETag_Headers[ship] = response.headers.getRawHeaders('ETag')[0]
    if response.headers.hasHeader('Last-Modified'):
       Modified_Headers[ship] = response.headers.getRawHeaders('Last-Modified')[0]
    d = readBody(response)
    d.addCallback(EQBody, ship)
    return d

def CheckupURL():
   HTTPHeader0 = Headers({'User-Agent': ['PSO2Proxy']})

   for shipNum in config.globalConfig.get_key('enabledShips'):
       eq_URL = eqnotice_config.get_key(str(shipNum))
       if eq_URL:
          HTTPHeaderX = HTTPHeader0.copy()
          if ETag_Headers[shipNum]:
            HTTPHeaderX.addRawHeader('If-None-Match', ETag_Headers[shipNum])
          if Modified_Headers[shipNum]:
            HTTPHeaderX.addRawHeader('If-Modified-Since', Modified_Headers[shipNum])
          #print pformat(list(HTTPHeaderX.getAllRawHeaders()))
          EQ0 = agent.request('GET', eq_URL, HTTPHeaderX, None)
          EQ0.addCallback(EQResponse, shipNum)

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

