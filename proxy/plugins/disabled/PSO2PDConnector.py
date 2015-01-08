# Connector for PSO2Proxy-Distributed. Requires redis.
import traceback
import redis
import config
import json
from packetFactory import SystemMessagePacket
import plugins

import data.clients

from commands import commandList, Command


def servercom_handler(message):
    try:
        cmdObj = json.loads(message['data'])
    except:
        print("[PSO2PD] Got unknown message on servercom channel: %s" % message['data'])
        return
    if cmdObj['command'] == "exec":
        line = cmdObj['input']
        try:
            command = line.split(' ')[0]
            if command != "":
                if command in commandList:
                    f = commandList[command][0]
                    out = f(line).call_from_console()
                    if out is not None:
                        sendCommand({'command': "msg", 'msg': out})
                elif command in plugins.commands:
                    plugin_f = plugins.commands[command][0]
                    out = plugin_f(line).call_from_console()
                    if out is not None:
                        sendCommand({'command': "msg", 'msg': out})
                else:
                    sendCommand({'command': "msg", 'msg': "[Command] Command %s not found!" % command})
        except:
            e = traceback.format_exc()
            sendCommand({'command': "msg", 'msg': "[ShipProxy] Error Occurred: %s" % e})
    if cmdObj['command'] == "register":
        sendCommand({'command': "newserver", 'ip': config.myIpAddress, 'name': connector_conf['server_name']})
        print("[PSO2PD] Registered with redis!")
        sendCommand({'command': "ping", 'name': connector_conf['server_name'], 'usercount': len(data.clients.connectedClients)})


connector_conf = config.YAMLConfig("cfg/distributed.cfg.yml",{'db_host': 'localhost', 'db_port': 6379, 'db_id': 0, 'db_pass': '', 'server_name': 'changeme'}, True)

if connector_conf['db_pass'] is not '':
    db_conn = redis.StrictRedis(host=connector_conf['db_host'], port=connector_conf['db_port'], db=connector_conf['db_id'], password=connector_conf['db_pass'])
else:
    db_conn = redis.StrictRedis(host=connector_conf['db_host'], port=connector_conf['db_port'], db=connector_conf['db_id'])

pub_sub = db_conn.pubsub(ignore_subscribe_messages=True)

pub_sub.subscribe(**{"proxy-server-%s" % connector_conf['server_name']: servercom_handler})
pub_sub.subscribe(**{"proxy-global": servercom_handler})

pub_sub_thread = pub_sub.run_in_thread(sleep_time=0.001)

def sendCommand(command_dict):
    db_conn.publish("proxy-server-%s" % connector_conf['server_name'], json.dumps(command_dict))

@plugins.on_start_hook
def addServer():
    sendCommand({'command': "newserver", 'ip': config.myIpAddress, 'name': connector_conf['server_name']})
    print("[PSO2PD] Registered with redis!")


@plugins.on_stop_hook
def removeServer():
    sendCommand({'command': "delserver", 'name': connector_conf['server_name']})

    pub_sub_thread.stop()
    pub_sub.close()

    print("[PSO2PD] Redis stopped!")


@plugins.on_initial_connect_hook
def notifyMaster(client):
    sendCommand({'command': "ping", 'name': connector_conf['server_name'], 'usercount': len(data.clients.connectedClients)})

@plugins.on_client_remove_hook
def notifyMaster(client):
    sendCommand({'command': "ping", 'name': connector_conf['server_name'], 'usercount': len(data.clients.connectedClients) - 1})


@plugins.CommandHook("server", "Shows the server you're currently connected to.")
class ServerCommand(Command):
    def call_from_client(self, client):
        client.send_crypto_packet(SystemMessagePacket("You are currently connected to %s, on the IP address %s." % (connector_conf['server_name'], config.myIpAddress)).build())