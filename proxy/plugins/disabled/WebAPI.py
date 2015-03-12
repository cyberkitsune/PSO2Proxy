import calendar
import commands
from config import bindIp as interfaceIp
from config import myIpAddress as hostName
from config import YAMLConfig as ConfigModel

import data.blocks
import data.clients
import data.players

import datetime
import json
import os
import plugins
from plugins import commands as pluginCommands
import traceback
from twisted.internet import endpoints
from twisted.internet import reactor
from twisted.web import resource

web_api_config = ConfigModel("cfg/webapi.config.yml", {"port": 8080, "ServerName": "Unnamed Server", 'webRconEnabled': False, 'webRconKey': ''}, True)

upStart = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
peakPlayers = 0


class WEBRcon(resource.Resource):
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
                    if request.args['command'][0] in commands.commandList:
                        cmd_class = commands.commandList[request.args['command'][0]][0]
                        result = cmd_class("%s %s" % (request.args['command'][0], request.args['params'][0] if 'params' in request.args else None)).call_from_console()
                        return json.dumps({'success': True, 'output': result})
                    elif request.args['command'][0] in pluginCommands:
                        cmd_class = pluginCommands[request.args['command'][0]][0]
                        result = cmd_class("%s %s" % (request.args['command'][0], request.args['params'][0] if 'params' in request.args else None)).call_from_console()
                        return json.dumps({'success': True, 'output': result})
                    else:
                        return json.dumps({'success': False, 'reason': "Command not found."})
                except Exception as e:
                    e = traceback.format_exc()
                    return json.dumps({'success': False, 'reason': "Error executing command\n%s" % e})


class JSONConfig(resource.Resource):
    isLeaf = True

    # noinspection PyPep8Naming
    @staticmethod
    def render_GET(request):
        request.setHeader("content-type", "application/json")
        config_json = {'version': 1, "name": web_api_config.get_key('ServerName'), "publickeyurl": "http://%s:%i/publickey.blob" % (hostName, web_api_config.get_key('port')), "host": hostName}
        return json.dumps(config_json)


class PublicKey(resource.Resource):
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


class LatestProfile(resource.Resource):
    isLeaf = True

    @staticmethod
    def render_GET(request):
        request.setHeader("content-type", "text-plain")
        if os.path.exists("latest_profile.txt"):
            f = open("latest_profile.txt")
            profile = f.read()
            f.close()
            return profile
        else:
            return "No profile saved."


class LatestStackTrace(resource.Resource):
    isLeaf = True

    @staticmethod
    def render_GET(request):
        request.setHeader("content-type", "text-plain")
        if os.path.exists("log/tracestack.log"):
            f = open("log/tracestack.log")
            tracestack = f.read()
            f.close()
            return tracestack
        else:
            return "No tracekstack saved."


class WebAPI(resource.Resource):

    # noinspection PyPep8Naming
    @staticmethod
    def render_GET(request):
        current_data = {'playerCount': len(data.clients.connectedClients), 'blocksCached': len(data.blocks.blockList), 'uniquePlayers': data.clients.dbManager.get_db_size(), 'upSince': upStart, 'peakPlayers': peakPlayers}
        request.setHeader("content-type", "application/json")
        return json.dumps(current_data)

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)


@plugins.on_start_hook
def setup_web_api():
    from twisted.web import server
    if not os.path.exists("keys/publickey.blob"):
        print("[WebAPI] === Error ===")
        print("[WebAPI] Your public key is not in keys/publickey.blob !!")
        print("[WebAPI] As a result, webapi will be disabled !!")
        print("[WebAPI] Please fix this and restart the proxy.")
        return
    web_endpoint = endpoints.TCP4ServerEndpoint(reactor, web_api_config.get_key('port'), interface=interfaceIp)
    web_resource = WebAPI()
    web_resource.putChild("config.json", JSONConfig())
    web_resource.putChild("publickey.blob", PublicKey())
    web_resource.putChild("latest_profile", LatestProfile())
    web_resource.putChild("stacktrace", LatestStackTrace())
    if web_api_config.get_key('webRconEnabled'):
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
