import data.clients, data.players, data.blocks 
from twisted.web.resource import Resource
import json, time

upStart = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

class WebAPI(Resource):
	isLeaf = True

	def render_GET(self, request):
		currData = {'count' : len(data.clients.connectedClients), 'blocksCached' : len(data.blocks.blockList), 'playersCached' : len(data.players.playerList), 'upSince' : upStart}
		request.setHeader("content-type", "text/plain")
		return json.dumps(currData)