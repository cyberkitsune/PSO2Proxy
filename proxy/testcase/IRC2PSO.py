#!/bin/python
import sys
from PSO2DataTools import replace_irc_with_pso2

f = sys.stdin


#    Usage: echo -e "\000308yellow" | python ./IRC2PSO.py
def main():
    global f
    if len(sys.argv) > 1:
        f = open(sys.argv[1])

for line in f:
    replace_irc_with_pso2(line, 1)

if __name__ == "__main__":
    main()
