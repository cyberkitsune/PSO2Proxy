import io, struct


def encode_string_utf16(string, xor_value, sub_value):
    prefix = ((len(string) + 1) + sub_value) ^ xor_value

    data = string.encode('utf-16le') + '\0\0'
    if (len(data) % 4) == 2:
        data += '\0\0'

    return struct.pack('<I', prefix) + data


class Packet(object):
    """docstring for PacketFactory"""

    def __init__(self, packet_type, packet_subtype, flag1, flag2, data):
        self.pId = packet_type
        self.subId = packet_subtype
        self.flag1 = flag1
        self.flag2 = flag2
        self.data = data

    def build(self):
        buf = bytearray()
        buf += struct.pack('i', (len(self.data) + 0x8))
        buf += struct.pack('BBBB', self.pId, self.subId, self.flag1, self.flag2)
        buf += self.data
        return str(buf)


class PlayerHeader(object):
    """docstring for PlayerHeader"""

    def __init__(self, player_id=0x0, _4=0x0, _8=0x4, _a=0x0):
        self.playerId = player_id
        self._4 = _4
        self._8 = _8
        self._A = _a

    def build(self):
        buf = bytearray()
        buf += struct.pack('<IIHH', self.playerId, self._4, self._8, self._A)
        return buf


class ChatPacket(object):
    def __init__(self, sender_id, message, channel=0x1):
        self.senderId = sender_id
        self.message = message
        self.channel = channel

    def build(self):
        buf = bytearray()
        buf += PlayerHeader(self.senderId).build()
        buf += struct.pack('<I', self.channel)
        # Magical xor man
        buf += encode_string_utf16(self.message, 0x9d3f, 0x44)
        # buf += struct.pack('xx') #pad!
        return Packet(0x7, 0x0, 0x44, 0x0, buf).build()


class GoldGlobalMessagePacket(object):
    """Golden Global Message Packet"""

    def __init__(self, message):
        self.message = message

    def build(self):
        buf = bytearray()
        buf += encode_string_utf16(self.message, 0x78f7, 0xa2)
        buf += struct.pack('4x')
        return Packet(0x19, 0x01, 0x4, 0x0, buf).build()


class TeamChatPacket(object):
    """docstring for TeamChatPacket"""

    def __init__(self, sender_id, sender_name, message):
        self.senderId = sender_id
        self.senderName = sender_name
        self.message = message

    def build(self):
        buf = bytearray()
        buf += PlayerHeader(self.senderId).build()
        buf += struct.pack('<I', 0x2)
        buf += encode_string_utf16(self.senderName, 0x7ED7, 0x41)
        buf += encode_string_utf16(self.senderName, 0x7ED7, 0x41)
        buf += encode_string_utf16(self.message, 0x7ED7, 0x41)
        return Packet(0x7, 0x11, 0x4, 0x00, buf).build()
