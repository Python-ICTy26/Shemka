import pathlib
import random
import typing as tp

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: float = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        if randomize:
            grid = [[random.randint(0, 1) for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        y_borders = [max(0, cell[0] - 1), min(self.rows, cell[0] + 2)]
        x_borders = [max(0, cell[1] - 1), min(self.cols, cell[1] + 2)]
        for i in range(*y_borders):
            neighbours += self.curr_generation[i][x_borders[0] : x_borders[1]]
        neighbours.remove(self.curr_generation[cell[0]][cell[1]])
        return neighbours

    def get_next_generation(self) -> Grid:
        new_generation = self.create_grid(randomize=False)
        for i in range(self.rows):
            for j in range(self.cols):
                n_neighbours = sum(self.get_neighbours((i, j)))
                if self.curr_generation[i][j] and 2 <= n_neighbours <= 3:
                    new_generation[i][j] = 1
                elif not self.curr_generation[i][j] and n_neighbours == 3:
                    new_generation[i][j] = 1

        return new_generation

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.generations += 1
        self.prev_generation = self.curr_generation
        self.curr_generation = self.get_next_generation()

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.generations >= self.max_generations

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.prev_generation != self.curr_generation or self.generations == 1

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        try:
            with filename.open() as f:
                grid = list(map(lambda x: list(map(int, list(x))), f.read().split()))
            loaded_game = GameOfLife((len(grid), len(grid[0])), randomize=False)
            loaded_game.curr_generation = grid

        except (ValueError, IndexError):
            print("Something wrong with file")
            return GameOfLife((13, 13))
        except Exception as error:
            print(error)
            return GameOfLife((13, 13))
        else:
            return loaded_game

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        with filename.open("w") as f:
            for cells in self.curr_generation:
                f.write("".join(map(str, cells)) + "\n")
