import data.clients, data.players, data.blocks
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from config import webapi_enabled
from config import bindIp as interfaceIp
import json, calendar, datetime, plugins

upStart = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
peakPlayers = 0


class WebAPI(Resource):
    isLeaf = True

    # noinspection PyPep8Naming
    @staticmethod
    def render_GET(request):
        current_data = {'playerCount': len(data.clients.connectedClients), 'blocksCached': len(data.blocks.blockList),
                    'playersCached': len(data.players.playerList), 'upSince': upStart, 'peakPlayers': peakPlayers}
        request.setHeader("content-type", "application/json")
        return json.dumps(current_data)


@plugins.on_start_hook
def setup_web_api():
    if webapi_enabled:
        from twisted.web import server

        web_endpoint = TCP4ServerEndpoint(reactor, 8080, interface=interfaceIp)
        web_endpoint.listen(server.Site(WebAPI()))


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
