import struct


def readUnencryptedPktFile(path):
    f = open(path, 'r')
    length = struct.unpack('i', f.read(4))[0]
    f.seek(0)
    data = f.read(length)
    return bytearray(data)
