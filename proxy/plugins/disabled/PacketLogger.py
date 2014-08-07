import exceptions
import plugins as plugins
import struct
import os


@plugins.on_start_hook
def on_start():
    print("!!! WARNING !!!")
    print("You have PacketLogger.py outside of the disabled plugins folder! This means it is ON!")
    print("This plugin can log sensitive data!")
    print("Please be careful!")
    print("!!! WARNING !!!")


@plugins.raw_packet_hook
def on_packet_received(context, packet, packet_type, packet_subtype):
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