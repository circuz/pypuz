import sys
import curses
import readpuz as rp


def highlight(scr: curses.window, puz: rp.Puzzle, y, x, dir):
    if puz.player_state[y][x] == ord('.'):
        return
    elif dir == 0:
        i = 1
        j = 0
        while (i < (puz.width-x)) and (puz.player_state[y+j][x+i] != ord('.')):
            c = chr(scr.inch(y+j, x+i))
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # fst
            i += 1
        i = -1
        j = 0
        while (i > -x-1) and (puz.player_state[y+j][x+i] != ord('.')):
            c = chr(scr.inch(y+j, x+i))
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # snd
            i -= 1
    else:
        i = 0
        j = 1
        while (j < (puz.height-y)) and (puz.player_state[y+j][x+i] != ord('.')):
            c = chr(scr.inch(y+j, x+i))
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # fst
            j += 1
        i = 0
        j = -1
        while (j > -y-1) and (puz.player_state[y+j][x+i] != ord('.')):
            c = chr(scr.inch(y+j, x+i))
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # snd
            j -= 1
    return


def main(stdscr):
    if len(sys.argv) != 2:
        stdscr.addstr("Usage: python pypuz.py [.PUZ FILENAME]")
        stdscr.getkey()
        return

    puzzle = rp.Puzzle(sys.argv[1])

    stdscr.addstr(puzzle.title + b' - ' + puzzle.author + b'\n')
    stdscr.addstr(puzzle.notes + b'\n')

    bwidth = puzzle.width
    bheight = puzzle.height
    # wx = curses.COLS // 2 - bwidth # this can replace 1 in board = [...] , 1)
    wy = (curses.LINES - bheight) // 2
    board = curses.newwin(bheight, bwidth, wy, 1)
    boarder = curses.newwin(bheight + 2, bwidth + 2, wy - 1, 0)
    boarder.border(0, 0, 0, 0, 0, 0, 0, 0)
    belowboarder = wy + bheight + 1

    # Draw player state
    for i, row in enumerate(puzzle.player_state):
        for j, b in enumerate(row):
            if b == ord('.'):
                board.insstr(i, j, u'\u2588')
            else:
                board.insstr(i, j, chr(b))
    board.move(8, 8)
    stdscr.refresh()
    boarder.refresh()
    board.refresh()

    # Create window object; size is whole stdscreen
    stdscr.keypad(True)

    # Initializing variables for game loop
    dir = 0  # 0 for across, 1 for down
    while True:
        y, x = board.getyx()
        for i, row in enumerate(puzzle.player_state):
            for j, b in enumerate(row):
                if b == ord('.'):
                    board.insstr(i, j, u'\u2588')
                else:
                    board.insstr(i, j, chr(b))
        board.move(y, x)
        # read character from keyboard
        c = stdscr.getkey()
        # ASCII int -> character
        match c:
            case "KEY_BACKSPACE":
                break
            case " ":
                dir = 1 - dir
            case "KEY_UP":
                dir = 1
                if y > 0:
                    board.move(y-1, x)
            case "KEY_DOWN":
                dir = 1
                if y < bheight - 1:
                    board.move(y+1, x)
            case "KEY_LEFT":
                dir = 0
                if x > 0:
                    board.move(y, x-1)
            case "KEY_RIGHT":
                dir = 0
                if x < bwidth - 1:
                    board.move(y, x+1)

        y, x = board.getyx()
        highlight(board, puzzle, y, x, dir)
        board.move(y, x)

        # Draw currclue
        stdscr.addstr(belowboarder, 1, puzzle.cluedict[(x, y)][dir])

        stdscr.refresh()
        boarder.refresh()
        board.refresh()
    stdscr.keypad(False)


curses.wrapper(main)
