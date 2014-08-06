import json
import calendar
import datetime
import os

from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

import data.clients
import data.players
import data.blocks
from commands import commandList
from plugins import commands as pluginCommands
from config import bindIp as interfaceIp
from config import myIpAddress as hostName
from config import YAMLConfig as ConfigModel
import plugins


web_api_config = ConfigModel("cfg/webapi.config.yml", {"port": 8080, "ServerName": "Unnamed Server", 'webRconEnabled': False, 'webRconKey': ''}, True)

upStart = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
peakPlayers = 0


class WEBRcon(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader('content-type', "application/json")
        if 'key' not in request.args or request.args['key'][0] != web_api_config.get_key('webRconKey'):
            return json.dumps({'success': False, 'reason': "Your RCON key is invalid!"})
        else:
            if 'command' not in request.args:
                return json.dumps({'success': False, 'reason': "Command not specified."})
            else:
                try:
                    if request.args['command'][0] in commandList:
                        cmd_class = commandList[request.args['command'][0]][0]
                        result = cmd_class(request.args['params'][0] if 'params' in request.args else None).call_from_console()
                        return json.dumps({'success': True, 'output': result})
                    elif request.args['command'][0] in pluginCommands:
                        cmd_class = pluginCommands[request.args['command'][0]][0]
                        result = cmd_class(request.args['params'][0] if 'params' in request.args else None).call_from_console()
                        return json.dumps({'success': True, 'output': result})
                    else:
                        json.dumps({'success': False, 'reason': "Command not found."})
                except:
                    return json.dumps({'success': False, 'reason': "Error executing command"})



class JSONConfig(Resource):
    isLeaf = True

    # noinspection PyPep8Naming
    @staticmethod
    def render_GET(request):
        request.setHeader("content-type", "application/json")
        config_json = {'version': 1, "name": web_api_config.get_key('ServerName'), "publickeyurl": "http://%s:8080/publickey.blob" % hostName, "host": hostName}
        return json.dumps(config_json)


class PublicKey(Resource):
    isLeaf = True

    # noinspection PyPep8Naming
    @staticmethod
    def render_GET(request):
        request.setHeader("content-type", "application/octet-stream")
        if os.path.exists("keys/publickey.blob"):
            f = open("keys/publickey.blob", 'rb')
            pubkey_data = f.read()
            f.close()
            return pubkey_data


class WebAPI(Resource):

    # noinspection PyPep8Naming
    @staticmethod
    def render_GET(request):
        current_data = {'playerCount': len(data.clients.connectedClients), 'blocksCached': len(data.blocks.blockList),
                    'playersCached': len(data.players.playerList), 'upSince': upStart, 'peakPlayers': peakPlayers}
        request.setHeader("content-type", "application/json")
        return json.dumps(current_data)

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)


@plugins.on_start_hook
def setup_web_api():
    from twisted.web import server
    if not os.path.exists("keys/publickey.blob"):
        print("[WebAPI] === Error ===")
        print("[WebAPI] Your public key is not in keys/publickey.blob !!")
        print("[WebAPI] As a result, webapi will be disabled !!")
        print("[WebAPI] Please fix this and restart the proxy.")
        return
    web_endpoint = TCP4ServerEndpoint(reactor, web_api_config.get_key('port'), interface=interfaceIp)
    web_resource = WebAPI()
    web_resource.putChild("config.json", JSONConfig())
    web_resource.putChild("publickey.blob", PublicKey())
    if web_api_config.get_key(['webRconEnabled']):
        web_resource.putChild("rcon", WEBRcon())
    web_endpoint.listen(server.Site(web_resource))


@plugins.on_connection_hook
def on_connection(client):
    global peakPlayers
    if peakPlayers < len(data.clients.connectedClients):
        peakPlayers = len(data.clients.connectedClients)


@plugins.on_connection_lost_hook
def on_loss(client):  # This may be overkill
    global peakPlayers
    if peakPlayers < len(data.clients.connectedClients):
        peakPlayers = len(data.clients.connectedClients)
