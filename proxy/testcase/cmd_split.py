#!/bin/python


from PSO2DataTools import split_cmd_msg

if __name__ == "__main__":
    print (split_cmd_msg("/mn16 doom keen hugs"))  # 0 extra swtich
    print (split_cmd_msg("/mn16  "))  # command with no text
    print (split_cmd_msg("/la sit1 doom keen hugs"))  # 1 extra swtich
    print (split_cmd_msg("/ci0 6 t6 nw s99 doom keen hugs"))  # up to 4
    print (split_cmd_msg("/ci0 6 t6 s99 doom keen hugs"))  # 3?
    print (split_cmd_msg("/ci0 6 t6 s99 /doom/keen/hugs"))  # 3 with bad commands
    print (split_cmd_msg(u"doom keen hugs"))  # no commands
