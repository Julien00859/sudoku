import collections
import random

def generate():
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

    return [list(line) for line in grid]


def get_grid(no):
    with open(__file__[:-2] + 'txt') as file:
        file.seek(108 * no + 9)
        return file.read(89).split('\n')


def validate(grid):
    for _ in range(2):
        for row in grid:
            assert sorted(row) == list('123456789')
        grid = list(zip(*grid))

    for i in range(3):
        for j in range(3):
            block = [
                *grid[i*3][j*3:j*3+3],
                *grid[i*3+1][j*3:j*3+3],
                *grid[i*3+2][j*3:j*3+3],
            ]
            assert sorted(block) == list('123456789')


def pprint(g):
    print(f"""\
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
""".replace('0', '.'))


if __name__ == '__main__':
    pprint(get_grid(0))
    pprint(generate())

    for _ in range(1000):
        validate(generate())
