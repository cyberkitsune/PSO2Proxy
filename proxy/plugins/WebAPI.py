import data.clients, data.players, data.blocks 
from twisted.web.resource import Resource
from twisted.internet import reactor
from config import webapi as webapi
import json, calendar, datetime, plugins

upStart = calendar.timegm(datetime.datetime.utcnow().utctimetuple())

class WebAPI(Resource):
	isLeaf = True

	def render_GET(self, request):
		currData = {'playerCount' : len(data.clients.connectedClients), 'blocksCached' : len(data.blocks.blockList), 'playersCached' : len(data.players.playerList), 'upSince' : upStart}
		request.setHeader("content-type", "application/json")
		return json.dumps(currData)

@plugins.onStartHook
def setupWebAPI():
	if webapi:
		from twisted.web import server
		import plugins.WebAPI as jsonsite
		wEndpoint = TCP4ServerEndpoint(reactor, 8080, interface=ifaceIp)
		wEndpoint.listen(server.Site(jsonsite.WebAPI()))
	