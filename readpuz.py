import sys


def readrest(rest, number_clues):
    strings = rest.split(b'\x00')
    title = strings[0]
    author = strings[1]
    copyrightstring = strings[2]
    clues = strings[3:3 + int(number_clues[0])]
    notes = strings[-1]
    return title, author, copyrightstring, clues, notes


#   matchclues :: ([Bytes], [Bytes]) -> [(Clue, Coord)]
def matchclues(clues, solution):
    # iterate + keep track of cell above and to the left-linear time. optimal?
    for i, b in enumerate(solution)


def readpuz(file):
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
        solution = [f.read(width) for _ in range(height)]
        player_state = [f.read(width) for _ in range(height)]
        rest = f.read()

    title, author, copyrightstring, clues, notes = readrest(rest, number_clues)
    cluedict = matchclues(clues, solution)
    print(file_magic_b, version_stri, width, height, number_clues)

    for row in solution:
        print(row)
    for row in player_state:
        print(row)

    print(f"{title=} {author=} {copyrightstring=} {clues=} {notes=}")

    if False:
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python readpuz.py [.PUZ FILENAME]")
    else:
        readpuz(sys.argv[1])
