#!/bin/python


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
    print("Translate BUG: need handle for cmd %s" % msg.split()[0])
    return 0  # Unknown


def split_cmd_msg(message):
    cmd = ""
    msg = message
    if not message.strip() or message.strip() == "null":
        return (cmd, "")
    cmd, split, msg = message.rpartition("/")  # Let process that last command
    if split:
        args = need_switchs(msg)  # how many switchs does the last command need?
        msgl = msg.split(u" ", args + 1)   # let break apart msg strings into a list
        msg = msgl[len(msgl) - 1]  # the string at the end of the list is the text
        cmdl = []  # Start a new list, with cmd
        cmdl.extend(msgl[0:args + 1])  # Add the command and all the switchs
        cmd = split + u" ".join(cmdl)  # join the list into a string
    return (cmd, msg)


if __name__ == "__main__":
    print (split_cmd_msg("/mn16 doom keen hugs"))  # 0 extra swtich
    print (split_cmd_msg("/la sit1 doom keen hugs"))  # 1 extra swtich
    print (split_cmd_msg("/ci0 6 t6 nw s99 doom keen hugs"))  # up to 4
    print (split_cmd_msg("/ci0 6 t6 s99 doom keen hugs"))  # 3?
    print (split_cmd_msg(u"doom keen hugs"))  # no commands
