import commands
import packetFactory
from packetFactory import SystemMessagePacket
import plugins
maintmode = False


@plugins.CommandHook("maint", "[Admin Only] Toggle maint mode", True)
class maintmode(commands.Command):
    def call_from_client(self, client):
        global maintmode
        maintmode = not maintmode
        if maintmode:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Maint] maintenance mode turned on.", 0x3).build())
            return
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Maint] maintenance mode turned off.", 0x3).build())
            return

    def call_from_console(self):
        global maintmode
        maintmode = not maintmode
        if maintmode:
            return "[Maint] maintenance mode turned on."
        else:
            return "[Maint] maintenance mode turned off."


@plugins.PacketHook(0x11, 0x0)
def Maint_check(context, data):
    """

    :type context: ShipProxy.ShipProxy
    """
    global maintmode
    if not maintmode:
        return data
    context.send_crypto_packet(SystemMessagePacket("PSO2 Servers/Proxy is in maintenance mode", 0x1).build())
    context.transport.loseConnection()
    return data
