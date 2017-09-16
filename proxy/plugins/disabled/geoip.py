import commands
from config import YAMLConfig
import json
import os
import packetFactory
from packetFactory import SystemMessagePacket
import plugins


try:
    import geoip2
except ImportError:
    print("[GeoIP] geoip2 library not installed")

try:
    import GeoIP
except ImportError:
    print("[GeoIP] GeoIP library not installed")


cidr = False
try:
    import netaddr
    from netaddr import IPAddress
    from netaddr import IPNetwork
    cidr = True
except ImportError:
    print("[GeoIP] netaddr library not installed")

cidrlist = []

geoiplist = []

GeoSettings = YAMLConfig("cfg/pso2proxy.geoip.config.yml",
                         {'enabled': True, 'geoip1': "/usr/share/GeoIP/GeoIP.dat", 'geoip2': "/var/lib/GeoIP/GeoLite2-Country.mmdb"}, True)

geoipmode = GeoSettings.get_key('enabled')
geoip1db = GeoSettings.get_key('geoip1')
geoip2db = GeoSettings.get_key('geoip2')

geoip2c = None
geoip1c = None


@plugins.on_start_hook
def load_geoiplist():
    global geoiplist
    global geoip2c, geoip1c
    if not os.path.exists("cfg/pso2proxy.geoip.json"):
        f = open("cfg/pso2proxy.geoip.json", "w")
        f.write(json.dumps(geoiplist))
        f.close()
        print('[GeoIP] Blank whitelist made.')
    else:
        f = open("cfg/pso2proxy.geoip.json", "r")
        geoiplist = json.loads(f.read())
        f.close()
        print("[GeoIP] Loaded %i geoip entries." % len(geoiplist))

    try:
        geoip2c = geoip2.database.Reader(geoip2db)
    except AttributeError:
        None
    except NameError:
        None
    except Exception as e:
        print("[GeoIP] GeoIP2 error: {}".format(e))

    if geoip2c is None:
        try:
            geoip1c = GeoIP.open(geoip1db, GeoIP.GEOIP_CHECK_CACHE)
            geoip1c.set_charset(GeoIP.GEOIP_CHARSET_UTF8)
        except AttributeError:
            None
        except NameError:
            None
        except Exception as e:
            print("[GeoIP] GeoIP1 Error: {}".format(e))

    if cidr:
        cidrlist = []
        for x in geoiplist:
            try:
                cidrlist.append(IPNetwork(x))
            except ValueError:
                None
            except netaddr.AddrFormatError:
                None
            except Exception as e:
                print("[GeoIP] Error adding CIDR range {} during loading: {}".format(x, e))


def save_geoiplist():
    f = open("cfg/pso2proxy.geoip.json", "w")
    f.write(json.dumps(geoiplist))
    f.close()
    print('[GeoIP] Saved whitelist')

    if cidr:
        cidrlist = []
        for x in geoiplist:
            try:
                cidrlist.append(IPNetwork(x))
            except ValueError:
                None
            except Exception as e:
                print("[GeoIP] Error adding CIDR range {} during saving: {}".format(x, e))


@plugins.CommandHook("geoipmode", "[Admin Only] Toggle geoip mode", True)
class geoipmode(commands.Command):
    def call_from_client(self, client):
        global geoipmode
        geoipmode = not geoipmode
        if geoipmode:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GeoIP] Whitelist turn on.", 0x3).build())
            return
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[GeoIP] Whitelist turn off.", 0x3).build())
            return

    def call_from_console(self):
        global geoipmode
        geoipmode = not geoipmode
        if geoipmode:
            return "[GeoIP] Whitelist turn on."
        else:
            return "[GeoIP] Whitelist turn off."


@plugins.CommandHook("geoip", "[Admin Only] Adds or removes places to the geoip whitelist.", True)
class geoip(commands.Command):
    def call_from_console(self):
        global geoiplist
        params = self.args.split(" ")
        if len(params) < 3:
            return "[geoip] Invalid usage. (Usage: geoip <add/del> <place>)"
        if params[1] == "add" or params[1] == "ADD":
            if params[2] not in geoiplist:
                geoiplist.append(params[2])
                save_geoiplist()
                return "[GeoIP] Added %s to the whitelist." % params[2]
            else:
                return "[GeoIP] %s is already in the whitelist." % params[2]
        elif params[1] == "del" or params[1] == "DEL":
            if params[2] in geoiplist:
                geoiplist.remove(params[2])
                save_geoiplist()
                return "[GeoIP] Removed %s from whitelist." % params[2]
            else:
                return "[GeoIP] %s is not in the whitelist, can not delete!" % params[2]
        else:
            return "[GeoIP] Invalid usage. (Usage: whitelist <add/del> <palce>)"

    def call_from_client(self, client):
        """
        :param client: ShipProxy.ShipProxy
        """
        global geoiplist
        params = self.args.split(" ")
        if len(params) < 3:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. (Usage: geoip <add/del> <SegaID>)", 0x3).build())
            return
        if params[1] == "add" or params[1] == "ADD":
            if params[2] not in geoiplist:
                geoiplist.append(params[2])
                save_geoiplist()
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Added %s to the whitelist." % params[2], 0x3).build())
                return
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s is already in the whitelist." % params[2], 0x3).build())
                return
        elif params[1] == "del" or params[1] == "DEL":
            if params[2] in geoiplist:
                geoiplist.remove(params[2])
                save_geoiplist()
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {gre}Removed %s from whitelist." % params[2], 0x3).build())
                return
            else:
                client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}%s is not in the whitelist, can not delete!" % params[2], 0x3).build())
                return
        else:
            client.send_crypto_packet(packetFactory.SystemMessagePacket("[Command] {red}Invalid usage. (Usage: whitelist <add/del> <SegaID>)", 0x3).build())
            return


@plugins.PacketHook(0x11, 0x0)
def geoip_check(context, data):
    """

    :type context: ShipProxy.ShipProxy
    """
    global geoip2c, geoip1c
    global geoiplist
    global geoipmode
    place = "IPv4"
    ip = context.transport.getPeer().host
    badip = True

    if cidr:
        ipa = IPAddress(ip)
        for x in cidrlist:
            if ipa == x:
                badip = False

    if ip in geoiplist:
        badip = False
    elif geoip2c:
        try:
            respone = geoip2c.country(ip)
            place = respone.country.iso_code
            if place in geoiplist:
                badip = False
        except geoip2.AddressNotFoundError:
            print("[GeoIP] Could not find {} in GeoIP database)".format(ip))
            place = "NULL"
        except Exception as e:
            print("[GeoIP] Error: {}".format(e))
            place = "ERROR"
    elif geoip1c:
        try:
            place = geoip1c.country_code_by_addr(ip)
            if place is None:
                place = "NULL"
            elif place in geoiplist:
                badip = False
        except Exception as e:
            print("[GeoIP] Error: {}".format(e))
            place = "ERROR"

    if not geoip:
        print("[GeoIP] Connection from {}|{}".format(place, ip))
    elif badip:
        print("[GeoIP] {} (IP: {}) is not in the GeoIP whitelist, disconnecting client.".format(place, ip))
        context.send_crypto_packet(SystemMessagePacket("You are not on the Geoip whitelist for this proxy, please contact the owner of this proxy.\nDetails:\nCountry Code: {}\nIPv4: {}".format(place, ip), 0x1).build())
        context.transport.loseConnection()
    return data
