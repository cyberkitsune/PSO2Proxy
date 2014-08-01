import data.clients, data.players, data.blocks 
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from config import webapi as webapi
from config import bindIp as ifaceIp
import json, calendar, datetime, plugins

upStart = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
peakPlayers = 0

class WebAPI(Resource):
	isLeaf = True

	def render_GET(self, request):
		currData = {'playerCount' : len(data.clients.connectedClients), 'blocksCached' : len(data.blocks.blockList), 'playersCached' : len(data.players.playerList), 'upSince' : upStart, 'peakPlayers' : peakPlayers}
		request.setHeader("content-type", "application/json")
		return json.dumps(currData)

@plugins.onStartHook
def setupWebAPI():
	if webapi:
		from twisted.web import server
		wEndpoint = TCP4ServerEndpoint(reactor, 8080, interface=ifaceIp)
		wEndpoint.listen(server.Site(WebAPI()))

@plugins.onConnectionHook
def onConnection(client):
	global peakPlayers
	if peakPlayers < len(data.clients.connectedClients):
		peakPlayers = len(data.clients.connectedClients)

@plugins.onConnectionLossHook
def onLoss(clients): #This may be overkill
	global peakPlayers
	if peakPlayers < len(data.clients.connectedClients):
		peakPlayers = len(data.clients.connectedClients)
	
