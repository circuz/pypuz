import sys
import numpy as np


def readrest(rest, number_clues):
    strings = rest.split(b'\x00')
    title = strings[0]
    author = strings[1]
    copyrightstring = strings[2]
    clues = strings[3:3 + int(number_clues[0])]
    notes = strings[-1]
    return title, author, copyrightstring, clues, notes


#   matchclues :: ([Bytes], np.array([[Bytes]])) -> {Coord -> (Clue, Clue)}
def matchclues(clues, solution):
    # iterate + keep track of cell above and to the left-linear time. optimal?
    height = solution.shape[0]
    width = solution.shape[1]
    cluedict = {(x, -1): ("$BLK", "$BLK") for x in range(width)}
    for y in range(height):
        cluedict[(-1, y)] = ("$BLK", "$BLK")
    cluenumber = 0
    for j in range(height):
        for i in range(width):
            if (solution[j, i] == 46):
                cluedict[(i, j)] = ("$BLK", "$BLK")
            elif (cluedict[(i-1, j)][0] == "$BLK") and (cluedict[(i, j-1)][1] == "$BLK"):
                cluedict[(i, j)] = (clues[cluenumber], clues[cluenumber + 1])
                cluenumber += 2
            elif (cluedict[(i-1, j)][0] == "$BLK"):
                cluedict[(i, j)] = (clues[cluenumber], cluedict[(i, j-1)][1])
                cluenumber += 1
            elif (cluedict[(i, j-1)][1] == "$BLK"):
                cluedict[(i, j)] = (cluedict[(i-1, j)][0], clues[cluenumber])
                cluenumber += 1
            else:
                cluedict[(i, j)] = (cluedict[(i-1, j)][0], cluedict[(i, j-1)][1])

    return cluedict


def readpuz(file, verbose=0):
    with open(file, 'rb') as f:
        fst_checksum = f.read(2)            # Overall file checksum
        file_magic_b = f.read(12)         # NUL-terminated constant string
        if file_magic_b != b"ACROSS&DOWN\x00":
            print(f"""Error! Incorrect file magic. Got: {file_magic_b}
                Expected: ACROSS&DOWN""")
            return 0
        CIB_checksum = f.read(2)    # TODO: (defined later)
        ML_checksums = f.read(4)    # Checksums, XOR-masked against a magic str
        MH_checksums = f.read(4)    # Checksums, XOR-masked against a magic str
        version_stri = f.read(4)    # Version string, e.g. 1.2
        reserved_1C_ = f.read(2)    # In many files, uninitialized memory
        scr_checksum = f.read(2)    # In scrambled puzzles, a solution checksum
        _ = f.read(12)              # offset from 0x1F to 0x2C
        width, height = f.read(2)   # width and height of board, one byte each
        number_clues = f.read(2)    # the number of clues on this board
        unknown_bits = f.read(2)    # a bitmask. operations unknown
        is_scrambled = f.read(2)    # 0 for unscrambled, nonzero for scrambled
        solution = np.array([list(f.read(width)) for _ in range(height)])
        player_state = [f.read(width) for _ in range(height)]
        rest = f.read()

    title, author, copyrightstring, clues, notes = readrest(rest, number_clues)
    cluedict = matchclues(clues, solution)

    if verbose == 1:
        print(f"{title=} {author=} {copyrightstring=} {clues=} {notes=}")
        print(solution)
        for y in range(height):
            for x in range(width):
                print(f'{x}, {y}, {cluedict[(x, y)]}')
    if verbose == 2:
        for row in player_state:
            print(row)
        print(file_magic_b, version_stri, width, height, number_clues)
        print(
            fst_checksum
            , CIB_checksum
            , ML_checksums
            , MH_checksums
            , version_stri
            , reserved_1C_
            , scr_checksum
            , number_clues
            , unknown_bits
            , is_scrambled)

    return cluedict


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python readpuz.py [.PUZ FILENAME]")
    else:
        readpuz(sys.argv[1])
