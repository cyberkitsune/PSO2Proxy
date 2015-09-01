import commands
from config import YAMLConfig
import data.clients
import packetFactory
import struct
import time
from twisted.internet import threads
from unicodescript import script

import plugins as p

plugin_config = YAMLConfig("cfg/translator.config.yml", {"translationService": 0, "msTranslateID": '', "msTranslateSecret": ''})
if plugin_config['translationService'] == 1 and plugin_config['msTranslateID'] != '' and plugin_config['msTranslateSecret'] != '':
    import microsofttranslator
    provider = "Bing"
    translator = microsofttranslator.Translator(plugin_config['msTranslateID'], plugin_config['msTranslateSecret'])
    lastKeyTime = time.time()
else:
    import goslate
    provider = "Google"
    translator = goslate.Goslate()


@p.on_initial_connect_hook
def create_preferences(client):
    """
    :type client: ShipProxy
    """
    if client.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[client.playerId].preferences
        if not user_prefs.has_preference('translate_chat'):
            user_prefs.set_preference('translate_chat', False)
            user_prefs.set_preference('translate_out', False)


@p.CommandHook("jpin", "Toggles proxy-end chat translation. (Powered by %s Translate, Incoming only.)" % provider)
class ToggleTranslateIn(commands.Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].preferences
            user_prefs.set_preference('translate_chat', not user_prefs.get_preference('translate_chat'))
            if user_prefs.get_preference('translate_chat'):
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Enabled incoming chat translation.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Disabled incoming chat translation.", 0x3).build())


@p.CommandHook("jpout", "Toggles outbound chat translation to japanese. (Powered by %s Translate, Outgoing only.)" % provider)
class ToggleTranslateOut(commands.Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].preferences
            user_prefs.set_preference('translate_out', not user_prefs.get_preference('translate_out'))
            if user_prefs.get_preference('translate_out'):
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Enabled outgoing chat translation.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Disabled outgoing chat translation.", 0x3).build())


@p.PacketHook(0x7, 0x0)
def get_chat_packet(context, packet):
    """
    :type context: ShipProxy.ShipProxy
    """
    try:
        if context.psoClient and context.playerId and data.clients.connectedClients[context.playerId].preferences.get_preference('translate_out'):
            player_id = struct.unpack_from("<I", packet, 0x8)[0]
            if player_id != 0:  # ???
                return None
            channel_id = struct.unpack_from("<I", packet, 0x14)[0]
            message = packet[0x1C:].decode('utf-16').rstrip("\0")
            d = threads.deferToThread(generate_translated_message, player_id, channel_id, message, "ja", "en")
            d.addCallback(context.peer.send_crypto_packet)
            return None
    except KeyError:
        return packet
    if context.peer.psoClient and context.peer.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[context.peer.playerId].preferences
        if not user_prefs.get_preference('translate_chat'):
            return packet
        player_id = struct.unpack_from("<I", packet, 0x8)[0]
        if player_id == 0:  # We sent it
            return packet
        channel_id = struct.unpack_from("<I", packet, 0x14)[0]
        message = packet[0x1C:].decode('utf-16').rstrip("\0")
        if message.startswith("/"):
            return packet  # Command
        japanese = False
        for char in message:
            char_script = script(unicode(char))
            if char_script != 'Latin' and char_script != 'Common':
                japanese = True
                break
        if not japanese:
            return packet
        d = threads.deferToThread(generate_translated_message, player_id, channel_id, message, "en", "ja")
        d.addCallback(context.peer.send_crypto_packet)
        return None
    return packet


def decode_string_utf16_len(prefix, xor_value, sub_value):
    #  prefix = ((len(string) + 1) + sub_value) ^ xor_value
    #  prefix ^ xor_value = ((len(string) + 1) + sub_value)
    #  ((prefix ^ xor_value) - sub_value) = len + 1
    #  ((prefix ^ xor_value) - sub_value) - 1 = len
    return ((prefix ^ xor_value) - sub_value) - 1


@p.PacketHook(0x7, 0x11)
def get_team_chat_packet(context, packet):
    """
    :type context: ShipProxy.ShipProxy
    """
    if struct.unpack_from("<I", packet, 0xF)[0] == 0x2:
        return packet
    try:
        if context.psoClient and context.playerId and data.clients.connectedClients[context.playerId].preferences.get_preference('translate_out'):
            player_id = struct.unpack_from("<I", packet, 0x8)[0]
            if player_id != 0:  # ???
                return None

            pis = 0x8  # read the playerid
            player_id = struct.unpack_from("<I", packet, pis)[0]
            pis += 0x14  # let skip to the first unicode string len

            wlen = decode_string_utf16_len(struct.unpack_from("<I", packet, pis)[0], 0x7ED7, 0x41)
            wlen += 1
            if (wlen % 2) == 1:
                wlen += 1

            pis += 0x04  # skipping to start of utf-16 string
            account = packet[pis:pis + (wlen * 2)].decode('utf-16').rstrip("\0")
            pis += (wlen * 2)  # skipping to the end of utf-16 string

            wlen = decode_string_utf16_len(struct.unpack_from("<I", packet, pis)[0], 0x7ED7, 0x41)
            wlen += 1
            if (wlen % 2) == 1:
                wlen += 1

            pis += 0x04  # skipping to start of utf-16 string
            charname = packet[pis:pis + (wlen * 2)].decode('utf-16').rstrip("\0")
            pis += (wlen * 2)  # skipping to the end of utf-16 string

            wlen = decode_string_utf16_len(struct.unpack_from("<I", packet, pis)[0], 0x7ED7, 0x41)
            wlen += 1
            if (wlen % 2) == 1:
                wlen += 1

            pis += 0x04  # skipping to start of utf-16 string
            message = packet[pis:pis + (wlen * 2)].decode('utf-16').rstrip("\0")
            pis += (wlen * 2)  # skipping to the end of utf-16 string

            if message.startswith("/"):
                return packet  # Command

            d = threads.deferToThread(generate_translated_team_message, player_id, account, charname, message, "ja", "en")
            d.addCallback(context.peer.send_crypto_packet)
            return None
    except KeyError:
        return packet
    if context.peer.psoClient and context.peer.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[context.peer.playerId].preferences
        if not user_prefs.get_preference('translate_chat'):
            return packet

        pis = 0x8  # read the playerid
        player_id = struct.unpack_from("<I", packet, 0x8)[0]
        pis += 0x14  # let skip to the first unicode string len

        wlen = decode_string_utf16_len(struct.unpack_from("<I", packet, pis)[0], 0x7ED7, 0x41)
        wlen += 1
        if (wlen % 2) == 1:
            wlen += 1

        pis += 0x04  # skipping to start of utf-16 string
        account = packet[pis:pis + (wlen * 2)].decode('utf-16').rstrip("\0")
        pis += (wlen * 2)  # skipping to the end of utf-16 string

        wlen = decode_string_utf16_len(struct.unpack_from("<I", packet, pis)[0], 0x7ED7, 0x41)
        wlen += 1
        if (wlen % 2) == 1:
            wlen += 1

        pis += 0x04  # skipping to start of utf-16 string
        charname = packet[pis:pis + (wlen * 2)].decode('utf-16').rstrip("\0")
        pis += (wlen * 2)  # skipping to the end of utf-16 string

        wlen = decode_string_utf16_len(struct.unpack_from("<I", packet, pis)[0], 0x7ED7, 0x41)
        wlen += 1
        if (wlen % 2) == 1:
            wlen += 1

        pis += 0x04  # skipping to start of utf-16 string
        message = packet[pis:pis + (wlen * 2)].decode('utf-16').rstrip("\0")
        pis += (wlen * 2)  # skipping to the end of utf-16 string

        if message.startswith("/"):
            return packet  # Command
        japanese = False
        for char in message:
            char_script = script(unicode(char))
            if char_script != 'Latin' and char_script != 'Common':
                japanese = True
                break
        if not japanese:
            return packet
        d = threads.deferToThread(generate_translated_team_message, player_id, account, charname, message, "en", "ja")
        d.addCallback(context.peer.send_crypto_packet)
        return None
    return packet


def generate_translated_message(player_id, channel_id, message, end_lang, start_lang):
    if provider == "Bing" and time.time() - lastKeyTime >= 600:
        translator.access_token = translator.get_access_token()

    try:
        if end_lang == "ja":
            message_string = "%s" % translator.translate(message, end_lang, start_lang)
        else:
            message_string = "%s {def}(%s)" % (translator.translate(message, end_lang, start_lang), message)
    except Exception as e:
        print (str(e))
        message_string = message

    return packetFactory.ChatPacket(player_id, message_string, channel_id).build()


def generate_translated_team_message(player_id, account, charname, message, end_lang, start_lang):
    if provider == "Bing" and time.time() - lastKeyTime >= 600:
        translator.access_token = translator.get_access_token()

    try:
        if end_lang == "ja":
            message_string = "%s" % translator.translate(message, end_lang, start_lang)
        else:
            message_string = "%s {def}(%s)" % (translator.translate(message, end_lang, start_lang), message)
    except Exception as e:
        print (str(e))
        message_string = message

    return packetFactory.TeamChatPacket(player_id, account, charname, message_string, True).build()
