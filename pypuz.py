import sys
import curses
# import numpy as np
import readpuz as rp


def draw(char):
    pass


def restorescreen():
    curses.nocbreak()
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pypuz.py [.PUZ FILENAME]")
        exit()

    # metadata = across, down,
    puzzle = rp.Puzzle(sys.argv[1])
    print(puzzle.cluedict)
    for clue in puzzle.across:
        print(clue)
    for clue in puzzle.down:
        print(clue)

    # Create window object; size is whole screen
    scrn = curses.initscr()
    # turn off keystroke echo
    curses.noecho()
    # no need to press enter after key
    curses.cbreak()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    scrn.clear()
    while False:
        # read character from keyboard
        c = scrn.getch()
        # ASCII int -> character
        c = chr(c)
        if c == 'q':
            break
        draw(c)
    restorescreen()
