import exceptions
from twisted.internet import reactor
from commands import Command
import plugins as plugins
from data.clients import dbManager
import struct
import packetFactory
import json
import os
import config

def write_file(filename, data, mode='wb'):
    with open(filename, mode) as f:
        f.write(data)

@plugins.on_start_hook
def on_start():
    print("=== PacketLogger Notice ===")
    print("PacketLogger is enabled!")
    print("This plugin can log sensitive data!")
    print("Please be careful!")
    print("=== PacketLogger Notice ===")

@plugins.on_initial_connect_hook
def notify_and_config(client):
    """
    :type client: ShipProxy.ShipProxy
    """
    client_config = dbManager.get_data_for_sega_id(client.myUsername)
    if 'logPackets' not in client_config:
        client_config['logPackets'] = False
    if client_config['logPackets']:
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket("[PacketLogger] {gre}You have opted-in to packet logging, thank you! You can opt-out at any time by using {command_prefix}optout", 0x3).build())
    else:
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket("[PacketLogger] {red}You have opted-out of packet logging. You can opt-in at any time by using {command_prefix}optin", 0x3).build())

@plugins.CommandHook("optin", "Opts you into packet logging.")
class OptIn(Command):
    def call_from_client(self, client):
        client_config = dbManager.get_data_for_sega_id(client.myUsername)
        client_config['logPackets'] = True
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket("[PacketLogger] {gre}You have enabled packet logging, thank you! You can opt-out at any time by using {command_prefix}optout", 0x3).build())

@plugins.CommandHook("optout", "Opts you out of the packet logging.")
class OptOut(Command):
    def call_from_client(self, client):
        archive_packets(client)
        client_config = dbManager.get_data_for_sega_id(client.myUsername)
        client_config['logPackets'] = True
        client.send_crypto_packet(
	  packetFactory.SystemMessagePacket("[PacketLogger] {red}You have disabled packet logging. If you change your mind, you can opt-in by using {command_prefix}optin", 0x3).build())

@plugins.raw_packet_hook
def on_packet_received(context, packet, packet_type, packet_subtype):
    """
    :type context: ShipProxy.ShipProxy
    """
    if context.myUsername is not None:
        client_config = dbManager.get_data_for_sega_id(context.myUsername)
        if 'logPackets' not in client_config:
            client_config['logPackets'] = False
            return packet
        if not client_config['logPackets']:
            if 'orphans' in context.extendedData:
                print("[PacketLogger] %s has opted out of packet logging." % context.myUsername)
                del context.extendedData['orphans']
            return packet
    if packet_type == 0x11 and packet_subtype == 0x0:
        packet_data = bytearray(packet)
        struct.pack_into("64x", packet_data, 0x48)
        packet_data = str(packet_data)
    else:
        packet_data = packet
    if context.psoClient:
        sender = "C"
    else:
        sender = "S"
    if context.myUsername is not None:
        path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (context.myUsername, context.connTimestamp, context.packetCount, packet_type, packet_subtype,sender)
        try:
            os.makedirs(os.path.dirname(path))
        except exceptions.OSError:
            pass
        reactor.callInThread(write_file, path, packet_data)
    else:
        if 'orphans' not in context.extendedData:
            context.extendedData['orphans'] = []
        context.extendedData['orphans'].append({'data': packet_data, 'count': context.packetCount, 'type': packet_type, "sub": packet_subtype, "sender": sender})

    if context.myUsername is not None and 'orphans' in context.extendedData and len(context.extendedData['orphans']) > 0:
        count = 0
        while len(context.extendedData['orphans']) > 0:
            orphan_packet = context.extendedData['orphans'].pop()
            path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (
                context.myUsername, context.connTimestamp, orphan_packet['count'], orphan_packet['type'],
                orphan_packet['sub'], orphan_packet['sender'])
            try:
                os.makedirs(os.path.dirname(path))
            except exceptions.OSError:
                pass
            reactor.callInThread(write_file, path, orphan_packet['data'])
            count += 1
        print('[PacketLogger] Flushed %i orphan packets for %s.' % (count, context.myUsername))

    return str(packet)

@plugins.on_connection_lost_hook
def archive_packets(client):
    """
    :type client: ShipProxy.ShipProxy
    """
    user_config = dbManager.get_data_for_sega_id(client.myUsername)
    if user_config['logPackets']:
        metadata = {'sega_id': client.myUsername, 'player_id': client.playerId, 'timestamp': client.connTimestamp}
        json_string = json.dumps(metadata)
        reactor.callInThread(write_file, "packets/%s/%s/metadata.json" % (client.myUsername, client.connTimestamp), json_string, 'w')
        print("[PacketLogger] Wrote meta for %s, %i." % (client.myUsername, client.connTimestamp))
