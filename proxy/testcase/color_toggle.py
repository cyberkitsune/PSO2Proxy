#!/bin/python


from PSO2DataTools import color_hide
from PSO2DataTools import color_show

if __name__ == "__main__":
    print (color_hide("doom keen hugs"))  # no colors
    print (color_show("doom keen hugs"))  # no colors
    print (color_hide("{red}doom{def}"))  # red and default
    print (color_show("_R_D_doom_D_F_"))  # red and default
