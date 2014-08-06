import data.clients
import packetFactory
import struct
from microsofttranslator import Translator
from unicodescript import script
from commands import Command
from config import YAMLConfig

import plugins as p

translation_config = YAMLConfig("cfg/translator.config.yml", {'app_id': '', 'secret_key': ''}, True)


@p.on_initial_connect_hook
def create_preferences(client):
    if client.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[client.playerId].get_preferences()
        if 'translate_chat' not in user_prefs:
            user_prefs['translate_chat'] = False
            user_prefs['translate_out'] = False
            data.clients.connectedClients[client.playerId].set_preferences(user_prefs)


@p.CommandHook("translate", "Toggles proxy-end chat translation. (Powered by Bing Translate, Incoming only.)")
class ToggleTranslate(Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].get_preferences()
            user_prefs['translate_chat'] = not user_prefs['translate_chat']
            if user_prefs['translate_chat']:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Enabled incoming chat translation.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Disabled incoming chat translation.", 0x3).build())
            data.clients.connectedClients[client.playerId].set_preferences(user_prefs)

@p.CommandHook("jpout", "Toggles outbound chat translation to japanese. (Powered by Bing Translate, Outgoing only.)")
class ToggleTranslate(Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].get_preferences()
            user_prefs['translate_out'] = not user_prefs['translate_out']
            if user_prefs['translate_out']:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Enabled outgoing chat translation.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Disabled outgoing chat translation.", 0x3).build())
            data.clients.connectedClients[client.playerId].set_preferences(user_prefs)


@p.PacketHook(0x7, 0x0)
def get_chat_packet(context, packet):
    if context.psoClient and context.playerId and data.clients.connectedClients[context.playerId].get_preferences()['translate_out']:
        player_id = struct.unpack_from("I", packet, 0x8)[0]
        if player_id != 0:  # ???
            return
        channel_id = struct.unpack_from("I", packet, 0x14)[0]
        message = packet[0x1C:].decode('utf-16').rstrip("\0")
        translator = Translator(translation_config.get_key('app_id'), translation_config.get_key('secret_key'))
        return packetFactory.ChatPacket(0x0, translator.translate(message, "ja"), channel_id).build()
    if context.peer.psoClient and context.peer.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[context.peer.playerId].get_preferences()
        if not user_prefs['translate_chat']:
            return packet
        player_id = struct.unpack_from("I", packet, 0x8)[0]
        if player_id == 0:  # We sent it
            return packet
        channel_id = struct.unpack_from("I", packet, 0x14)[0]
        message = packet[0x1C:].decode('utf-16')
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
        translator = Translator(translation_config.get_key('app_id'), translation_config.get_key('secret_key'))
        new_msg = "%s (%s)" % (translator.translate(message, "en"), message.rstrip('\0'))
        return packetFactory.ChatPacket(player_id, new_msg, channel_id).build()
    return packet
