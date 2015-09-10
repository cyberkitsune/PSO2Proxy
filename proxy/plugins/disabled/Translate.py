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


def ci_switchs(cmd):  # decode /ci[1-9] {[1-5]} {t[1-5]} {nw} {s[0-99]}
    count = 0
    cmdl = cmd.split(" ", 5)
    if cmdl[count + 1].isalnum():
        count += 1
    if not cmdl[count + 1]:
        return count
    if cmdl[count + 1][0] == "t":
        count += 1
    if not cmdl[count + 1]:
        return count
    if cmdl[count + 1] == "nw":
        count += 1
    if not cmdl[count + 1]:
        return count
    if cmdl[count + 1][0] == "s":
        count += 1
    return count


def need_switchs(msg):  # return the max number of swtichs for the command
    if msg.startswith("toge") or msg.startswith("moya") or msg.startswith("mn"):
        return 0  # Text Bubble Emotes
    if msg.startswith("mainpalette") or msg.startswith("mpal"):
        return 0  # Switch Main Palette to %1
    if msg.startswith("subpalette") or msg.startswith("spal"):
        return 0  # Switch Sub Palette
    if msg.startswith("costume") or msg.startswith("cs"):
        return 1  # Switch Costume %1
    if msg.startswith("camouflage") or msg.startswith("cmf"):
        return 1  # Switch Camos %1
    if msg.startswith("la") or msg.startswith("mla") or msg.startswith("fla") or msg.startswith("cla"):
        return 1  # Lobby action %1
    if msg.startswith("ci"):
        return ci_switchs(msg)  # Cut-ins need special handling
    if msg.startswith("symbol"):
        return 0  # Symbol Art (symbol#)
    if msg.startswith("vo"):
        return 0  # Voice Clips (vo#)
    return -1  # Unknown


def split_cmd_msg(message):
    cmd = ""
    msg = message
    if not message.strip() or message.strip() == "null":
        return (cmd, "")
    cmd, split, msg = message.rpartition("/")  # Let process that last command
    if split:
        args = need_switchs(msg)  # how many switchs does the last command need?
        if args == -1:  # not a vaild command, let look again
            cmdr, msgr = split_cmd_msg(cmd)
            return (cmdr, msgr + split + msg)
        else:  # so it is a vaild command, let add back togther
            msgl = msg.split(u" ", args + 1)   # let break apart msg strings into a list
            msg = msgl[len(msgl) - 1]  # the string at the end of the list is the text
            cmdl = []  # Start a new list, with cmd
            cmdl.extend(msgl[0:args + 1])  # Add the command and all the switchs
            cmd = split + u" ".join(cmdl)  # join the list into a string
    return (cmd, msg)


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
            if channel_id == 2:
                return packet  # skip team chat
            message = packet[0x1C:].decode('utf-16').rstrip("\0")
            cmd, msg = split_cmd_msg(message)
            if not msg:
                return packet  # Command
            d = threads.deferToThread(generate_translated_message, player_id, channel_id, cmd, msg, "ja", "en")
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
        cmd, msg = split_cmd_msg(message)
        if not msg:
            return packet  # Command
        japanese = False
        for char in msg:
            char_script = script(unicode(char))
            if char_script != 'Latin' and char_script != 'Common':
                japanese = True
                break
        if not japanese:
            return packet
        d = threads.deferToThread(generate_translated_message, player_id, channel_id, cmd, msg, "en", "ja")
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

            cmd, msg = split_cmd_msg(message)

            if not msg:
                return packet  # Command

            d = threads.deferToThread(generate_translated_team_message, player_id, account, charname, cmd, msg, "ja", "en")
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
        if player_id == 0:  # We sent it
            return packet
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

        cmd, msg = split_cmd_msg(message)

        if not msg:
            return packet  # Command

        japanese = False
        for char in msg:
            char_script = script(unicode(char))
            if char_script != 'Latin' and char_script != 'Common':
                japanese = True
                break
        if not japanese:
            return packet
        d = threads.deferToThread(generate_translated_team_message, player_id, account, charname, cmd, msg, "en", "ja")
        d.addCallback(context.peer.send_crypto_packet)
        return None
    return packet


def generate_translated_message(player_id, channel_id, cmd, message, end_lang, start_lang):
    if provider == "Bing" and time.time() - lastKeyTime >= 600:
        translator.access_token = translator.get_access_token()

    try:
        if end_lang == "ja":
            message_string = "%s%s" % (cmd, translator.translate(message, end_lang, start_lang))
        else:
            message_string = "%s%s {def}(%s)" % (cmd, translator.translate(message, end_lang, start_lang), message)
    except Exception as e:
        print (str(e))
        message_string = message

    return packetFactory.ChatPacket(player_id, message_string, channel_id).build()


def generate_translated_team_message(player_id, account, charname, cmd, message, end_lang, start_lang):
    if provider == "Bing" and time.time() - lastKeyTime >= 600:
        translator.access_token = translator.get_access_token()

    try:
        if end_lang == "ja":
            message_string = "%s%s" % (cmd, translator.translate(message, end_lang, start_lang))
        else:
            message_string = "%s%s {def}(%s)" % (cmd, translator.translate(message, end_lang, start_lang), message)
    except Exception as e:
        print (str(e))
        message_string = message

    return packetFactory.TeamChatPacket(player_id, account, charname, message_string, True).build()
