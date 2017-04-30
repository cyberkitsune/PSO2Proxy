# Should this file even be in here?
# -*- coding: utf-8 -*-
from twisted.python import log

PSO2_IRC = [
    ("{red}", "\x03""04"),  # Red

    ("{blu}", "\x03""02"),  # Blue
    ("{blue}", "\x03""02"),  # Blue

    ("{gre}", "\x03""03"),  # green
    ("{green}", "\x03""03"),  # green
    ("{grn}", "\x03""03"),  # green
    ("{gree}", "\x03""03"),  # green

    ("{yel}", "\x03""08"),  # yellow
    ("{yellow}", "\x03""08"),  # yellow

    ("{ora}", "\x03""07"),  # orange (olive)
    ("{orange}", "\x03""07"),  # orange (olive)
    ("{org}", "\x03""07"),  # orange (olive)

    ("{pur}", "\x03""06"),  # purple
    ("{purple}", "\x03""06"),  # purple
    ("{vir}", "\x03""06"),  # purple

    ("{vio}", "\x03""13"),  # Violet
    ("{violet}", "\x03""13"),  # Violet

    ("{bei}", "\x03""05"),  # Beige
    ("{beige}", "\x03""05"),  # Beige

    ("{gra}", "\x03""14"),  # grey
    ("{gray}", "\x03""14"),  # grey
    ("{gra}", "\x03""14"),  # grey
    ("{gry}", "\x03""14"),  # grey
    ("{bla}", "\x03""14"),  # grey
    ("{ble}", "\x03""14"),  # grey
    ("{bra}", "\x03""14"),  # grey

    ("{whi}", "\x03""00"),  # white
    ("{white}", "\x03""00"),  # white
    ("{whit}", "\x03""00"),  # white

    ("{blk}", "\x03""01"),  # black
    ("{black}", "\x03""01"),  # black
    ("{pla}", "\x03""01"),  # black

    ("{def}", "\x0F"),  # colour reset
]

IRC_PSO2 = [
    # Color text on white background
    ("\x03""00,00", "{whi}"),  # white
    ("\x03""01,00", "{blk}"),  # black
    ("\x03""02,00", "{blu}"),  # blue (navy)
    ("\x03""03,00", "{gre}"),  # green
    ("\x03""04,00", "{red}"),  # red
    ("\x03""05,00", ""),  # brown (maroon)
    ("\x03""06,00", "{pur}"),  # purple
    ("\x03""07,00", "{ora}"),  # orange (olive)
    ("\x03""08,00", "{yel}"),  # yellow
    ("\x03""09,00", ""),  # light green (lime)
    ("\x03""10,00", ""),  # teal (a green/blue cyan)
    ("\x03""11,00", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,00", ""),  # light blue (royal)
    ("\x03""13,00", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,00", "{gra}"),  # grey
    ("\x03""15,00", ""),  # light grey (silver)
    ("\x03""99,00", ""),  # transparent
    # Color text on black background
    ("\x03""00,01", "{whi}"),  # white
    ("\x03""01,01", "{blk}"),  # black
    ("\x03""02,01", "{blu}"),  # blue (navy)
    ("\x03""03,01", "{gre}"),  # green
    ("\x03""04,01", "{red}"),  # red
    ("\x03""05,01", ""),  # brown (maroon)
    ("\x03""06,01", "{pur}"),  # purple
    ("\x03""07,01", "{ora}"),  # orange (olive)
    ("\x03""08,01", "{yel}"),  # yellow
    ("\x03""09,01", ""),  # light green (lime)
    ("\x03""10,01", ""),  # teal (a green/blue cyan)
    ("\x03""11,01", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,01", ""),  # light blue (royal)
    ("\x03""13,01", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,01", "{gra}"),  # grey
    ("\x03""15,01", ""),  # light grey (silver)
    ("\x03""99,01", ""),  # transparent
    # Color text on blue background
    ("\x03""00,02", "{whi}"),  # white
    ("\x03""01,02", "{blk}"),  # black
    ("\x03""02,02", "{blu}"),  # blue (navy)
    ("\x03""03,02", "{gre}"),  # green
    ("\x03""04,02", "{red}"),  # red
    ("\x03""05,02", ""),  # brown (maroon)
    ("\x03""06,02", "{pur}"),  # purple
    ("\x03""07,02", "{ora}"),  # orange (olive)
    ("\x03""08,02", "{yel}"),  # yellow
    ("\x03""09,02", ""),  # light green (lime)
    ("\x03""10,02", ""),  # teal (a green/blue cyan)
    ("\x03""11,02", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,02", ""),  # light blue (royal)
    ("\x03""13,02", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,02", "{gra}"),  # grey
    ("\x03""15,02", ""),  # light grey (silver)
    ("\x03""99,02", ""),  # transparent
    # Color text on green background
    ("\x03""00,03", "{whi}"),  # white
    ("\x03""01,03", "{blk}"),  # black
    ("\x03""02,03", "{blu}"),  # blue (navy)
    ("\x03""03,03", "{gre}"),  # green
    ("\x03""04,03", "{red}"),  # red
    ("\x03""05,03", ""),  # brown (maroon)
    ("\x03""06,03", "{pur}"),  # purple
    ("\x03""07,03", "{ora}"),  # orange (olive)
    ("\x03""08,03", "{yel}"),  # yellow
    ("\x03""09,03", ""),  # light green (lime)
    ("\x03""10,03", ""),  # teal (a green/blue cyan)
    ("\x03""11,03", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,03", ""),  # light blue (royal)
    ("\x03""13,03", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,03", "{gra}"),  # grey
    ("\x03""15,03", ""),  # light grey (silver)
    ("\x03""99,03", ""),  # transparent
    # Color text on red background
    ("\x03""00,04", "{whi}"),  # white
    ("\x03""01,04", "{blk}"),  # black
    ("\x03""02,04", "{blu}"),  # blue (navy)
    ("\x03""03,04", "{gre}"),  # green
    ("\x03""04,04", "{red}"),  # red
    ("\x03""05,04", ""),  # brown (maroon)
    ("\x03""06,04", "{pur}"),  # purple
    ("\x03""07,04", "{ora}"),  # orange (olive)
    ("\x03""08,04", "{yel}"),  # yellow
    ("\x03""09,04", ""),  # light green (lime)
    ("\x03""10,04", ""),  # teal (a green/blue cyan)
    ("\x03""11,04", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,04", ""),  # light blue (royal)
    ("\x03""13,04", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,04", "{gra}"),  # grey
    ("\x03""15,04", ""),  # light grey (silver)
    ("\x03""99,04", ""),  # transparent
    # Color text on brown background
    ("\x03""00,05", "{whi}"),  # white
    ("\x03""01,05", "{blk}"),  # black
    ("\x03""02,05", "{blu}"),  # blue (navy)
    ("\x03""03,05", "{gre}"),  # green
    ("\x03""04,05", "{red}"),  # red
    ("\x03""05,05", ""),  # brown (maroon)
    ("\x03""06,05", "{pur}"),  # purple
    ("\x03""07,05", "{ora}"),  # orange (olive)
    ("\x03""08,05", "{yel}"),  # yellow
    ("\x03""09,05", ""),  # light green (lime)
    ("\x03""10,05", ""),  # teal (a green/blue cyan)
    ("\x03""11,05", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,05", ""),  # light blue (royal)
    ("\x03""13,05", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,05", "{gra}"),  # grey
    ("\x03""15,05", ""),  # light grey (silver)
    ("\x03""99,05", ""),  # transparent
    # Color text on purple background
    ("\x03""00,06", "{whi}"),  # white
    ("\x03""01,06", "{blk}"),  # black
    ("\x03""02,06", "{blu}"),  # blue (navy)
    ("\x03""03,06", "{gre}"),  # green
    ("\x03""04,06", "{red}"),  # red
    ("\x03""05,06", ""),  # brown (maroon)
    ("\x03""06,06", "{pur}"),  # purple
    ("\x03""07,06", "{ora}"),  # orange (olive)
    ("\x03""08,06", "{yel}"),  # yellow
    ("\x03""09,06", ""),  # light green (lime)
    ("\x03""10,06", ""),  # teal (a green/blue cyan)
    ("\x03""11,06", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,06", ""),  # light blue (royal)
    ("\x03""13,06", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,06", "{gra}"),  # grey
    ("\x03""15,06", ""),  # light grey (silver)
    ("\x03""99,06", ""),  # transparent
    # Color text on orange background
    ("\x03""00,07", "{whi}"),  # white
    ("\x03""01,07", "{blk}"),  # black
    ("\x03""02,07", "{blu}"),  # blue (navy)
    ("\x03""03,07", "{gre}"),  # green
    ("\x03""04,07", "{red}"),  # red
    ("\x03""05,07", ""),  # brown (maroon)
    ("\x03""06,07", "{pur}"),  # purple
    ("\x03""07,07", "{ora}"),  # orange (olive)
    ("\x03""08,07", "{yel}"),  # yellow
    ("\x03""09,07", ""),  # light green (lime)
    ("\x03""10,07", ""),  # teal (a green/blue cyan)
    ("\x03""11,07", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,07", ""),  # light blue (royal)
    ("\x03""13,07", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,07", "{gra}"),  # grey
    ("\x03""15,07", ""),  # light grey (silver)
    ("\x03""99,07", ""),  # transparent
    # Color text on light yelll background
    ("\x03""00,08", "{whi}"),  # white
    ("\x03""01,08", "{blk}"),  # black
    ("\x03""02,08", "{blu}"),  # blue (navy)
    ("\x03""03,08", "{gre}"),  # green
    ("\x03""04,08", "{red}"),  # red
    ("\x03""05,08", ""),  # brown (maroon)
    ("\x03""06,08", "{pur}"),  # purple
    ("\x03""07,08", "{ora}"),  # orange (olive)
    ("\x03""08,08", "{yel}"),  # yellow
    ("\x03""09,08", ""),  # light green (lime)
    ("\x03""10,08", ""),  # teal (a green/blue cyan)
    ("\x03""11,08", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,08", ""),  # light blue (royal)
    ("\x03""13,08", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,08", "{gra}"),  # grey
    ("\x03""15,08", ""),  # light grey (silver)
    ("\x03""99,08", ""),  # transparent
    # Color text on light green background
    ("\x03""00,09", "{whi}"),  # white
    ("\x03""01,09", "{blk}"),  # black
    ("\x03""02,09", "{blu}"),  # blue (navy)
    ("\x03""03,09", "{gre}"),  # green
    ("\x03""04,09", "{red}"),  # red
    ("\x03""05,09", ""),  # brown (maroon)
    ("\x03""06,09", "{pur}"),  # purple
    ("\x03""07,09", "{ora}"),  # orange (olive)
    ("\x03""08,09", "{yel}"),  # yellow
    ("\x03""09,09", ""),  # light green (lime)
    ("\x03""10,09", ""),  # teal (a green/blue cyan)
    ("\x03""11,09", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,09", ""),  # light blue (royal)
    ("\x03""13,09", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,09", "{gra}"),  # grey
    ("\x03""15,09", ""),  # light grey (silver)
    ("\x03""99,09", ""),  # transparent
    # Color text on teal background
    ("\x03""00,10", "{whi}"),  # white
    ("\x03""01,10", "{blk}"),  # black
    ("\x03""02,10", "{blu}"),  # blue (navy)
    ("\x03""03,10", "{gre}"),  # green
    ("\x03""04,10", "{red}"),  # red
    ("\x03""05,10", ""),  # brown (maroon)
    ("\x03""06,10", "{pur}"),  # purple
    ("\x03""07,10", "{ora}"),  # orange (olive)
    ("\x03""08,10", "{yel}"),  # yellow
    ("\x03""09,10", ""),  # light green (lime)
    ("\x03""10,10", ""),  # teal (a green/blue cyan)
    ("\x03""11,10", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,10", ""),  # light blue (royal)
    ("\x03""13,10", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,10", "{gra}"),  # grey
    ("\x03""15,10", ""),  # light grey (silver)
    ("\x03""99,10", ""),  # transparent
    # Color text on light cyan background
    ("\x03""00,11", "{whi}"),  # white
    ("\x03""01,11", "{blk}"),  # black
    ("\x03""02,11", "{blu}"),  # blue (navy)
    ("\x03""03,11", "{gre}"),  # green
    ("\x03""04,11", "{red}"),  # red
    ("\x03""05,11", ""),  # brown (maroon)
    ("\x03""06,11", "{pur}"),  # purple
    ("\x03""07,11", "{ora}"),  # orange (olive)
    ("\x03""08,11", "{yel}"),  # yellow
    ("\x03""09,11", ""),  # light green (lime)
    ("\x03""10,11", ""),  # teal (a green/blue cyan)
    ("\x03""11,11", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,11", ""),  # light blue (royal)
    ("\x03""13,11", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,11", "{gra}"),  # grey
    ("\x03""15,11", ""),  # light grey (silver)
    ("\x03""99,11", ""),  # transparent
    # Color text on light blue background
    ("\x03""00,12", "{whi}"),  # white
    ("\x03""01,12", "{blk}"),  # black
    ("\x03""02,12", "{blu}"),  # blue (navy)
    ("\x03""03,12", "{gre}"),  # green
    ("\x03""04,12", "{red}"),  # red
    ("\x03""05,12", ""),  # brown (maroon)
    ("\x03""06,12", "{pur}"),  # purple
    ("\x03""07,12", "{ora}"),  # orange (olive)
    ("\x03""08,12", "{yel}"),  # yellow
    ("\x03""09,12", ""),  # light green (lime)
    ("\x03""10,12", ""),  # teal (a green/blue cyan)
    ("\x03""11,12", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,12", ""),  # light blue (royal)
    ("\x03""13,12", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,12", "{gra}"),  # grey
    ("\x03""15,12", ""),  # light grey (silver)
    ("\x03""99,12", ""),  # transparent
    # Color text on pink background
    ("\x03""00,13", "{whi}"),  # white
    ("\x03""01,13", "{blk}"),  # black
    ("\x03""02,13", "{blu}"),  # blue (navy)
    ("\x03""03,13", "{gre}"),  # green
    ("\x03""04,13", "{red}"),  # red
    ("\x03""05,13", ""),  # brown (maroon)
    ("\x03""06,13", "{pur}"),  # purple
    ("\x03""07,13", "{ora}"),  # orange (olive)
    ("\x03""08,13", "{yel}"),  # yellow
    ("\x03""09,13", ""),  # light green (lime)
    ("\x03""10,13", ""),  # teal (a green/blue cyan)
    ("\x03""11,13", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,13", ""),  # light blue (royal)
    ("\x03""13,13", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,13", "{gra}"),  # grey
    ("\x03""15,13", ""),  # light grey (silver)
    ("\x03""99,13", ""),  # transparent
    # Color text on grey background
    ("\x03""00,14", "{whi}"),  # white
    ("\x03""01,14", "{blk}"),  # black
    ("\x03""02,14", "{blu}"),  # blue (navy)
    ("\x03""03,14", "{gre}"),  # green
    ("\x03""04,14", "{red}"),  # red
    ("\x03""05,14", ""),  # brown (maroon)
    ("\x03""06,14", "{pur}"),  # purple
    ("\x03""07,14", "{ora}"),  # orange (olive)
    ("\x03""08,14", "{yel}"),  # yellow
    ("\x03""09,14", ""),  # light green (lime)
    ("\x03""10,14", ""),  # teal (a green/blue cyan)
    ("\x03""11,14", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,14", ""),  # light blue (royal)
    ("\x03""13,14", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,14", "{gra}"),  # grey
    ("\x03""15,14", ""),  # light grey (silver)
    ("\x03""99,14", ""),  # transparent
    # Color text on silver background
    ("\x03""00,15", "{whi}"),  # white
    ("\x03""01,15", "{blk}"),  # black
    ("\x03""02,15", "{blu}"),  # blue (navy)
    ("\x03""03,15", "{gre}"),  # green
    ("\x03""04,15", "{red}"),  # red
    ("\x03""05,15", ""),  # brown (maroon)
    ("\x03""06,15", "{pur}"),  # purple
    ("\x03""07,15", "{ora}"),  # orange (olive)
    ("\x03""08,15", "{yel}"),  # yellow
    ("\x03""09,15", ""),  # light green (lime)
    ("\x03""10,15", ""),  # teal (a green/blue cyan)
    ("\x03""11,15", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,15", ""),  # light blue (royal)
    ("\x03""13,15", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,15", "{gra}"),  # grey
    ("\x03""15,15", ""),  # light grey (silver)
    ("\x03""99,15", ""),  # transparent
    # Color text on restored defaulted background
    ("\x03""00,", "{whi}"),  # white
    ("\x03""01,", "{blk}"),  # black
    ("\x03""02,", "{blu}"),  # blue (navy)
    ("\x03""03,", "{gre}"),  # green
    ("\x03""04,", "{red}"),  # red
    ("\x03""05,", ""),  # brown (maroon)
    ("\x03""06,", "{pur}"),  # purple
    ("\x03""07,", "{ora}"),  # orange (olive)
    ("\x03""08,", "{yel}"),  # yellow
    ("\x03""09,", ""),  # light green (lime)
    ("\x03""10,", ""),  # teal (a green/blue cyan)
    ("\x03""11,", ""),  # light cyan (cyan) (aqua)
    ("\x03""12,", ""),  # light blue (royal)
    ("\x03""13,", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14,", "{gra}"),  # grey
    ("\x03""15,", ""),  # light grey (silver)
    ("\x03""99,", ""),  # transparent
    # Color text on default background
    ("\x03""00", "{whi}"),  # white
    ("\x03""01", "{blk}"),  # black
    ("\x03""02", "{blu}"),  # blue (navy)
    ("\x03""03", "{gre}"),  # green
    ("\x03""04", "{red}"),  # red
    ("\x03""05", ""),  # brown (maroon)
    ("\x03""06", "{pur}"),  # purple
    ("\x03""07", "{ora}"),  # orange (olive)
    ("\x03""08", "{yel}"),  # yellow
    ("\x03""09", ""),  # light green (lime)
    ("\x03""10", ""),  # teal (a green/blue cyan)
    ("\x03""11", ""),  # light cyan (cyan) (aqua)
    ("\x03""12", ""),  # light blue (royal)
    ("\x03""13", "{vio}"),  # pink (light purple) (fuchsia)
    ("\x03""14", "{gra}"),  # grey
    ("\x03""15", ""),  # light grey (silver)
    ("\x03""99", ""),  # transparent
    # Format codes
    ("\x02", ""),  # bold
    ("\x03,", "{def}"),  # no more color
    ("\x03", "{def}"),  # no more color
    ("\x1D", ""),  # italic text
    ("\x0F", "{def}"),  # colour reset
    ("\x16", ""),  # reverse colour
    ("\x1F", ""),  # underlined text
    # drop other control chars
    ("\x04", ""),
    ("\x05", ""),
    ("\x06", ""),
    ("\x07", ""),
    ("\x08", ""),
    ("\x09", ""),
    ("\x0A", ""),
    ("\x0B", ""),
    ("\x0C", ""),
    ("\x0D", ""),
    ("\x0E", ""),
    ("\x10", ""),
    ("\x11", ""),
    ("\x12", ""),
    ("\x13", ""),
    ("\x14", ""),
    ("\x15", ""),
    ("\x17", ""),
    ("\x18", ""),
    ("\x19", ""),
    ("\x1A", ""),
    ("\x1B", ""),
    ("\x1C", ""),
    ("\x1E", ""),
]

Bad_Unicode = [
    "👌",
    "👉 ",
    "👏",
    "🤔",
    "👀",
    "🏿",
    "👁️‍🗨️",
    "😠",
    "👁️",
    "🔥",
]


def replace_with_table(pIncoming, table, debug=0, check=0):
    if isinstance(pIncoming, str):
        lIncoming = unicode(pIncoming, 'utf-8-sig', 'replace')
    else:
        lIncoming = pIncoming

    if debug > 0:
        print ("Incoming object:  {}".format(repr(pIncoming)))
        print ("Incoming unicode: {}".format(repr(lIncoming)))

    if (check):
        for i, o in table:
            outtext = lIncoming.replace(i, "")
            lIncoming = outtext
    else:
        for i, o in table:
            outtext = lIncoming.replace(i, o)
            lIncoming = outtext

    if (check):
        lIncoming = lIncoming.strip()

    if isinstance(pIncoming, str):
        outtext = lIncoming.encode('utf-8', 'replace')
        for i in Bad_Unicode:
            outtext = outtext.replace(i, "")
    else:
        outtext = lIncoming.rstrip('\x00')

    if debug > 0:
        print ("Outgoing replace: {}".format(repr(lIncoming)))
        print ("Outgoing string:  {}".format(repr(outtext)))

    return outtext


def check_pso2_with_irc(pIncoming, debug=0):
    return replace_with_table(pIncoming, PSO2_IRC, debug, check=1)


def check_irc_with_pso2(pIncoming, debug=0):
    return replace_with_table(pIncoming, IRC_PSO2, debug, check=1)


def replace_pso2_with_irc(pIncoming, debug=0):
    return replace_with_table(pIncoming, PSO2_IRC, debug)


def replace_irc_with_pso2(pIncoming, debug=0):
    return replace_with_table(pIncoming, IRC_PSO2, debug)


def ci_switchs(cmd):  # decode /ci[1-9] {[1-5]} {t[1-5]} {nw} {s[0-99]}
    count = 0
    cmdl = cmd.split(" ", 5)
    lcmd = len(cmdl)
    if lcmd == count + 1:
        return count
    if not (cmdl[count + 1]):
        return count
    if cmdl[count + 1].isdigit():
        count += 1
    if lcmd == count + 1:
        return count
    try:
        if cmdl[count + 1][0] == "t":
            count += 1
    except Exception:
        log.msg("issue with ci string: %s" % cmd)
        return count
    if lcmd == count + 1:
        return count
    if cmdl[count + 1] == "nw":
        count += 1
    if lcmd == count + 1:
        return count
    if cmdl[count + 1][0] == "s":
        count += 1
    return count

PSO2_Commands = [
    # Text Bubble Emotes
    ("toge", 0),
    ("moya", 0),
    ("mn", 0),  # (mn#)
    # Switch Main Palette (mpal#)
    ("mainpalette", 0),
    ("mpal", 0),
    ("subpalette", 0),
    ("spal", 0),
    # Switch Consume %1
    ("costume", 1),
    ("cs", 1),
    # Switch Camos %1
    ("camouflage", 1),
    ("cmf", 1),
    # Lobby action %1
    ("la", 1),
    ("mla", 1),
    ("fla", 1),
    ("cla", 1),
    # Symbol Art (symbol#)
    ("symbol", 0),
    # Voice Clip (vo#)
    ("vo", 0),
    # All chat
    ("a", 0),
    # Party chat
    ("p", 0),
    # Team Chat
    ("t", 0),
    # EOL
]


def need_switchs(msg):  # return the max number of swtichs for the command
    for s, n in PSO2_Commands:
        if msg.startswith(s):
            return n
    if msg.startswith("ci"):
        return ci_switchs(msg)  # Cut-ins need special handling
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
            msg += u" "
            msgl = msg.split(u" ", args + 1)   # let break apart msg strings into a list
            msg = msgl[-1]  # the string at the end of the list is the text
            cmdl = []  # Start a new list, with cmd
            cmdl.extend(msgl[0:args + 1])  # Add the command and all the switchs
            cmd = split + u" ".join(cmdl)  # join the list into a string
            if cmd and msg.rstrip():
                cmd += u" "
    return (cmd, msg.rstrip())
