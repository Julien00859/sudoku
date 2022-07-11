# Original author Peter Norvig
# http://norvig.com/sudoku.html

import re

GRID_9x9 = """
A1 A2 A3|A4 A5 A6|A7 A8 A9
C1 C2 C3|C4 C5 C6|C7 C8 C9
B1 B2 B3|B4 B5 B6|B7 B8 B9
--------+--------+---------
D1 D2 D3|D4 D5 D6|D7 D8 D9
E1 E2 E3|E4 E5 E6|E7 E8 E9
F1 F2 F3|F4 F5 F6|F7 F8 F9
--------+--------+---------
G1 G2 G3|G4 G5 G6|G7 G8 G9
H1 H2 H3|H4 H5 H6|H7 H8 H9
I1 I2 I3|I4 I5 I6|I7 I8 I9
"""

def cross(a, b):
    return frozenset([aa + bb for aa in a for bb in b])

def sq_from_rc(row, col):
    return row // 3 * 3 + col // 3

def rc_from_sq(sq, i=0):
    return sq // 3 * 3 + i // 3, sq % 3 * 3 + i % 3

digits = '123456789'
row_digits = 'ABCDEFGHI'
col_digits = digits

rows = [cross(rd, col_digits) for rd in row_digits]
cols = [cross(row_digits, cd) for cd in col_digits]
sqrs = [cross(row_digits[ri:ri+3], col_digits[ci:ci+3])
        for ri in range(0, 9, 3) for ci in range(0, 9, 3)]

cells = cross(row_digits, col_digits)
peers_of = {
    cell: (
        rows[ri := ord(cell[0]) - 65]
        | cols[ci := ord(cell[1]) - 49]
        | sqrs[sq_from_rc(ri, ci)]
    ) - {cell} for cell in cells
}

class _Solver:
    def __init__(self):
        self.guess_count = 0
        self.max_depth = 0
        self.candidates = {cell: digits for cell in cells}

    def assign(self, cell, digit):
        # Instead of assigning the digit to the cell, we eliminate all
        # the other digits from the cell, ultimately this only leaves
        # the given digit in the cell.
        other_digits = self.candidates[cell].replace(digit, '')
        for other_digit in other_digits:
            self.eliminate(cell, other_digit)
        assert self.candidates[cell] == digit

    def eliminate(self, cell, digit):
        # The digit doesn't fit here, remove it from the candidates.
        self.candidates[cell] = self.candidates[cell].replace(digit, '')

        # This is no candidate left for this cell, the puzzle is
        # impossible or we guessed a wrong digit before.
        if len(self.candidates[cell]) == 0:
            raise ValueError("No solution.")

        # There is a single candidate left in this cell making it the
        # right digit in this cell. That digit cannot go in any of the
        # peers, eliminate it from the peers.
        if len(self.candidates[cell]) == 1:
            for peer in peers_of[cell]:
                if self.candidates[cell] in self.candidates[peer]:
                    self.eliminate(peer, self.candidates[cell])

        # The digit doesn't fit here but it must fit in one of the peer.
        # Determine the peers where the digit would fit.
        peers = [peer for peer in peers_of[cell] if digit in self.candidates[peer]]

        # There is no peer where the digit would fit, the puzzle is
        # impossible or we guessed a wrong digit before.
        if len(peers) == 0:
            raise ValueError("No solution.")

        # There is a single peer where the digit can fit, assign it to
        # that peer.
        if len(peers) == 1:
            self.assign(peers[0], digit)

    def guess(self, depth=1):
        self.guess_count += 1
        self.max_depth = max(self.max_depth, depth)

        # Find a cell with a minimum of candidates then just assume
        # one of the candidate is the correct value and continue the
        # puzzle. In case we are proven wrong, just try another
        # candidate.
        cell, cands = min(((cell, cands) for cell, cands in self.candidates.items() if len(cands) > 1), key=lambda x: len(x[1]))

        for candidate in cands:
            frozen_candidates = self.candidates.copy()
            try:
                self.assign(cell, candidate)
                if self.is_solved():
                    return depth
                return self.guess(depth + 1)
            except ValueError:
                self.candidates = frozen_candidates

        # Truly unsolvable.
        raise ValueError("No solution.")

    def is_solved(self):
        return all(len(candidates) == 1 for candidates in self.candidates.values())

    def __str__(self):
        return re.sub(r'(\w\d)', r'{\1} ', GRID_9x9).format(**{
            cell: value if len(value) == 1 else '.'
            for cell, value in self.candidates.items()
        })

class Sudoku:

    def __init__(self, grid):
        self.grid = grid

    @classmethod
    def from_snapshot(cls, snapshot):
        snapshot = re.sub(r'[^0-9 \.]', '', snapshot)
        snapshot = re.sub(r'[ \.]', '0', snapshot)
        return cls([list(snapshot[i:i+9]) for i in range(0, 81, 9)])

    @classmethod
    def from_database(cls, grid_no):
        with open(__file__[:-2] + 'txt') as file:
            file.seek(108 * (grid_no - 1) + 9)
            return cls.from_snapshot(file.read(89))

    def get_row(self, row):
        return self.grid[row]

    def get_col(self, col):
        return [self.grid[row][col] for row in range(9)]

    def get_square(self, square):
        return self.get_square_rc(*rc_from_sq(square))

    def get_square_rc(self, row, col):
        g = self.grid
        row = row // 3 * 3
        col = col // 3 * 3

        return [
            g[row][col], g[row][col+1], g[row][col+2],
            g[row+1][col], g[row+1][col+1], g[row+1][col+2],
            g[row+2][col], g[row+2][col+1], g[row+2][col+2],
        ]

    def is_solved(self):
        """ Verify that the grid is complete and valid. """
        for i in range(9):
            if not (
                sorted(self.get_square(i)) == list(digits)
                and sorted(self.get_col(i)) == list(digits)
                and sorted(self.get_row(i)) == list(digits)
            ):
                return False
        return True

    def is_valid(self):
        """ Verify that the grid is valid so far. """
        for i in range(9):
            if (self._contains_duplicate(self.get_square(i))
                or self._contains_duplicate(self.get_row(i))
                or self._contains_duplicate(self.get_col(i))):
                return False
        return True

    @staticmethod
    def _contains_duplicate(line):
        return any(line.count(digit) > 1 for digit in line if digit != '0')

    def solve(self):
        solver = _Solver()
        depth = 0
        for rn, rd in zip(range(9), row_digits):
            for cn, cd in zip(range(9), col_digits):
                if self.grid[rn][cn] != '0':
                    solver.assign(rd + cd, self.grid[rn][cn])
        if not solver.is_solved():
            depth += solver.guess()
        for rn, rd in zip(range(9), row_digits):
            for cn, cd in zip(range(9), col_digits):
                self.grid[rn][cn] = solver.candidates[rd + cd]

        assert self.is_valid()
        assert self.is_solved()

        return (depth, solver.max_depth, solver.guess_count)

    def __str__(self):
        return "\n-----+-----+-----\n".join(
            "\n".join(
                "|".join(
                    " ".join(
                        row[i:i+3]
                    ) for i in range(0, 9, 3)
                ) for row in self.grid[j:j+3]
            ) for j in range(0, 9, 3)
        )

    def __repr__(self):
        return '\n'.join(''.join(line) for line in self.grid)


if __name__ == '__main__':
    import time
    import sys

    if len(sys.argv) < 2:
        sys.exit(f"usage: {__file__} {{grid, low:high}}")

    low, _, high = sys.argv[1].partition(':')

    total_time = 0
    for grid_no in range(int(low), int(high) if high else int(low) + 1):
        sudo = Sudoku.from_database(grid_no)
        chrono = time.time()
        depth, max_depth, total_guesses = sudo.solve()
        elapsed = time.time() - chrono
        total_time += elapsed
        assert sudo.is_valid()
        assert sudo.is_solved()
        print(f"Solved grid n°{grid_no:<2d} in {elapsed:.03f}s; {depth=:<2d} {max_depth=:<2d} {total_guesses=}")

    if high:
        print(f"Total time: {total_time:.04f}s")
    else:
        print(repr(sudo))
