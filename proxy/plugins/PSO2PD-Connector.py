# Connector for PSO2Proxy-Distributed. Requires redis.
import redis
import config
import json
import plugins

import data.clients

def servercom_handler(message):
    pass

connector_conf = config.YAMLConfig("cfg/distributed.cfg.yml",{'db_host': 'localhost', 'db_port': 6379, 'db_id': 0, 'server_name': 'changeme'},True)

db_conn = redis.StrictRedis(host=connector_conf['db_host'], port=connector_conf['db_port'], db=connector_conf['db_id'])
pub_sub = db_conn.pubsub(ignore_subscribe_messages=True)

pub_sub.subscribe(**{"proxy-server-%s" % connector_conf['server_name']: servercom_handler})

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
    sendCommand({'command': "ping", 'name': connector_conf['server_name'], 'usercount': len(data.clients.connectedClients)})