# redpill.py PSO2Proxy plugin
# For use with redpill.py flask webapp and website for packet logging and management
import exceptions
import pymysql
import os
import glob
import tarfile
import shutil
import cProfile
import pstats
import StringIO
import json
import struct
import packetFactory
import plugins

jsonConfig = {'profiling': True, 'dbConfig': {'host': '', 'port': 3306, 'db': 'redpill', 'user': '', 'passwd': ''}, 'tarOut': None}

enabledCache = []

if not os.path.exists("cfg/redpill.config.json"):
    f = open("cfg/redpill.config.json", 'w')
    f.write(json.dumps(jsonConfig, indent=1))
    f.close()
    print("[Redpill] Redpill config generated!")
else:
    f = open("cfg/redpill.config.json", 'r')
    jsonConfig = json.loads(f.read())
    f.close()
    print("[Redpill] Redpill config loaded!")

profiling = jsonConfig['profiling']


@plugins.on_start_hook
def redpill_init():
    print("[Redpill] Redpill initialized.")


@plugins.on_initial_connect_hook
def notify_user(client):
    """
    :type client: ShipProxy
    """
    if 'redpill' in client.extendedData and client.extendedData['redpill']:
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[Redpill] {grn}You have chosen to opt-in to PacketDB. Your packets are being logged.", 0x3).build())
    else:
        client.send_crypto_packet(packetFactory.SystemMessagePacket("[Redpill] {red}You have chosen to opt-out from PacketDB. Your packets are not being logged.", 0x3).build())


@plugins.on_connection_hook
def catch_block_change(client):
    """
    :type client: ShipProxy
    """
    if client.myUsername is not None:
        if client.myUsername in enabledCache:
            client.extendedData['redpill'] = True
            client.peer.extendedData['redpill'] = True
        else:
            client.extendedData['redpill'] = False
            client.peer.extendedData['redpill'] = False
    else:
        client.extendedData['redpill'] = False
        client.peer.extendedData['redpill'] = False


@plugins.PacketHook(0x11, 0x0)
def login_packet_hook(context, packet):
    """
    :type context: ShipProxy
    """
    username = packet[0x8:0x48].decode('utf-8')
    username = username.rstrip('\0')
    con = get_connection()
    with con:
        if get_userid(con, username) is None:
            context.extendedData['redpill'] = False
            context.peer.extendedData['redpill'] = False
            print("[Redpill] %s is not in the whitelist database. Disabling functionality." % username)
        else:
            context.extendedData['redpill'] = True
            context.peer.extendedData['redpill'] = True
            enabledCache.append(username)
            increment_login_count(con, get_userid(con, username))
    return packet


@plugins.raw_packet_hook
def on_packet_received(context, packet, packet_type, packet_subtype):
    """
    :type context: ShipProxy
    """
    if 'redpill' in context.extendedData and not context.extendedData['redpill']:
        if 'orphans' in context.extendedData:
            del context.extendedData['orphans']
            print("[Redpill] Deleted orphans for non-participating client.")
        return packet
    if packet_type == 0x11 and packet_subtype == 0x0:
        packet_data = bytearray(packet)
        struct.pack_into("64x", packet_data, 0x48)
        packet_data = str(packet_data)
    else:
        packet_data = packet
    if context.psoClient:
        sender = "C"
    else:
        sender = "S"
    if context.myUsername is not None:
        path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (
            context.myUsername, context.connTimestamp, context.packetCount, packet_type, packet_subtype,
            sender)
        try:
            os.makedirs(os.path.dirname(path))
        except exceptions.OSError:
            pass
        with open(path, 'wb') as out_file:
            out_file.write(packet_data)
    else:
        if 'orphans' not in context.extendedData:
            context.extendedData['orphans'] = []
        context.extendedData['orphans'].append(
            {'data': packet_data, 'count': context.packetCount, 'type': packet_type, "sub": packet_subtype, "sender": sender})

    if context.myUsername is not None and 'orphans' in context.extendedData and len(context.extendedData['orphans']) > 0 and 'redpill' in context.extendedData and context.extendedData['redpill']:
        count = 0
        while len(context.extendedData['orphans']) > 0:
            orphan_packet = context.extendedData['orphans'].pop()
            path = 'packets/%s/%s/%i.%x-%x.%s.bin' % (
                context.myUsername, context.connTimestamp, orphan_packet['count'], orphan_packet['type'],
                orphan_packet['sub'], orphan_packet['sender'])
            try:
                os.makedirs(os.path.dirname(path))
            except exceptions.OSError:
                pass
            with open(path, 'wb') as out_file:
                out_file.write(orphan_packet['data'])
            count += 1
        print('[ShipProxy] Flushed %i orphan packets for %s.' % (count, context.myUsername))

    return str(packet)


@plugins.on_connection_lost_hook
def archive_packets(client):
    """
    :type client: ShipProxy
    """
    if not client.changingBlocks and client.myUsername in enabledCache:
        print("[Redpill] Removing %s from the enabled cache." % client.myUsername)
        enabledCache.remove(client.myUsername)
    if 'redpill' in client.extendedData and client.extendedData['redpill']:
        global profiling
        sid = client.myUsername
        timestamp = client.connTimestamp
        if sid is None or timestamp is None:
            print("[Redpill] Unable to check-in session, SID or timestamp is none.")
            return
        if not os.path.exists("packets/%s/%i/" % (sid, timestamp)):
            print("[Redpill] Could not check-in session for %s, timestamp %i does not exist" % (sid, timestamp))
            return

        if profiling:
            profile = cProfile.Profile()
            profile.enable()
        con = get_connection()
        with con:
            session_id = create_session(con, get_userid(con, sid), timestamp)
            packets = glob.glob("packets/%s/%i/*.bin" % (sid, timestamp))
            count = 0
            for packet in packets:
                order, packet_types, packet_sender, extension = packet.split(".")
                order = order.split("/")[-1]
                packet_type, packet_subtype = packet_types.split("-")
                player_id = get_packet_id(con, int(packet_type, 16), int(packet_subtype, 16))
                if player_id is None:
                    player_id = create_packet(con, int(packet_type, 16), int(packet_subtype, 16), get_userid(con, sid))
                add_session_data(con, session_id, player_id, packet_sender, order)
                increment_packet_count(con, player_id)
                count += 1
            print("[Redpill] Checked in session %i for %s with %i packets" % (timestamp, sid, count))
            tar = tarfile.open("packets/%s/%i.tar.gz" % (sid, timestamp), "w:gz")
            tar.add("packets/%s/%i/" % (sid, timestamp), arcname="%i" % timestamp)
            tar.close()
            shutil.rmtree("packets/%s/%i/" % (sid, timestamp))
            if jsonConfig['tarOut'] is not None:
                if not os.path.exists("%s/%s/" % (jsonConfig['tarOut'], sid)):
                    os.makedirs("%s/%s/" % (jsonConfig['tarOut'], sid))
                shutil.move("packets/%s/%i.tar.gz" % (sid, timestamp), "%s/%s/%i.tar.gz" % (jsonConfig['tarOut'], sid, timestamp))
            print("[Redpill] Archived as %i.tar.gz and deleted base folder." % timestamp)
        if profiling:
            profile.disable()
            s = StringIO.StringIO()
            sort_by = 'cumulative'
            ps = pstats.Stats(profile, stream=s).sort_stats(sort_by)
            ps.print_stats()


def get_connection():
    global jsonConfig
    db_settings = jsonConfig['dbConfig']
    connection = pymysql.connect(host=db_settings['host'], port=db_settings['port'], db=db_settings['db'],
                                 user=db_settings['user'], passwd=db_settings['passwd'], cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_userid(con, username):
    cur = con.cursor()
    cur.execute("select id from users where segaid = %s", (username, ))
    out = cur.fetchone()
    if out is None:
        return None
    else:
        return out['id']


def create_session(con, userid, timestamp):
    cur = con.cursor()
    cur.execute("insert into sessions (user, timestamp, name, notes) VALUES (%s,%s,%s,%s) ",
                (userid, timestamp, "Unnamed Session %s" % timestamp, "No notes."))
    return cur.lastrowid


def get_session_id(con, userid, timestamp):
    cur = con.cursor()
    cur.execute("select id from sessions where user = %s and timestamp = %s", (userid, timestamp))
    out = cur.fetchone()
    if out is None:
        return None
    else:
        return out['id']


def add_session_data(con, session_id, packet_id, sent_from, order):
    cur = con.cursor()
    cur.execute("insert into session_data (sessionID, sentFrom, packetId, notes, pOrder) values (%s,%s,%s,%s,%s)",
                (session_id, sent_from, packet_id, "No notes.", int(order)))


def get_packet_id(con, packet_type, packet_subtype):
    cur = con.cursor()
    cur.execute("select id from packets where type = %s and subType = %s", (packet_type, packet_subtype))
    out = cur.fetchone()
    if out is None:
        return None
    else:
        return out['id']


def increment_packet_count(con, packet_id):
    cur = con.cursor()
    cur.execute("update packets set count=count+1 where id = %s", (packet_id,))


def increment_login_count(con, player_id):
    cur = con.cursor()
    cur.execute("update users set logincount=logincount+1 where id = %s", (player_id,))


def create_packet(con, packet_type, packet_subtype, logger):
    cur = con.cursor()
    cur.execute("insert into packets (type, subType, firstLoggedBy, count) values (%s, %s, %s, 0)",
                (packet_type, packet_subtype, logger))
    return cur.lastrowid
