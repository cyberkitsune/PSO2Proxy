import data.clients
import packetFactory
import struct
import goslate
from unicodescript import script
from commands import Command

import plugins as p

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


@p.CommandHook("jpin", "Toggles proxy-end chat translation. (Powered by Google Translate, Incoming only.)")
class ToggleTranslate(Command):
    def call_from_client(self, client):
        if client.playerId in data.clients.connectedClients:
            user_prefs = data.clients.connectedClients[client.playerId].preferences
            user_prefs.set_preference('translate_chat', not user_prefs.get_preference('translate_chat'))
            if user_prefs.get_preference('translate_chat'):
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Enabled incoming chat translation.", 0x3).build())
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Translate] Disabled incoming chat translation.", 0x3).build())

@p.CommandHook("jpout", "Toggles outbound chat translation to japanese. (Powered by Google Translate, Outgoing only.)")
class ToggleTranslate(Command):
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
    if context.psoClient and context.playerId and data.clients.connectedClients[context.playerId].preferences.get_preference('translate_out'):
        player_id = struct.unpack_from("I", packet, 0x8)[0]
        if player_id != 0:  # ???
            return
        channel_id = struct.unpack_from("I", packet, 0x14)[0]
        message = packet[0x1C:].decode('utf-16').rstrip("\0")
        try:
            return packetFactory.ChatPacket(0x0, translator.translate(message, "ja", "en"), channel_id).build()
        except:
            print("[Translator] Got an exception! Bailing out...")
            return packet
    if context.peer.psoClient and context.peer.playerId in data.clients.connectedClients:
        user_prefs = data.clients.connectedClients[context.peer.playerId].preferences
        if not user_prefs.get_preference('translate_chat'):
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
        try:
            new_msg = "%s (%s)" % (translator.translate(message, "en", "ja").rstrip('\0'), message.rstrip('\0'))
            return packetFactory.ChatPacket(player_id, new_msg, channel_id).build()
        except:
            print("[Translator] Got an exception! Bailing out...")
            return packet
    return packet
