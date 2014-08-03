enabled = False

if enabled:
    import json, plugins, os
    from twisted.protocols import basic

    whitelist = []

    @plugins.onStartHook
    def loadWhitelist():
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

    def saveWhitelist():
        f = open("cfg/pso2proxy.whitelist.json", "w")
        f.write(json.dumps(whitelist))
        f.close()
        print('[Whitelist] Saved whitelist!')

    @plugins.commandHook("whitelist")
    def whiteListCommand(sender, params):
        if isinstance(sender, basic.LineReceiver):
            global whitelist
            params = params.split(" ")
            if len(params) < 3:
                print("[Whitelist] Wrong usage, usage: >>> whitelist <add/del> <SEGA ID>")
                return
            if params[1] == "add":
                if params[2] not in whitelist:
                    whitelist.append(params[2])
                    print("[Whitelist] %s added to the whitelist!" % params[2])
                    saveWhitelist()
                else:
                    print("[Whitelist] %s is already in the whitelist" % params[2])
            elif params[1] == "del":
                if params[2] in whitelist:
                    whitelist.remove(params[2])
                    print("[Whitelist] Removed %s from whitelist." % params[2])
                    saveWhitelist()
                else:
                    print("[Whitelist] %s is not in the whitelist, can not delete!" % params[2])
            else:
                print("[Whitelist] Wrong usage, usage: >>> whitelist <add/del> <SEGA ID>")

    @plugins.packetHook(0x11, 0x0)
    def whitelistCheck(context, data):
        global whitelist
        username = data[0x8:0x48].decode('utf-8')
        username = username.rstrip('\0')
        if username not in whitelist:
            print("[Whitelist] %s is not in the whitelist, hanging up!" % username)
            context.transport.loseConnection()
        return data