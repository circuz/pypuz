import sys
import curses
import readpuz as rp


def goup(x, y):
    return x, y-1


def godown(x, y):
    return x, y+1


def goleft(x, y):
    return x-1, y


def goright(x, y):
    return x+1, y


def erasebackward(puz: rp.Puzzle, x: int, y: int, dir: bool):
    i = x
    j = y
    puz.write(i, j, '-')
    first = True
    while first or (puz.player_state[j][i] == '.'):
        first = False
        if dir:
            j -= 1
        else:
            i -= 1
        if (i < 0):
            j -= 1
            i = puz.width - 1
            if (j < 0):
                dir = not dir
        if (j < 0):
            i -= 1
            j = puz.height - 1
            if (i < 0):
                dir = not dir
                i = puz.width - 1
    return i, j, dir


def move(puz: rp.Puzzle, x: int, y: int, d: str):
    # take a step independent of writing but skip blocked squares
    match d:
        case "up":
            f = goup
        case "down":
            f = godown
        case "left":
            f = goleft
        case "right":
            f = goright

    nx, ny = f(x, y)
    while nx in range(0, puz.width) and ny in range(0, puz.height):
        if puz.player_state[ny][nx] != '.':
            return nx, ny
        nx, ny = f(nx, ny)
    return x, y


def write_move(puz: rp.Puzzle, x: int, y: int, k: str, dir: bool):
    # write to the screen and then move to the next non-written square
    # following the correct direction
    puz.write(x, y, k.upper())
    if is_clue_filled(puz, x, y, dir)[0]:
        i, j, d = next_clue(puz, x, y, dir)
    else:
        _, i, j = is_clue_filled(puz, x, y, dir)
        d = dir
    return i, j, d


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


def is_clue_filled(puz: rp.Puzzle, x: int, y: int, dir: bool):
    if puz.player_state[y][x] == '.':
        return (True, x, y)
    if puz.player_state[y][x] == '-':
        return (False, x, y)
    elif dir:
        i = 0
        j = 1
        while (j < (puz.height-y)) and (puz.player_state[y+j][x+i] != '.'):
            if puz.player_state[y+j][x+i] == '-':
                return (False, x+i, y+j)
            j += 1
        i = 0
        j = -1
        while (j > -y) and (puz.player_state[y+j][x+i] != '.'):
            j -= 1
        while (j < 0):
            if puz.player_state[y+j][x+i] == '-':
                return (False, x+i, y+j)
            j += 1
        return (True, x, y)
    else:
        i = 1
        j = 0
        while (i < (puz.width-x)) and (puz.player_state[y+j][x+i] != '.'):
            if puz.player_state[y+j][x+i] == '-':
                return (False, x+i, y+j)
            i += 1
        i = -1
        j = 0
        while (i > -x) and (puz.player_state[y+j][x+i] != '.'):
            i -= 1
        while (i < 0):
            if puz.player_state[y+j][x+i] == '-':
                return (False, x+i, y+j)
            i += 1
        return (True, x, y)


def next_clue(puz: rp.Puzzle, x: int, y: int, dir: bool):
    cclue = puz.cluedict[(x, y)][dir]
    first = 1
    while first or is_clue_filled(puz, x, y, dir)[0]:
        first = 0
        if dir:  # Down
            ix = puz.down.index(cclue)
            if ix < len(puz.down) - 1:
                cclue = puz.down[ix + 1]
                x, y = puz.xydict[cclue]
            else:
                dir = 0
                cclue = puz.across[0]
                x, y = puz.xydict[cclue]
        else:  # Across
            ix = puz.across.index(cclue)
            if ix < len(puz.across) - 1:
                cclue = puz.across[ix + 1]
                x, y = puz.xydict[cclue]
            else:
                dir = 1
                cclue = puz.down[0]
                x, y = puz.xydict[cclue]
    _, x, y = is_clue_filled(puz, x, y, dir)
    return x, y, dir


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

    # Create window object; size is whole stdscreen
    stdscr.keypad(True)

    # Initializing variables for game loop
    dir = False  # 0 for across, 1 for down
    currclue = "A0"
    (x, y) = puzzle.xydict[currclue]
    draw_player_state(board, puzzle)
    board.move(x, y)
    highlight(board, puzzle, y, x, dir)
    stdscr.addstr(belowboarder, 1, "A0: " + str(puzzle.strdict["A0"], 'latin-1'))
    stdscr.refresh()
    boarder.refresh()
    board.refresh()
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
            case "\t":
                x, y, dir = next_clue(puzzle, x, y, dir)
                board.move(x, y)
            case "KEY_BACKSPACE":
                x, y, dir = erasebackward(puzzle, x, y, dir)
            case " ":
                dir = not dir
            case "KEY_UP":
                dir = True
                if y > 0:
                    x, y = move(puzzle, x, y, "up")
            case "KEY_DOWN":
                dir = True
                if y < bheight - 1:
                    x, y = move(puzzle, x, y, "down")
            case "KEY_LEFT":
                dir = False
                if x > 0:
                    x, y = move(puzzle, x, y, "left")
            case "KEY_RIGHT":
                dir = False
                if x < bwidth - 1:
                    x, y = move(puzzle, x, y, "right")
            case _:
                if len(k) == 1:
                    x, y, dir = write_move(puzzle, x, y, k, dir)
                    draw_player_state(board, puzzle)
        board.move(y, x)

        y, x = board.getyx()
        highlight(board, puzzle, y, x, dir)
        board.move(y, x)

        # Clear previous clur and draw current clue
        stdscr.addstr(belowboarder, 1, " "*(len(puzzle.strdict[currclue]) + 6))
        board.move(y, x)
        currclue = puzzle.cluedict[(x, y)][dir]
        stdscr.addstr(belowboarder, 1, currclue + ": " + str(puzzle.strdict[currclue], 'latin-1'))

        stdscr.refresh()
        boarder.refresh()
        board.refresh()
    stdscr.keypad(False)


curses.wrapper(main)
