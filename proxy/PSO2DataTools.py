PSO2_IRC = [
("{red}"    ,r"\x03""04"), # Red

("{blu}"    ,r"\x03""02"), # Blue
("{blue}"   ,r"\x03""02"), # Blue

("{gre}"    ,r"\x03""03"), # green
("{green}"  ,r"\x03""03"), # green
("{grn}"    ,r"\x03""03"), # green
("{gree}"   ,r"\x03""03"), # green

("{yel}"    ,r"\x03""08"), # yellow
("{yellow}" ,r"\x03""08"), # yellow

("{ora}"   ,r"\x03""07"), # orange (olive)
("{orange}",r"\x03""07"), # orange (olive)
("{org}"   ,r"\x03""07"), # orange (olive)

("{pur}"   ,r"\x03""06"), # purple
("{purple}",r"\x03""06"), # purple
("{vir}"   ,r"\x03""06"), # purple

("{vio}"   ,r"\x03""13"), # Violet
("{violet}",r"\x03""13"), # Violet

("{bro}"   ,r"\x03""11"), # light purple?


("{bei}"   ,r"\x03""05"), # Beige
("{beige}" ,r"\x03""05"), # Beige

("{gra}"   ,r"\x03""14"), # grey
("{gray}"  ,r"\x03""14"), # grey
("{gra}"   ,r"\x03""14"), # grey
("{gry}"   ,r"\x03""14"), # grey
("{bla}"   ,r"\x03""14"), # grey
("{ble}"   ,r"\x03""14"), # grey
("{ble}"   ,r"\x03""14"), # grey
("{bra}"   ,r"\x03""14"), # grey

("{whi}"   ,r"\x03""00"), # white
("{white}" ,r"\x03""00"), # white
("{whit}"  ,r"\x03""00"), # white

("{blk}"   ,r"\x03""01"), # black
("{black}" ,r"\x03""01"), # black
("{pla}"   ,r"\x03""01"), # black

("{def}"   ,"\x0F"), # colour reset

("{orang}" , r"\x03""10"), # teal (a green/blue cyan)

("{yello}"  ,r"\x03""05"), # brown (maroon)
]

IRC_PSO2 = [
# Color text on white background
(r"\x03""0000","{whi}"), # white
(r"\x03""0100","{blk}"), # black
(r"\x03""0200","{blu}"), # blue (navy)
(r"\x03""0300","{gre}"), # green
(r"\x03""0400","{red}"), # red
(r"\x03""0500",""), # brown (maroon)
(r"\x03""0600","{pur}"), # purple
(r"\x03""0700","{ora}"), # orange (olive)
(r"\x03""0800","{yel}"), # yellow
(r"\x03""0900",""), # light green (lime)
(r"\x03""1000",""), # teal (a green/blue cyan)
(r"\x03""1100",""), # light cyan (cyan) (aqua)
(r"\x03""1200",""), # light blue (royal)
(r"\x03""1300","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1400","{gra}"), # grey
(r"\x03""1500",""), # light grey (silver)
(r"\x03""9900",""), # transparent
# Color text on black background
(r"\x03""0001","{whi}"), # white
(r"\x03""0101","{blk}"), # black
(r"\x03""0201","{blu}"), # blue (navy)
(r"\x03""0301","{gre}"), # green
(r"\x03""0401","{red}"), # red
(r"\x03""0501",""), # brown (maroon)
(r"\x03""0601","{pur}"), # purple
(r"\x03""0701","{ora}"), # orange (olive)
(r"\x03""0801","{yel}"), # yellow
(r"\x03""0901",""), # light green (lime)
(r"\x03""1001",""), # teal (a green/blue cyan)
(r"\x03""1101",""), # light cyan (cyan) (aqua)
(r"\x03""1201",""), # light blue (royal)
(r"\x03""1301","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1401","{gra}"), # grey
(r"\x03""1501",""), # light grey (silver)
(r"\x03""9901",""), # transparent
# Color text on blue background
(r"\x03""0002","{whi}"), # white
(r"\x03""0102","{blk}"), # black
(r"\x03""0202","{blu}"), # blue (navy)
(r"\x03""0302","{gre}"), # green
(r"\x03""0402","{red}"), # red
(r"\x03""0502",""), # brown (maroon)
(r"\x03""0602","{pur}"), # purple
(r"\x03""0702","{ora}"), # orange (olive)
(r"\x03""0802","{yel}"), # yellow
(r"\x03""0902",""), # light green (lime)
(r"\x03""1002",""), # teal (a green/blue cyan)
(r"\x03""1102",""), # light cyan (cyan) (aqua)
(r"\x03""1202",""), # light blue (royal)
(r"\x03""1302","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1402","{gra}"), # grey
(r"\x03""1502",""), # light grey (silver)
(r"\x03""9902",""), # transparent
# Color text on green background
(r"\x03""0003","{whi}"), # white
(r"\x03""0103","{blk}"), # black
(r"\x03""0203","{blu}"), # blue (navy)
(r"\x03""0303","{gre}"), # green
(r"\x03""0403","{red}"), # red
(r"\x03""0503",""), # brown (maroon)
(r"\x03""0603","{pur}"), # purple
(r"\x03""0703","{ora}"), # orange (olive)
(r"\x03""0803","{yel}"), # yellow
(r"\x03""0903",""), # light green (lime)
(r"\x03""1003",""), # teal (a green/blue cyan)
(r"\x03""1103",""), # light cyan (cyan) (aqua)
(r"\x03""1203",""), # light blue (royal)
(r"\x03""1303","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1403","{gra}"), # grey
(r"\x03""1503",""), # light grey (silver)
(r"\x03""9903",""), # transparent
# Color text on red background
(r"\x03""0004","{whi}"), # white
(r"\x03""0104","{blk}"), # black
(r"\x03""0204","{blu}"), # blue (navy)
(r"\x03""0304","{gre}"), # green
(r"\x03""0404","{red}"), # red
(r"\x03""0504",""), # brown (maroon)
(r"\x03""0604","{pur}"), # purple
(r"\x03""0704","{ora}"), # orange (olive)
(r"\x03""0804","{yel}"), # yellow
(r"\x03""0904",""), # light green (lime)
(r"\x03""1004",""), # teal (a green/blue cyan)
(r"\x03""1104",""), # light cyan (cyan) (aqua)
(r"\x03""1204",""), # light blue (royal)
(r"\x03""1304","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1404","{gra}"), # grey
(r"\x03""1504",""), # light grey (silver)
(r"\x03""9904",""), # transparent
# Color text on brown background
(r"\x03""0005","{whi}"), # white
(r"\x03""0105","{blk}"), # black
(r"\x03""0205","{blu}"), # blue (navy)
(r"\x03""0305","{gre}"), # green
(r"\x03""0405","{red}"), # red
(r"\x03""0505",""), # brown (maroon)
(r"\x03""0605","{pur}"), # purple
(r"\x03""0705","{ora}"), # orange (olive)
(r"\x03""0805","{yel}"), # yellow
(r"\x03""0905",""), # light green (lime)
(r"\x03""1005",""), # teal (a green/blue cyan)
(r"\x03""1105",""), # light cyan (cyan) (aqua)
(r"\x03""1205",""), # light blue (royal)
(r"\x03""1305","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1405","{gra}"), # grey
(r"\x03""1505",""), # light grey (silver)
(r"\x03""9905",""), # transparent
# Color text on purple background
(r"\x03""0006","{whi}"), # white
(r"\x03""0106","{blk}"), # black
(r"\x03""0206","{blu}"), # blue (navy)
(r"\x03""0306","{gre}"), # green
(r"\x03""0406","{red}"), # red
(r"\x03""0506",""), # brown (maroon)
(r"\x03""0606","{pur}"), # purple
(r"\x03""0706","{ora}"), # orange (olive)
(r"\x03""0806","{yel}"), # yellow
(r"\x03""0906",""), # light green (lime)
(r"\x03""1006",""), # teal (a green/blue cyan)
(r"\x03""1106",""), # light cyan (cyan) (aqua)
(r"\x03""1206",""), # light blue (royal)
(r"\x03""1306","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1406","{gra}"), # grey
(r"\x03""1506",""), # light grey (silver)
(r"\x03""9906",""), # transparent
# Color text on orange background
(r"\x03""0007","{whi}"), # white
(r"\x03""0107","{blk}"), # black
(r"\x03""0207","{blu}"), # blue (navy)
(r"\x03""0307","{gre}"), # green
(r"\x03""0407","{red}"), # red
(r"\x03""0507",""), # brown (maroon)
(r"\x03""0607","{pur}"), # purple
(r"\x03""0707","{ora}"), # orange (olive)
(r"\x03""0807","{yel}"), # yellow
(r"\x03""0907",""), # light green (lime)
(r"\x03""1007",""), # teal (a green/blue cyan)
(r"\x03""1107",""), # light cyan (cyan) (aqua)
(r"\x03""1207",""), # light blue (royal)
(r"\x03""1307","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1407","{gra}"), # grey
(r"\x03""1507",""), # light grey (silver)
(r"\x03""9907",""), # transparent
# Color text on light yelll background
(r"\x03""0008","{whi}"), # white
(r"\x03""0108","{blk}"), # black
(r"\x03""0208","{blu}"), # blue (navy)
(r"\x03""0308","{gre}"), # green
(r"\x03""0408","{red}"), # red
(r"\x03""0508",""), # brown (maroon)
(r"\x03""0608","{pur}"), # purple
(r"\x03""0708","{ora}"), # orange (olive)
(r"\x03""0808","{yel}"), # yellow
(r"\x03""0908",""), # light green (lime)
(r"\x03""1008",""), # teal (a green/blue cyan)
(r"\x03""1108",""), # light cyan (cyan) (aqua)
(r"\x03""1208",""), # light blue (royal)
(r"\x03""1308","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1408","{gra}"), # grey
(r"\x03""1508",""), # light grey (silver)
(r"\x03""9908",""), # transparent
# Color text on light green background
(r"\x03""0009","{whi}"), # white
(r"\x03""0109","{blk}"), # black
(r"\x03""0209","{blu}"), # blue (navy)
(r"\x03""0309","{gre}"), # green
(r"\x03""0409","{red}"), # red
(r"\x03""0509",""), # brown (maroon)
(r"\x03""0609","{pur}"), # purple
(r"\x03""0709","{ora}"), # orange (olive)
(r"\x03""0809","{yel}"), # yellow
(r"\x03""0909",""), # light green (lime)
(r"\x03""1009",""), # teal (a green/blue cyan)
(r"\x03""1109",""), # light cyan (cyan) (aqua)
(r"\x03""1209",""), # light blue (royal)
(r"\x03""1309","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1409","{gra}"), # grey
(r"\x03""1509",""), # light grey (silver)
(r"\x03""9909",""), # transparent
# Color text on teal background
(r"\x03""0010","{whi}"), # white
(r"\x03""0110","{blk}"), # black
(r"\x03""0210","{blu}"), # blue (navy)
(r"\x03""0310","{gre}"), # green
(r"\x03""0410","{red}"), # red
(r"\x03""0510",""), # brown (maroon)
(r"\x03""0610","{pur}"), # purple
(r"\x03""0710","{ora}"), # orange (olive)
(r"\x03""0810","{yel}"), # yellow
(r"\x03""0910",""), # light green (lime)
(r"\x03""1010",""), # teal (a green/blue cyan)
(r"\x03""1110",""), # light cyan (cyan) (aqua)
(r"\x03""1210",""), # light blue (royal)
(r"\x03""1310","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1410","{gra}"), # grey
(r"\x03""1510",""), # light grey (silver)
(r"\x03""9910",""), # transparent
# Color text on light cyan background
(r"\x03""0011","{whi}"), # white
(r"\x03""0111","{blk}"), # black
(r"\x03""0211","{blu}"), # blue (navy)
(r"\x03""0311","{gre}"), # green
(r"\x03""0411","{red}"), # red
(r"\x03""0511",""), # brown (maroon)
(r"\x03""0611","{pur}"), # purple
(r"\x03""0711","{ora}"), # orange (olive)
(r"\x03""0811","{yel}"), # yellow
(r"\x03""0911",""), # light green (lime)
(r"\x03""1011",""), # teal (a green/blue cyan)
(r"\x03""1111",""), # light cyan (cyan) (aqua)
(r"\x03""1211",""), # light blue (royal)
(r"\x03""1311","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1411","{gra}"), # grey
(r"\x03""1511",""), # light grey (silver)
(r"\x03""9911",""), # transparent
# Color text on light blue background
(r"\x03""0012","{whi}"), # white
(r"\x03""0112","{blk}"), # black
(r"\x03""0212","{blu}"), # blue (navy)
(r"\x03""0312","{gre}"), # green
(r"\x03""0412","{red}"), # red
(r"\x03""0512",""), # brown (maroon)
(r"\x03""0612","{pur}"), # purple
(r"\x03""0712","{ora}"), # orange (olive)
(r"\x03""0812","{yel}"), # yellow
(r"\x03""0912",""), # light green (lime)
(r"\x03""1012",""), # teal (a green/blue cyan)
(r"\x03""1112",""), # light cyan (cyan) (aqua)
(r"\x03""1212",""), # light blue (royal)
(r"\x03""1312","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1412","{gra}"), # grey
(r"\x03""1512",""), # light grey (silver)
(r"\x03""9912",""), # transparent
# Color text on pink background
(r"\x03""0013","{whi}"), # white
(r"\x03""0113","{blk}"), # black
(r"\x03""0213","{blu}"), # blue (navy)
(r"\x03""0313","{gre}"), # green
(r"\x03""0413","{red}"), # red
(r"\x03""0513",""), # brown (maroon)
(r"\x03""0613","{pur}"), # purple
(r"\x03""0713","{ora}"), # orange (olive)
(r"\x03""0813","{yel}"), # yellow
(r"\x03""0913",""), # light green (lime)
(r"\x03""1013",""), # teal (a green/blue cyan)
(r"\x03""1113",""), # light cyan (cyan) (aqua)
(r"\x03""1213",""), # light blue (royal)
(r"\x03""1313","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1413","{gra}"), # grey
(r"\x03""1513",""), # light grey (silver)
(r"\x03""9913",""), # transparent
# Color text on grey background
(r"\x03""0014","{whi}"), # white
(r"\x03""0114","{blk}"), # black
(r"\x03""0214","{blu}"), # blue (navy)
(r"\x03""0314","{gre}"), # green
(r"\x03""0414","{red}"), # red
(r"\x03""0514",""), # brown (maroon)
(r"\x03""0614","{pur}"), # purple
(r"\x03""0714","{ora}"), # orange (olive)
(r"\x03""0814","{yel}"), # yellow
(r"\x03""0914",""), # light green (lime)
(r"\x03""1014",""), # teal (a green/blue cyan)
(r"\x03""1114",""), # light cyan (cyan) (aqua)
(r"\x03""1214",""), # light blue (royal)
(r"\x03""1314","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1414","{gra}"), # grey
(r"\x03""1514",""), # light grey (silver)
(r"\x03""9914",""), # transparent
# Color text on silver background
(r"\x03""0015","{whi}"), # white
(r"\x03""0115","{blk}"), # black
(r"\x03""0215","{blu}"), # blue (navy)
(r"\x03""0315","{gre}"), # green
(r"\x03""0415","{red}"), # red
(r"\x03""0515",""), # brown (maroon)
(r"\x03""0615","{pur}"), # purple
(r"\x03""0715","{ora}"), # orange (olive)
(r"\x03""0815","{yel}"), # yellow
(r"\x03""0915",""), # light green (lime)
(r"\x03""1015",""), # teal (a green/blue cyan)
(r"\x03""1115",""), # light cyan (cyan) (aqua)
(r"\x03""1215",""), # light blue (royal)
(r"\x03""1315","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""1415","{gra}"), # grey
(r"\x03""1515",""), # light grey (silver)
(r"\x03""9915",""), # transparent
# Color text on default background
(r"\x03""00","{whi}"), # white
(r"\x03""01","{blk}"), # black
(r"\x03""02","{blu}"), # blue (navy)
(r"\x03""03","{gre}"), # green
(r"\x03""04","{red}"), # red
(r"\x03""05",""), # brown (maroon)
(r"\x03""06","{pur}"), # purple
(r"\x03""07","{ora}"), # orange (olive)
(r"\x03""08","{yel}"), # yellow
(r"\x03""09",""), # light green (lime)
(r"\x03""10",""), # teal (a green/blue cyan)
(r"\x03""11",""), # light cyan (cyan) (aqua)
(r"\x03""12",""), # light blue (royal)
(r"\x03""13","{vio}"), # pink (light purple) (fuchsia)
(r"\x03""14","{gra}"), # grey
(r"\x03""15",""), # light grey (silver)
(r"\x03""99",""), # transparent
# Format codes
("\x02",""), # bold
("\x1D",""), # italic text
("\x0F","{def}"), # colour reset
("\x16",""), # reverse colour
("\x1F",""), # underlined text
]

def replace_PSO2_with_IRC(pIncoming):

   lIncoming = unicode(pIncoming,'utf-8-sig')

   for couple in PSO2_IRC:
       outtext=lIncoming.replace(couple[0], couple[1])
       lIncoming=outtext

   return outtext.encode('utf-8-sig')

def replace_IRC_with_PSO2(pIncoming):

   lIncoming = unicode(pIncoming,'utf-8-sig')

   for couple in IRC_PSO2:
       outtext=lIncoming.replace(couple[0], couple[1])
       lIncoming=outtext

   return outtext.encode('utf-8-sig')
