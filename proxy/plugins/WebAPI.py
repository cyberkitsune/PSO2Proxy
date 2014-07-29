import data.clients, data.players, data.blocks 
from twisted.web.resource import Resource
import json, calendar, datetime

upStart = calendar.timegm(datetime.datetime.utcnow().utctimetuple())

class WebAPI(Resource):
	isLeaf = True

	def render_GET(self, request):
		currData = {'playerCount' : len(data.clients.connectedClients), 'blocksCached' : len(data.blocks.blockList), 'playersCached' : len(data.players.playerList), 'upSince' : upStart}
		request.setHeader("content-type", "application/json")
		return json.dumps(currData)