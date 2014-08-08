#/bin/python
import sys
from PSO2DataTools import replace_irc_with_pso2, replace_pso2_with_irc

# echo {yel}yel{green}green | python ./PSO2IRC.py
def main():
   f = sys.stdin
   if len(sys.argv) > 1:
      f = open(sys.argv[1])

for line in sys.stdin:
     replace_pso2_with_irc(line, 1)

if __name__ == "__main__":
    main()
