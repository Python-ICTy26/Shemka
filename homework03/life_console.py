import curses

import pygame
from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife, speed=10) -> None:
        super().__init__(life)
        self.speed = speed

    def draw_borders(self, screen) -> None:
        """Отобразить рамку."""
        screen.addstr(f"+{'-' * self.life.cols}+\n")
        for i in range(self.life.rows):
            screen.addstr("|")
            screen.addstr(i + 1, self.life.cols + 1, "|\n")
        screen.addstr(f"+{'-' * self.life.cols}+\n")

    def draw_grid(self, screen) -> None:
        """Отобразить состояние клеток."""
        for row in range(self.life.rows):
            for col in range(self.life.cols):
                if self.life.curr_generation[row][col]:
                    screen.move(row + 1, col + 1)
                    screen.addstr("*")

    def run(self) -> None:
        clock = pygame.time.Clock()

        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.nodelay(True)
        curses.curs_set(False)
        try:
            running = True
            pause = False
            while running:
                key = screen.getch()
                while key != -1:
                    if key == 113:
                        running = False
                    elif key == 32:
                        pause = not pause
                    key = screen.getch()
                screen.clear()
                self.draw_borders(screen)
                self.draw_grid(screen)
                if not pause:
                    self.life.step()
                screen.refresh()
                clock.tick(self.speed)

                if not self.life.is_changing or self.life.is_max_generations_exceeded:
                    running = False
            curses.echo()
            curses.nocbreak()
            curses.endwin()

        except Exception as err:
            print(f"{err}\n{type(err)}")
            curses.echo()
            curses.nocbreak()
            curses.endwin()


if __name__ == "__main__":
    life = Console(GameOfLife((32, 32)))
    life.run()
