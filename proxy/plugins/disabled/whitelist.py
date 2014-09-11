import json
import os

from packetFactory import SystemMessagePacket

from twisted.protocols import basic
from commands import Command

import plugins


whitelist = []

@plugins.on_start_hook
def load_whitelist():
    global whitelist
    if not os.path.exists("cfg/pso2proxy.whitelist.json"):
        f = open("cfg/pso2proxy.whitelist.json", "w")
        f.write(json.dumps(whitelist))
        f.close()
        print('[Whitelist] Blank whitelist created!')
    else:
        f = open("cfg/pso2proxy.whitelist.json", "r")
        whitelist = json.loads(f.read())
        f.close()
        print("[Whitelist] Loaded %i whitelisted SEGA IDs." % len(whitelist))


def save_whitelist():
    f = open("cfg/pso2proxy.whitelist.json", "w")
    f.write(json.dumps(whitelist))
    f.close()
    print('[Whitelist] Saved whitelist!')


@plugins.CommandHook("whitelist")
class Whitelist(Command):
    def call_from_console(self):
        global whitelist
        params = self.args.split(" ")
        if len(params) < 3:
            return "[Whitelist] Wrong usage, usage: >>> whitelist <add/del> <SEGA ID>"
        if params[1] == "add":
            if params[2] not in whitelist:
                whitelist.append(params[2])
                save_whitelist()
                return "[Whitelist] %s added to the whitelist!" % params[2]
            else:
                return "[Whitelist] %s is already in the whitelist" % params[2]
        elif params[1] == "del":
            if params[2] in whitelist:
                whitelist.remove(params[2])
                save_whitelist()
                return "[Whitelist] Removed %s from whitelist." % params[2]
            else:
                return "[Whitelist] %s is not in the whitelist, can not delete!" % params[2]
        else:
            return "[Whitelist] Wrong usage, usage: >>> whitelist <add/del> <SEGA ID>"


@plugins.PacketHook(0x11, 0x0)
def whitelist_check(context, data):
    """

    :type context: ShipProxy.ShipProxy
    """
    global whitelist
    start = len(data) - 132  # Skip password
    username = data[start:start + 0x40].decode('utf-8')
    username = username.rstrip('\0')
    if username not in whitelist:
        print("[Whitelist] %s is not in the whitelist, hanging up!" % username)
        context.send_crypto_packet(SystemMessagePacket("You are not whitelisted for this proxy. Please contact the owner to get in the whitelist.", 0x1).build())
        context.transport.loseConnection()
    return data
