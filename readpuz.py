import sys


class Puzzle:
    def __init__(self, puz_file):
        self.read(puz_file)
        self.matchclues()

    def read(self, puz_file):
        with open(puz_file, 'rb') as f:
            self.fst_checksum = f.read(2)            # Overall file checksum
            self.file_magic_b = f.read(12)         # NUL-terminated constant string
            if self.file_magic_b != b"ACROSS&DOWN\x00":
                print(f"""Error! Incorrect file magic. Got: {self.file_magic_b}
                    Expected: ACROSS&DOWN""")
                return 0
            self.CIB_checksum = f.read(2)    # TODO: (defined later)
            self.ML_checksums = f.read(4)    # Checksums, XOR-masked against a magic str
            self.MH_checksums = f.read(4)    # Checksums, XOR-masked against a magic str
            self.version_stri = f.read(4)    # Version string, e.g. 1.2
            self.reserved_1C_ = f.read(2)    # In many files, uninitialized memory
            self.scr_checksum = f.read(2)    # In scrambled puzzles, a solution checksum
            _ = f.read(12)              # offset from 0x1F to 0x2C
            self.width, self.height = f.read(2)   # width and height of board, one byte each
            self.number_clues = f.read(2)    # the number of clues on this board
            self.unknown_bits = f.read(2)    # a bitmask. operations unknown
            self.is_scrambled = f.read(2)    # 0 for unscrambled, nonzero for scrambled
            self.solution = [list(f.read(self.width).decode()) for _ in range(self.height)]
            self.player_state = [list(f.read(self.width).decode()) for _ in range(self.height)]
            rest = f.read()
        self.readrest(rest)

    def write(self, x, y, c: str):
        self.player_state[y][x] = c.encode() if self.player_state[y][x] != '.' else '.'
        return c

    def readrest(self, rest):
        strings = rest.split(b'\x00')
        self.title = strings[0]
        self.author = strings[1]
        self.copyrightstring = strings[2]
        self.clues = strings[3:3 + int(self.number_clues[0])]
        self.notes = strings[-1]
        return self

    #   matchclues :: ([Bytes], np.array([[Bytes]])) -> ({Coord -> (Clue, Clue)}, [String], [String])
    def matchclues(self):
        # iterate + keep track of cell above and to the left-linear time. optimal?
        across = []
        down = []
        height = len(self.solution)
        width = len(self.solution[0])
        cluedict = {(x, -1): ("$BLK", "$BLK") for x in range(width)}
        for y in range(height):
            cluedict[(-1, y)] = ("$BLK", "$BLK")
        cluenumber = 0
        for j in range(height):
            for i in range(width):
                if (self.solution[j][i] == '.'):
                    cluedict[(i, j)] = ("$BLK", "$BLK")
                elif (cluedict[(i-1, j)][0] == "$BLK") and (cluedict[(i, j-1)][1] == "$BLK"):
                    across.append(self.clues[cluenumber])
                    down.append(self.clues[cluenumber+1])
                    cluedict[(i, j)] = (self.clues[cluenumber], self.clues[cluenumber + 1])
                    cluenumber += 2
                elif (cluedict[(i-1, j)][0] == "$BLK"):
                    across.append(self.clues[cluenumber])
                    cluedict[(i, j)] = (self.clues[cluenumber], cluedict[(i, j-1)][1])
                    cluenumber += 1
                elif (cluedict[(i, j-1)][1] == "$BLK"):
                    down.append(self.clues[cluenumber+1])
                    cluedict[(i, j)] = (cluedict[(i-1, j)][0], self.clues[cluenumber])
                    cluenumber += 1
                else:
                    cluedict[(i, j)] = (cluedict[(i-1, j)][0], cluedict[(i, j-1)][1])

        self.cluedict = cluedict
        self.across = across
        self.down = down


if __name__ == "__main__":
    if sys.argv[1][-4:] != ".puz":
        print("Usage: python readpuz.py [.PUZ FILENAME]")
    else:
        Puzzle(sys.argv[1])
