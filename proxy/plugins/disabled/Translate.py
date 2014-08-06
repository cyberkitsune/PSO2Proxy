import data.clients
import packetFactory
import struct
from microsofttranslator import Translator
from unicodescript import script
from commands import Command
from config import YAMLConfig

import plugins as p

translation_config = YAMLConfig("cfg/translator.config.yml", {'app_id': '', 'secret_key': ''}, True)
translator = Translator(translation_config.get_key('app_id'), translation_config.get_key('secret_key'))


@p.on_initial_connect_hook
def create_preferences(client):
    if client.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[client.playerId].get_preferences()
        if 'translate_chat' not in user_prefs:
            user_prefs['translate_chat'] = False
            data.clients.connectedClients[client.playerId].set_preferences(user_prefs)


@p.CommandHook("translate", "Toggles proxy-end chat translation. (Powered by Bing Translate, Incoming only.)")
class ToggleTranslate(Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].get_preferences()
            user_prefs['translate_chat'] = not user_prefs['translate_chat']
            if user_prefs['translate_chat']:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Enabled Chat Translation.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Disabled Chat Translation.", 0x3).build())
            data.clients.connectedClients[client.playerId].set_preferences(user_prefs)


@p.PacketHook(0x7, 0x0)
def get_chat_packet(context, packet):
    if context.peer.psoClient and context.peer.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[context.peer.playerId].get_preferences()
        if not user_prefs['translate_chat']:
            return packet
        player_id = struct.unpack_from("I", packet, 0x8)[0]
        if player_id == 0 or player_id == context.peer.playerId:  # We sent it
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
        new_msg = "%s (%s)" % (translator.translate(message, "en"), message.rstrip('\0'))
        return packetFactory.ChatPacket(player_id, new_msg, channel_id).build()
    return packet