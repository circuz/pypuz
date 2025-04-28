import sys
import curses
import readpuz as rp


def write_move(puz: rp.Puzzle, x: int, y: int, k: str, dir: bool):
    # write to the screen and then move to the next non-written square
    # following the correct direction
    puz.write(x, y, k)
    i = x
    j = y
    if dir:
        while puz.player_state[j][i] != '-':
            j += 1
            if j >= puz.height:
                i += 1
                j = 0
                if i >= puz.width:
                    i = 0
                    j = 0
                    dir = not dir
    else:
        while puz.player_state[j][i] != '-':
            i += 1
            if i >= puz.width:
                i = 0
                j += 1
                if j >= puz.height:
                    i = 0
                    j = 0
                    dir = not dir
    return i, j, dir


def pause(puz: rp.Puzzle):
    # for now just exit, but in the future add options to save mb or check
    return "exit"


def highlight(scr: curses.window, puz: rp.Puzzle, y, x, dir):
    if puz.player_state[y][x] == '.':
        return
    elif dir:
        i = 0
        j = 1
        while (j < (puz.height-y)) and (puz.player_state[y+j][x+i] != '.'):
            c = puz.player_state[y+j][x+i]
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # fst 1
            j += 1
        i = 0
        j = -1
        while (j > -y-1) and (puz.player_state[y+j][x+i] != '.'):
            c = puz.player_state[y+j][x+i]
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # snd 1
            j -= 1
        c = puz.player_state[y][x]
        scr.delch(y, x)
        scr.insch(y, x, c, curses.A_REVERSE)  # trd
    else:
        i = 1
        j = 0
        while (i < (puz.width-x)) and (puz.player_state[y+j][x+i] != '.'):
            c = puz.player_state[y+j][x+i]
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # fst 0
            i += 1
        i = -1
        j = 0
        while (i > -x-1) and (puz.player_state[y+j][x+i] != '.'):
            c = puz.player_state[y+j][x+i]
            scr.delch(y+j, x+i)
            scr.insch(y+j, x+i, c, curses.A_REVERSE)  # snd 0
            i -= 1
        c = puz.player_state[y][x]
        scr.delch(y, x)
        scr.insch(y, x, c, curses.A_REVERSE)  # snd
    return


def draw_player_state(board: curses.window, puz: rp.Puzzle):
    y, x = board.getyx()
    # Draw player state
    for i, row in enumerate(puz.player_state):
        for j, c in enumerate(row):
            if c == '.':
                board.insstr(i, j, u'\u2588')
            else:
                board.insstr(i, j, c)
    board.move(y, x)


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

    draw_player_state(board, puzzle)
    board.move(8, 8)
    stdscr.refresh()
    boarder.refresh()
    board.refresh()

    # Create window object; size is whole stdscreen
    stdscr.keypad(True)

    # Initializing variables for game loop
    dir = False  # 0 for across, 1 for down
    while True:
        y, x = board.getyx()
        draw_player_state(board, puzzle)
        # read character from keyboard
        k = stdscr.getkey()
        # ASCII int -> character
        match k:
            case "\n":
                p = pause(puzzle)
                match p:
                    case "exit":
                        return 0
                    case _:
                        continue
            case "KEY_BACKSPACE":
                puzzle.write(x, y, "-")
            case " ":
                dir = not dir
            case "KEY_UP":
                dir = True
                if y > 0:
                    board.move(y-1, x)
            case "KEY_DOWN":
                dir = True
                if y < bheight - 1:
                    board.move(y+1, x)
            case "KEY_LEFT":
                dir = False
                if x > 0:
                    board.move(y, x-1)
            case "KEY_RIGHT":
                dir = False
                if x < bwidth - 1:
                    board.move(y, x+1)
            case _:
                if len(k) == 1:
                    puzzle.write(x, y, k)
                    nx, ny, dir = write_move(puzzle, x, y, k, dir)
                    board.move(ny, nx)
                    draw_player_state(board, puzzle)

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
