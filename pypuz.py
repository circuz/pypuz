import sys
import curses
# import numpy as np
import readpuz as rp


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pypuz.py [.PUZ FILENAME]")
    else:
        cluedict = rp.readpuz(sys.argv[1])
        print(cluedict)
