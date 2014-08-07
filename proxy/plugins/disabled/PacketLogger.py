import exceptions
import shutil
from commands import Command
import plugins as plugins
import struct
import data.clients
import packetFactory
import tarfile
import json
import os


@plugins.on_start_hook
def on_start():
    print("!!! WARNING !!!")
    print("You have PacketLogger.py outside of the disabled plugins folder! This means it is ON!")
    print("This plugin can log sensitive data!")
    print("Please be careful!")
    print("!!! WARNING !!!")


@plugins.on_initial_connect_hook
def notify_and_config(client):
    """
    :type client: ShipProxy
    """
    if data.clients.connectedClients[client.playerId].preferences['logPackets'] is None:
        data.clients.connectedClients[client.playerId].preferences['logPackets'] = False
    if data.clients.connectedClients[client.playerId].preferences['logPackets']:
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[PacketLogging] {gre}You have opted-in to packet logging, Thank you! View your contributions on http://pso2proxy.cyberkitsune.net/redpill/ or use !optout to opt out", 0x3).build())
    else:
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[PacketLogging] {red}You have not opted-in to packet logging, and it has been disabled. Use !optin to opt in.", 0x3).build())


@plugins.CommandHook("optin", "Opts you into packet logging for the redpill project.")
class OptIn(Command):
    def call_from_client(self, client):
        data.clients.connectedClients[client.playerId].preferences['logPackets'] = True
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[PacketLogging] {gre}You have enabled packet logging! Thank you! Track your data at http://pso2proxy.cyberkitsune.net/redpill/", 0x3).build())


@plugins.CommandHook("optout", "Opts you out of the packet logging for the redpill project.")
class OptOut(Command):
    def call_from_client(self, client):
        archive_packets(client)
        data.clients.connectedClients[client.playerId].preferences['logPackets'] = False
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[PacketLogging] {red}You have disabled packet logging! :( If you change your mind, please use !optin to rejoin!", 0x3).build())


@plugins.raw_packet_hook
def on_packet_received(context, packet, packet_type, packet_subtype):
    """
    :type context: ShipProxy
    """
    prefs = None
    if 'prefs' not in context.extendedData and context.myUsername is not None and context.playerId not in data.clients.connectedClients:
        prefs = context.extendedData['prefs'] = data.clients.ClientPreferences(context.myUsername)
    if context.playerId in data.clients.connectedClients:
        del context.extendedData['prefs']
        prefs = data.clients.connectedClients[context.playerId].preferences

    if prefs is not None and context.myUsername is not None and prefs['logPackets'] is not None and not prefs['logPackets']:
        if 'orphans' in context.extendedData:
            print("[PacketLogger] %s has opted out of packet logging. Deleting orphans..." % context.myUsername)
            del context.extendedData['orphans']
        return packet
    if packet_type == 0x11 and packet_subtype == 0x0:
        packet_data = bytearray(packet)
        struct.pack_into("64x", packet_data, 0x48)
        packet_data = str(packet_data)
    else:
        packet_data = packet
    if context.myUsername is not None:
        path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (
            context.myUsername, context.connTimestamp, context.packetCount, packet_type, packet_subtype,
            context.transport.getPeer().host)
        try:
            os.makedirs(os.path.dirname(path))
        except exceptions.OSError:
            pass
        with open(path, 'wb') as f:
            f.write(packet_data)
    else:
        if 'orphans' not in context.extendedData:
            context.extendedData['orphans'] = []
        context.extendedData['orphans'].append(
            {'data': packet_data, 'count': context.packetCount, 'type': packet_type, "sub": packet_subtype})

    if context.myUsername is not None and 'orphans' in context.extendedData and len(context.extendedData['orphans']) > 0:
        count = 0
        while len(context.extendedData['orphans']) > 0:
            orphan_packet = context.extendedData['orphans'].pop()
            path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (
                context.myUsername, context.connTimestamp, orphan_packet['count'], orphan_packet['type'],
                orphan_packet['sub'],
                context.transport.getPeer().host)
            try:
                os.makedirs(os.path.dirname(path))
            except exceptions.OSError:
                pass
            with open(path, 'wb') as f:
                f.write(orphan_packet['data'])
            count += 1
        print('[ShipProxy] Flushed %i orphan packets for %s.' % (count, context.myUsername))

    return str(packet)


@plugins.on_connection_lost_hook
def archive_packets(client):
    """
    :type client: ShipProxy
    """
    if client.playerId in data.clients.connectedClients:
        if data.clients.connectedClients[client.playerId].preferences['logPackets']:
            metadata = {'sega_id': client.myUsername, 'player_id': client.playerId, 'timestamp': client.connTimestamp}
            json.dump(metadata, open("packets/%s/%s/metadata.json" % (client.myUsername, client.connTimestamp), 'w'))
            tar = tarfile.open("packets/%s/%i.tar.gz" % (client.myUsername, client.connTimestamp), "w:gz")
            tar.add("packets/%s/%i/" % (client.myUsername, client.connTimestamp), arcname="%i" % client.connTimestamp)
            tar.close()
            shutil.rmtree("packets/%s/%i" % (client.myUsername, client.connTimestamp))
            print("[PacketLogger] Archived %s's packet session %i." % (client.myUsername, client.connTimestamp))