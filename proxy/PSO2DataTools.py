PSO2_IRC = [
('{red}'    ,'\x0304'), # Red

('{blu}'    ,'\x0302'), # Blue
('{blue}'   ,'\x0302'), # Blue

('{gre}'    ,'\x0303'), # green
('{green}'  ,'\x0303'), # green
('{grn}'    ,'\x0303'), # green
('{gree}'   ,'\x0303'), # green

('{yel}'    ,'\x0308'), # yellow
('{yellow}' ,'\x0308'), # yellow

('{ora}'   ,'\x0307'), # orange (olive)
('{orange}','\x0307'), # orange (olive)
('{org}'   ,'\x0307'), # orange (olive)

('{pur}'   ,'\x0306'), # purple
('{purple}','\x0306'), # purple
('{vir}'   ,'\x0306'), # purple

('{vio}'   ,'\x0313'), # Violet
('{violet}','\x0313'), # Violet

('{bro}'   ,'\x0311'), # light purple?


('{bei}'   ,'\x0305'), # Beige
('{beige}' ,'\x0305'), # Beige

('{gra}'   ,'\x0314'), # grey
('{gray}'  ,'\x0314'), # grey
('{gra}'   ,'\x0314'), # grey
('{gry}'   ,'\x0314'), # grey
('{bla}'   ,'\x0314'), # grey
('{ble}'   ,'\x0314'), # grey
('{ble}'   ,'\x0314'), # grey
('{bra}'   ,'\x0314'), # grey

('{whi}'   ,'\x0300'), # white
('{white}' ,'\x0300'), # white
('{whit}'  ,'\x0300'), # white

('{blk}'   ,'\x0301'), # black
('{black}' ,'\x0301'), # black
('{pla}'   ,'\x0301'), # black

('{def}'   ,'\x0F'), # colour reset

('{orang}' , '\x0310'), # teal (a green/blue cyan)

('{yello}'  ,'\x0305'), # brown (maroon)
]

IRC_PSO2 = [
# Color text on white background
('\x030000','{whi}'), # white
('\x030100','{blk}'), # black
('\x030200','{blu}'), # blue (navy)
('\x030300','{gre}'), # green
('\x030400','{red}'), # red
('\x030500',''), # brown (maroon)
('\x030600','{pur}'), # purple
('\x030700','{ora}'), # orange (olive)
('\x030800','{yel}'), # yellow
('\x030900',''), # light green (lime)
('\x031000',''), # teal (a green/blue cyan)
('\x031100',''), # light cyan (cyan) (aqua)
('\x031200',''), # light blue (royal)
('\x031300','{vio}'), # pink (light purple) (fuchsia)
('\x031400','{gra}'), # grey
('\x031500',''), # light grey (silver)
('\x039900',''), # transparent
# Color text on black background
('\x030001','{whi}'), # white
('\x030101','{blk}'), # black
('\x030201','{blu}'), # blue (navy)
('\x030301','{gre}'), # green
('\x030401','{red}'), # red
('\x030501',''), # brown (maroon)
('\x030601','{pur}'), # purple
('\x030701','{ora}'), # orange (olive)
('\x030801','{yel}'), # yellow
('\x030901',''), # light green (lime)
('\x031001',''), # teal (a green/blue cyan)
('\x031101',''), # light cyan (cyan) (aqua)
('\x031201',''), # light blue (royal)
('\x031301','{vio}'), # pink (light purple) (fuchsia)
('\x031401','{gra}'), # grey
('\x031501',''), # light grey (silver)
('\x039901',''), # transparent
# Color text on blue background
('\x030002','{whi}'), # white
('\x030102','{blk}'), # black
('\x030202','{blu}'), # blue (navy)
('\x030302','{gre}'), # green
('\x030402','{red}'), # red
('\x030502',''), # brown (maroon)
('\x030602','{pur}'), # purple
('\x030702','{ora}'), # orange (olive)
('\x030802','{yel}'), # yellow
('\x030902',''), # light green (lime)
('\x031002',''), # teal (a green/blue cyan)
('\x031102',''), # light cyan (cyan) (aqua)
('\x031202',''), # light blue (royal)
('\x031302','{vio}'), # pink (light purple) (fuchsia)
('\x031402','{gra}'), # grey
('\x031502',''), # light grey (silver)
('\x039902',''), # transparent
# Color text on green background
('\x030003','{whi}'), # white
('\x030103','{blk}'), # black
('\x030203','{blu}'), # blue (navy)
('\x030303','{gre}'), # green
('\x030403','{red}'), # red
('\x030503',''), # brown (maroon)
('\x030603','{pur}'), # purple
('\x030703','{ora}'), # orange (olive)
('\x030803','{yel}'), # yellow
('\x030903',''), # light green (lime)
('\x031003',''), # teal (a green/blue cyan)
('\x031103',''), # light cyan (cyan) (aqua)
('\x031203',''), # light blue (royal)
('\x031303','{vio}'), # pink (light purple) (fuchsia)
('\x031403','{gra}'), # grey
('\x031503',''), # light grey (silver)
('\x039903',''), # transparent
# Color text on red background
('\x030004','{whi}'), # white
('\x030104','{blk}'), # black
('\x030204','{blu}'), # blue (navy)
('\x030304','{gre}'), # green
('\x030404','{red}'), # red
('\x030504',''), # brown (maroon)
('\x030604','{pur}'), # purple
('\x030704','{ora}'), # orange (olive)
('\x030804','{yel}'), # yellow
('\x030904',''), # light green (lime)
('\x031004',''), # teal (a green/blue cyan)
('\x031104',''), # light cyan (cyan) (aqua)
('\x031204',''), # light blue (royal)
('\x031304','{vio}'), # pink (light purple) (fuchsia)
('\x031404','{gra}'), # grey
('\x031504',''), # light grey (silver)
('\x039904',''), # transparent
# Color text on brown background
('\x030005','{whi}'), # white
('\x030105','{blk}'), # black
('\x030205','{blu}'), # blue (navy)
('\x030305','{gre}'), # green
('\x030405','{red}'), # red
('\x030505',''), # brown (maroon)
('\x030605','{pur}'), # purple
('\x030705','{ora}'), # orange (olive)
('\x030805','{yel}'), # yellow
('\x030905',''), # light green (lime)
('\x031005',''), # teal (a green/blue cyan)
('\x031105',''), # light cyan (cyan) (aqua)
('\x031205',''), # light blue (royal)
('\x031305','{vio}'), # pink (light purple) (fuchsia)
('\x031405','{gra}'), # grey
('\x031505',''), # light grey (silver)
('\x039905',''), # transparent
# Color text on purple background
('\x030006','{whi}'), # white
('\x030106','{blk}'), # black
('\x030206','{blu}'), # blue (navy)
('\x030306','{gre}'), # green
('\x030406','{red}'), # red
('\x030506',''), # brown (maroon)
('\x030606','{pur}'), # purple
('\x030706','{ora}'), # orange (olive)
('\x030806','{yel}'), # yellow
('\x030906',''), # light green (lime)
('\x031006',''), # teal (a green/blue cyan)
('\x031106',''), # light cyan (cyan) (aqua)
('\x031206',''), # light blue (royal)
('\x031306','{vio}'), # pink (light purple) (fuchsia)
('\x031406','{gra}'), # grey
('\x031506',''), # light grey (silver)
('\x039906',''), # transparent
# Color text on orange background
('\x030007','{whi}'), # white
('\x030107','{blk}'), # black
('\x030207','{blu}'), # blue (navy)
('\x030307','{gre}'), # green
('\x030407','{red}'), # red
('\x030507',''), # brown (maroon)
('\x030607','{pur}'), # purple
('\x030707','{ora}'), # orange (olive)
('\x030807','{yel}'), # yellow
('\x030907',''), # light green (lime)
('\x031007',''), # teal (a green/blue cyan)
('\x031107',''), # light cyan (cyan) (aqua)
('\x031207',''), # light blue (royal)
('\x031307','{vio}'), # pink (light purple) (fuchsia)
('\x031407','{gra}'), # grey
('\x031507',''), # light grey (silver)
('\x039907',''), # transparent
# Color text on light yelll background
('\x030008','{whi}'), # white
('\x030108','{blk}'), # black
('\x030208','{blu}'), # blue (navy)
('\x030308','{gre}'), # green
('\x030408','{red}'), # red
('\x030508',''), # brown (maroon)
('\x030608','{pur}'), # purple
('\x030708','{ora}'), # orange (olive)
('\x030808','{yel}'), # yellow
('\x030908',''), # light green (lime)
('\x031008',''), # teal (a green/blue cyan)
('\x031108',''), # light cyan (cyan) (aqua)
('\x031208',''), # light blue (royal)
('\x031308','{vio}'), # pink (light purple) (fuchsia)
('\x031408','{gra}'), # grey
('\x031508',''), # light grey (silver)
('\x039908',''), # transparent
# Color text on light green background
('\x030009','{whi}'), # white
('\x030109','{blk}'), # black
('\x030209','{blu}'), # blue (navy)
('\x030309','{gre}'), # green
('\x030409','{red}'), # red
('\x030509',''), # brown (maroon)
('\x030609','{pur}'), # purple
('\x030709','{ora}'), # orange (olive)
('\x030809','{yel}'), # yellow
('\x030909',''), # light green (lime)
('\x031009',''), # teal (a green/blue cyan)
('\x031109',''), # light cyan (cyan) (aqua)
('\x031209',''), # light blue (royal)
('\x031309','{vio}'), # pink (light purple) (fuchsia)
('\x031409','{gra}'), # grey
('\x031509',''), # light grey (silver)
('\x039909',''), # transparent
# Color text on teal background
('\x030010','{whi}'), # white
('\x030110','{blk}'), # black
('\x030210','{blu}'), # blue (navy)
('\x030310','{gre}'), # green
('\x030410','{red}'), # red
('\x030510',''), # brown (maroon)
('\x030610','{pur}'), # purple
('\x030710','{ora}'), # orange (olive)
('\x030810','{yel}'), # yellow
('\x030910',''), # light green (lime)
('\x031010',''), # teal (a green/blue cyan)
('\x031110',''), # light cyan (cyan) (aqua)
('\x031210',''), # light blue (royal)
('\x031310','{vio}'), # pink (light purple) (fuchsia)
('\x031410','{gra}'), # grey
('\x031510',''), # light grey (silver)
('\x039910',''), # transparent
# Color text on light cyan background
('\x030011','{whi}'), # white
('\x030111','{blk}'), # black
('\x030211','{blu}'), # blue (navy)
('\x030311','{gre}'), # green
('\x030411','{red}'), # red
('\x030511',''), # brown (maroon)
('\x030611','{pur}'), # purple
('\x030711','{ora}'), # orange (olive)
('\x030811','{yel}'), # yellow
('\x030911',''), # light green (lime)
('\x031011',''), # teal (a green/blue cyan)
('\x031111',''), # light cyan (cyan) (aqua)
('\x031211',''), # light blue (royal)
('\x031311','{vio}'), # pink (light purple) (fuchsia)
('\x031411','{gra}'), # grey
('\x031511',''), # light grey (silver)
('\x039911',''), # transparent
# Color text on light blue background
('\x030012','{whi}'), # white
('\x030112','{blk}'), # black
('\x030212','{blu}'), # blue (navy)
('\x030312','{gre}'), # green
('\x030412','{red}'), # red
('\x030512',''), # brown (maroon)
('\x030612','{pur}'), # purple
('\x030712','{ora}'), # orange (olive)
('\x030812','{yel}'), # yellow
('\x030912',''), # light green (lime)
('\x031012',''), # teal (a green/blue cyan)
('\x031112',''), # light cyan (cyan) (aqua)
('\x031212',''), # light blue (royal)
('\x031312','{vio}'), # pink (light purple) (fuchsia)
('\x031412','{gra}'), # grey
('\x031512',''), # light grey (silver)
('\x039912',''), # transparent
# Color text on pink background
('\x030013','{whi}'), # white
('\x030113','{blk}'), # black
('\x030213','{blu}'), # blue (navy)
('\x030313','{gre}'), # green
('\x030413','{red}'), # red
('\x030513',''), # brown (maroon)
('\x030613','{pur}'), # purple
('\x030713','{ora}'), # orange (olive)
('\x030813','{yel}'), # yellow
('\x030913',''), # light green (lime)
('\x031013',''), # teal (a green/blue cyan)
('\x031113',''), # light cyan (cyan) (aqua)
('\x031213',''), # light blue (royal)
('\x031313','{vio}'), # pink (light purple) (fuchsia)
('\x031413','{gra}'), # grey
('\x031513',''), # light grey (silver)
('\x039913',''), # transparent
# Color text on grey background
('\x030014','{whi}'), # white
('\x030114','{blk}'), # black
('\x030214','{blu}'), # blue (navy)
('\x030314','{gre}'), # green
('\x030414','{red}'), # red
('\x030514',''), # brown (maroon)
('\x030614','{pur}'), # purple
('\x030714','{ora}'), # orange (olive)
('\x030814','{yel}'), # yellow
('\x030914',''), # light green (lime)
('\x031014',''), # teal (a green/blue cyan)
('\x031114',''), # light cyan (cyan) (aqua)
('\x031214',''), # light blue (royal)
('\x031314','{vio}'), # pink (light purple) (fuchsia)
('\x031414','{gra}'), # grey
('\x031514',''), # light grey (silver)
('\x039914',''), # transparent
# Color text on silver background
('\x030015','{whi}'), # white
('\x030115','{blk}'), # black
('\x030215','{blu}'), # blue (navy)
('\x030315','{gre}'), # green
('\x030415','{red}'), # red
('\x030515',''), # brown (maroon)
('\x030615','{pur}'), # purple
('\x030715','{ora}'), # orange (olive)
('\x030815','{yel}'), # yellow
('\x030915',''), # light green (lime)
('\x031015',''), # teal (a green/blue cyan)
('\x031115',''), # light cyan (cyan) (aqua)
('\x031215',''), # light blue (royal)
('\x031315','{vio}'), # pink (light purple) (fuchsia)
('\x031415','{gra}'), # grey
('\x031515',''), # light grey (silver)
('\x039915',''), # transparent
# Color text on default background
('\x0300','{whi}'), # white
('\x0301','{blk}'), # black
('\x0302','{blu}'), # blue (navy)
('\x0303','{gre}'), # green
('\x0304','{red}'), # red
('\x0305',''), # brown (maroon)
('\x0306','{pur}'), # purple
('\x0307','{ora}'), # orange (olive)
('\x0308','{yel}'), # yellow
('\x0309',''), # light green (lime)
('\x0310',''), # teal (a green/blue cyan)
('\x0311',''), # light cyan (cyan) (aqua)
('\x0312',''), # light blue (royal)
('\x0313','{vio}'), # pink (light purple) (fuchsia)
('\x0314','{gra}'), # grey
('\x0315',''), # light grey (silver)
('\x0399',''), # transparent
# Format codes
('\x02',''), # bold
('\x1D',''), # italic text
('\x0F','{def}'), # colour reset
('\x16',''), # reverse colour
('\x1F',''), # underlined text
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
