import commands
import packetFactory
from packetFactory import SystemMessagePacket
import plugins
maintmode = False


@plugins.CommandHook("maint", "[Admin Only] Toggle maintenance mode", True)
class maintmode(commands.Command):
    def call_from_client(self, client):
        global maintmode
        maintmode = not maintmode
        if maintmode:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Maint] Maintenance mode turned on.", 0x3).build())
            return
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Maint] Maintenance mode turned off.", 0x3).build())
            return

    def call_from_console(self):
        global maintmode
        maintmode = not maintmode
        if maintmode:
            return "[Maint] Maintenance mode turned on."
        else:
            return "[Maint] Maintenance mode turned off."


@plugins.PacketHook(0x11, 0x0)
def Maint_check(context, data):
    """

    :type context: ShipProxy.ShipProxy
    """
    global maintmode
    if not maintmode:
        return data
    context.send_crypto_packet(SystemMessagePacket("The PSO2 or PSO2Proxy server is currently undergoing maintenance. Please try again later.", 0x1).build())
    context.transport.loseConnection()
    return data
