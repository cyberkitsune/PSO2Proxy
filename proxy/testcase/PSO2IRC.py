#!/bin/python
import sys
from PSO2DataTools import replace_pso2_with_irc

f = sys.stdin


#    Usage: echo {yel}yel{green}green | python ./PSO2IRC.py
def main():
    global f
    if len(sys.argv) > 1:
        f = open(sys.argv[1])

for line in f:
    replace_pso2_with_irc(line, 1)

if __name__ == "__main__":
    main()
