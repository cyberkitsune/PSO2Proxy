import struct


def read_unencrypted_packet(filename):
    f = open(filename, 'r')
    length = struct.unpack('i', f.read(4))[0]
    f.seek(0)
    data = f.read(length)
    return bytearray(data)
