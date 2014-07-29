from . import data.clients, data.players, data.blocks 
from twisted.web.resource import Resource
import json, time

upStart = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

class WebAPI(Resource):
	def render_GET(self, request):
		currData = {'count' : len(clients.connectedClients), 'blocksCached' : len(blocks.blockList), 'playersCached' : len(players.playerList), 'upSince' : upStart}
		return json.dumps(currData)