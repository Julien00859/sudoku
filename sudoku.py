import collections
import contextlib
import random
import re
import textwrap

def sq_from_rc(row, col):
    return row // 3 * 3 + col // 3

def rc_from_sq(sq, i=0):
    return sq // 3 * 3 + i // 3, sq % 3 * 3 + i % 3

class _Grid:
    def __init__(self, grid):
        assert len(grid) == 9
        for line in grid:
            assert len(line) == 9
        self.grid = grid

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


class Sudoku(_Grid):
    @classmethod
    def from_snapshot(cls, snapshot):
        snapshot = re.sub(r'[^0-9\n]', '0', snapshot)
        return cls([list(line) for line in snapshot.splitlines()])

    @classmethod
    def new_solved_grid(cls):
        """ Create a solved 9x9 random grid. """
        # generate a solved grid that is garanteed to be valid
        grid = []
        seed = collections.deque('123456789')
        random.shuffle(seed)
        for _ in range(3):
            for _ in range(3):
                grid.append(list(seed))
                seed.rotate(3)
            seed.rotate(1)

        # shuffle the grid 
        for _ in range(2):
            for row in range(3):
                for _ in range(random.randint(2, 3)):
                    src = random.randint(0, 2)
                    dst = random.randint(0, 2)
                    grid[row*3+src], grid[row*3+dst] = grid[row*3+dst], grid[row*3+src]

            for _ in range(random.randint(2, 3)):
                src = random.randint(0, 2)
                dst = random.randint(0, 2)
                (grid[src*3], grid[src*3+1], grid[src*3+2],
                 grid[dst*3], grid[dst*3+1], grid[dst*3+2]) = (
                 grid[dst*3], grid[dst*3+1], grid[dst*3+2],
                 grid[src*3], grid[src*3+1], grid[src*3+2])

            grid = list(zip(*grid))

        return cls([list(line) for line in grid])

    @classmethod
    def from_database(cls, grid_no):
        """ Open and parse the 50-grids sodoku.txt file, return the n°no grid. """
        with open(__file__[:-2] + 'txt') as file:
            file.seek(108 * (grid_no - 1) + 9)
            return cls.from_snapshot(file.read(89))

    def __str__(self):
        g = self.grid
        return textwrap.dedent(f"""\
            {g[0][0]}{g[0][1]}{g[0][2]}|{g[0][3]}{g[0][4]}{g[0][5]}|{g[0][6]}{g[0][7]}{g[0][8]}
            {g[1][0]}{g[1][1]}{g[1][2]}|{g[1][3]}{g[1][4]}{g[1][5]}|{g[1][6]}{g[1][7]}{g[1][8]}
            {g[2][0]}{g[2][1]}{g[2][2]}|{g[2][3]}{g[2][4]}{g[2][5]}|{g[2][6]}{g[2][7]}{g[2][8]}
            ---+---+---
            {g[3][0]}{g[3][1]}{g[3][2]}|{g[3][3]}{g[3][4]}{g[3][5]}|{g[3][6]}{g[3][7]}{g[3][8]}
            {g[4][0]}{g[4][1]}{g[4][2]}|{g[4][3]}{g[4][4]}{g[4][5]}|{g[4][6]}{g[4][7]}{g[4][8]}
            {g[5][0]}{g[5][1]}{g[5][2]}|{g[5][3]}{g[5][4]}{g[5][5]}|{g[5][6]}{g[5][7]}{g[5][8]}
            ---+---+---
            {g[6][0]}{g[6][1]}{g[6][2]}|{g[6][3]}{g[6][4]}{g[6][5]}|{g[6][6]}{g[6][7]}{g[6][8]}
            {g[7][0]}{g[7][1]}{g[7][2]}|{g[7][3]}{g[7][4]}{g[7][5]}|{g[7][6]}{g[7][7]}{g[7][8]}
            {g[8][0]}{g[8][1]}{g[8][2]}|{g[8][3]}{g[8][4]}{g[8][5]}|{g[8][6]}{g[8][7]}{g[8][8]}
            """
        ).replace('0', '.')

    def __repr__(self):
        return "\n".join("".join(line) for line in self.grid)

    def is_solved(self):
        """ Verify that the grid is complete and valid. """
        for i in range(9):
            if not (
                sorted(self.get_square(i)) == list('123456789')
                and sorted(self.get_col(i)) == list('123456789')
                and sorted(self.get_row(i)) == list('123456789')
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
        c = collections.Counter(line)
        c.pop('0', None)
        return c.most_common(1)[0][1] != 1

    def _solve_row(self, row_no):
        found = False
        row = self.get_row(row_no)
        known_set = {x for x in row if x != '0'}
        missing_set = set("123456789") - known_set
        free_spots = [i for i, v in enumerate(row) if v == '0']
        if len(missing_set) != len(free_spots):
            raise ValueError("Invalid self")

        for missing in missing_set:
            fit = [
                col_no
                for col_no in free_spots
                if missing not in self.get_square_rc(row_no, col_no)
                and missing not in self.get_col(col_no)
            ]
            if len(fit) == 1:
                self.grid[row_no][fit[0]] = missing
                free_spots.remove(fit[0])
                found = True

        return found

    def _solve_col(self, col_no):
        found = False
        col = self.get_col(col_no)
        known_set = {x for x in col if x != '0'}
        missing_set = set("123456789") - known_set
        free_spots = [i for i, v in enumerate(col) if v == '0']
        if len(missing_set) != len(free_spots):
            raise ValueError("Invalid self")

        for missing in missing_set:
            fit = [
                row_no
                for row_no in free_spots
                if missing not in self.get_square_rc(row_no, col_no)
                and missing not in self.get_row(row_no)
            ]
            if len(fit) == 1:
                self.grid[fit[0]][col_no] = missing
                free_spots.remove(fit[0])
                found = True

        return found

    def _solve_square(self, sq_no):
        found = False
        square = self.get_square(sq_no)
        known_set = {x for x in square if x != '0'}
        missing_set = set("123456789") - known_set
        free_spots = [rc_from_sq(sq_no, i) for i, v in enumerate(square) if v == '0']
        if len(missing_set) != len(free_spots):
            raise ValueError("Invalid self")

        for missing in missing_set:
            fit = [
                (row_no, col_no)
                for (row_no, col_no) in free_spots
                if missing not in self.get_row(row_no)
                and missing not in self.get_col(col_no)
            ]
            if len(fit) == 1:
                free_spots.remove(fit[0])
                self.grid[fit[0][0]][fit[0][1]] = missing
                found = True

        return found

    def get_candidates(self, row_no, col_no):
        return (
            set("123456789")
            - set(self.get_row(row_no))
            - set(self.get_col(col_no))
            - set(self.get_square_rc(row_no, col_no))
        )

    def _solve_cell(self, row_no, col_no):
        if len(candidates := self.get_candidates(row_no, col_no)) == 1:
            self.grid[row_no][col_no] = candidates.pop()
            return True
        return False

    def _guess_value(self, row_no, col_no, length, depth):
        if len(candidates := self.get_candidates(row_no, col_no)) == length:
            for candidate in candidates:
                frozen_grid = [line.copy() for line in self.grid]
                self.grid[row_no][col_no] = candidate
                try:
                    depth = self.solve(depth + 1, (row_no, col_no))
                    if self.is_solved():
                        return depth
                except ValueError:
                    pass
                self.grid = frozen_grid

        return depth

    def solve(self, depth=0, guessed_rc=(0, 0)):
        found = True
        while not self.is_solved() and found:
            found = False

            for row_no in range(9):
                found |= self._solve_row(row_no)

            for col_no in range(9):
                found |= self._solve_col(col_no)

            for sq_no in range(9):
                found |= self._solve_square(sq_no)

            for row_no in range(9):
                for col_no in range(9):
                    if self.grid[row_no][col_no] == '0':
                        found |= self._solve_cell(row_no, col_no)

        if not self.is_solved():
            for candidate_len in range(2, 9):
                for row_no in range(guessed_rc[0], 9):
                    for col_no in range(guessed_rc[1], 9):
                        if self.grid[row_no][col_no] == '0':
                            depth = self._guess_value(row_no, col_no, candidate_len, depth)

        return depth


if __name__ == '__main__':
    import time
    for grid_no in range(1, 54):
        sudo = Sudoku.from_database(grid_no)
        #assert sudo.is_valid()
        chrono = time.time()
        depth = sudo.solve()
        elapsed = time.time() - chrono
        assert sudo.is_valid()
        assert sudo.is_solved()
        print(f"Solved {grid_no} in {elapsed:.03f}s guessing {depth} times")
