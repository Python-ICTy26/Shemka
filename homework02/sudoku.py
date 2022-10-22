import copy
import pathlib
import time
import typing as tp
from random import randint

T = tp.TypeVar("T")


def read_sudoku(path: tp.Union[str, pathlib.Path]) -> tp.List[tp.List[str]]:
    """Прочитать Судоку из указанного файла"""
    path = pathlib.Path(path)
    with path.open() as f:
        puzzle = f.read()
    return create_grid(puzzle)


def create_grid(puzzle: str) -> tp.List[tp.List[str]]:
    digits = [c for c in puzzle if c in "123456789."]
    grid = group(digits, 9)
    return grid


def display(grid: tp.List[tp.List[str]]) -> None:
    """Вывод Судоку"""
    width = 2
    line = "+".join(["-" * (width * 3)] * 3)
    for row in range(9):
        print(
            "".join(
                grid[row][col].center(width) + ("|" if str(col) in "25" else "") for col in range(9)
            )
        )
        if str(row) in "25":
            print(line)
    print()


def group(values: tp.List[T], n: int) -> tp.List[tp.List[T]]:
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов

    >>> group([1,2,3,4], 2)
    [[1, 2], [3, 4]]
    >>> group([1,2,3,4,5,6,7,8,9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """

    out = []
    pair = []
    c = 0
    for v in values:
        pair.append(v)
        c += 1
        if c == n:
            out.append(pair)
            c = 0
            pair = []
    if c > 0:
        out.append(pair)
    return out


def get_row(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера строки, указанной в pos

    >>> get_row([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '2', '.']
    >>> get_row([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (1, 0))
    ['4', '.', '6']
    >>> get_row([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (2, 0))
    ['.', '8', '9']
    """
    return grid[pos[0]]


def get_col(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера столбца, указанного в pos

    >>> get_col([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '4', '7']
    >>> get_col([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (0, 1))
    ['2', '.', '8']
    >>> get_col([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (0, 2))
    ['3', '6', '9']
    """
    return [row[pos[1]] for row in grid]


def get_block(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения из квадрата, в который попадает позиция pos

    >>> grid = read_sudoku('puzzle1.txt')
    >>> get_block(grid, (0, 1))
    ['5', '3', '.', '6', '.', '.', '.', '9', '8']
    >>> get_block(grid, (4, 7))
    ['.', '.', '3', '.', '.', '1', '.', '.', '6']
    >>> get_block(grid, (8, 8))
    ['2', '8', '.', '.', '.', '5', '.', '7', '9']
    """
    block_x, block_y = pos[0] // 3, pos[1] // 3
    result = []
    for row in grid[3 * block_x : 3 * block_x + 3]:
        result += row[3 * block_y : 3 * block_y + 3]
    return result


def find_empty_positions(
    grid: tp.List[tp.List[str]],
) -> tp.Optional[tp.Tuple[int, int]]:
    """Найти первую свободную позицию в пазле

    >>> find_empty_positions([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']])
    (0, 2)
    >>> find_empty_positions([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']])
    (1, 1)
    >>> find_empty_positions([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']])
    (2, 0)
    """
    for i, row in enumerate(grid):
        for j, el in enumerate(row):
            if el == ".":
                return i, j
    return None


def find_all_empty_positions(
    grid: tp.List[tp.List[str]],
) -> tp.Generator[tp.Tuple[int, int], None, None]:
    """Найти все свободные позиции в пазле"""
    for i, row in enumerate(grid):
        for j, el in enumerate(row):
            if el == ".":
                yield i, j


def find_possible_values(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.Set[str]:
    """Вернуть множество возможных значения для указанной позиции

    >>> grid = read_sudoku('puzzle1.txt')
    >>> values = find_possible_values(grid, (0, 2))
    >>> values == {'1', '2', '4'}
    True
    >>> values = find_possible_values(grid, (4, 7))
    >>> values == {'2', '5', '9'}
    True
    """
    if grid[pos[0]][pos[1]] != ".":
        raise ValueError("you should pass position of an empty element!")

    all_values = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
    row = set(filter(lambda x: x != ".", get_row(grid, pos)))
    col = set(filter(lambda x: x != ".", get_col(grid, pos)))
    block = set(filter(lambda x: x != ".", get_block(grid, pos)))
    return all_values - row - col - block


def solve(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.List[tp.List[str]]]:
    """Решение пазла, заданного в grid"""
    """ Как решать Судоку?
        1. Найти свободную позицию
        2. Найти все возможные значения, которые могут находиться на этой позиции
        3. Для каждого возможного значения:
            3.1. Поместить это значение на эту позицию
            3.2. Продолжить решать оставшуюся часть пазла

    >>> grid = read_sudoku('puzzle1.txt')
    >>> solve(grid)
    [['5', '3', '4', '6', '7', '8', '9', '1', '2'], ['6', '7', '2', '1', '9', '5', '3', '4', '8'], ['1', '9', '8', '3', '4', '2', '5', '6', '7'], ['8', '5', '9', '7', '6', '1', '4', '2', '3'], ['4', '2', '6', '8', '5', '3', '7', '9', '1'], ['7', '1', '3', '9', '2', '4', '8', '5', '6'], ['9', '6', '1', '5', '3', '7', '2', '8', '4'], ['2', '8', '7', '4', '1', '9', '6', '3', '5'], ['3', '4', '5', '2', '8', '6', '1', '7', '9']]
    """

    grid = copy.deepcopy(grid)
    pos = find_empty_positions(grid)
    if pos is None:
        return grid
    vals = find_possible_values(grid, pos)

    for v in vals:
        grid[pos[0]][pos[1]] = v
        sol = solve(grid)
        if sol is not None:
            return sol

    return None


def fast_solve(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.List[tp.List[str]]]:
    """Решение пазла, заданного в grid"""
    """ Как решать Судоку?
        1. Найти все свободные позиции
        2. Найти такую позицию у которой наименьшее количество вариантов
        3. Для этой позиции найти все возможные значения
        4. Для каждого возможного значения:
            4.1. Поместить это значение на эту позицию
            4.2. Продолжить решать оставшуюся часть пазла

    >>> grid = read_sudoku('puzzle1.txt')
    >>> fast_solve(grid)
    [['5', '3', '4', '6', '7', '8', '9', '1', '2'], ['6', '7', '2', '1', '9', '5', '3', '4', '8'], ['1', '9', '8', '3', '4', '2', '5', '6', '7'], ['8', '5', '9', '7', '6', '1', '4', '2', '3'], ['4', '2', '6', '8', '5', '3', '7', '9', '1'], ['7', '1', '3', '9', '2', '4', '8', '5', '6'], ['9', '6', '1', '5', '3', '7', '2', '8', '4'], ['2', '8', '7', '4', '1', '9', '6', '3', '5'], ['3', '4', '5', '2', '8', '6', '1', '7', '9']]
    """
    grid = copy.deepcopy(grid)
    positions = find_all_empty_positions(grid)

    curr_pos = next(positions, None)
    if curr_pos is None:
        return grid

    vals = find_possible_values(grid, curr_pos)
    for pos in positions:
        tmp_vals = find_possible_values(grid, pos)

        if len(tmp_vals) < len(vals):
            curr_pos = pos
            vals = tmp_vals

    for v in vals:
        grid[curr_pos[0]][curr_pos[1]] = v
        sol = fast_solve(grid)
        if sol is not None:
            return sol

    return None


def check_solution(solution: tp.List[tp.List[str]]) -> bool:
    """
    Если решение solution верно, то вернуть True, в противном случае False

    >>> grid = read_sudoku('puzzle1.txt')
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> solution[0][1] = '1'
    >>> check_solution(solution)
    False
    """

    if find_empty_positions(solution) is not None:
        return False

    all_values = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    for i in range(len(solution)):
        row = get_row(solution, (i, 0))
        unq_vals = set(map(int, row))
        if sum(unq_vals) != sum(map(int, row)) or len(unq_vals - all_values) > 0:
            return False

    for i in range(len(solution), 3):
        for j in range(len(solution), 3):
            block = get_block(solution, (i, j))
            if sum(set(map(int, block))) != sum(map(int, block)):
                return False

    for i in range(len(solution)):
        col = get_col(solution, (0, i))
        if sum(set(map(int, col))) != sum(map(int, col)):
            return False

    return True


def generate_sudoku(N: int) -> tp.List[tp.List[str]]:
    """Генерация судоку заполненного на N элементов

    >>> grid = generate_sudoku(40)
    >>> sum(1 for row in grid for e in row if e == '.')
    41
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(1000)
    >>> sum(1 for row in grid for e in row if e == '.')
    0
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(0)
    >>> sum(1 for row in grid for e in row if e == '.')
    81
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    """
    grid = [["."] * 9 for _ in range(9)]
    sol = solve(grid)

    if sol:
        grid = sol
    else:
        raise ValueError("something went wrong!")

    for _ in range(81 - N):
        pos = (randint(0, 8), randint(0, 8))
        while grid[pos[0]][pos[1]] == ".":
            pos = (randint(0, 8), randint(0, 8))
        grid[pos[0]][pos[1]] = "."

    return grid


if __name__ == "__main__":
    # CHECK SOLVE
    start = time.perf_counter()
    for fname in [
        "puzzle1.txt",
        "puzzle2.txt",
        "puzzle3.txt",
    ]:
        grid = read_sudoku(fname)
        display(grid)
        solution = solve(grid)
        if not solution:
            print(f"Puzzle {fname} can't be solved")
        else:
            display(solution)
    print(time.perf_counter() - start)

    # CHECK FAST SOLVE
    start = time.perf_counter()
    for fname in ["puzzle1.txt", "puzzle2.txt", "puzzle3.txt"]:
        grid = read_sudoku(fname)
        display(grid)
        solution = fast_solve(grid)
        if not solution:
            print(f"Puzzle {fname} can't be solved")
        else:
            display(solution)
    print(time.perf_counter() - start)

    # CHECK HARD PUZZLE
    hard_puzzle_idx = 2
    path = pathlib.Path("hard_puzzles.txt")
    with path.open() as f:
        puzzle = f.read().split("\n")[hard_puzzle_idx]
    grid = create_grid(puzzle)
    display(grid)
    solution = fast_solve(grid)
    if not solution:
        print(f"Puzzle hard_puzzles.txt::{hard_puzzle_idx} can't be solved")
    else:
        display(solution)
