import pygame
import random

pygame.init()

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

class Snake:
    """
    Single version game example
    """
    # pos = (x, y), where x is the col offset, and y is the row offset.
    def __init__(self, pos, rows, cols):
        self.rows, self.cols = rows, cols
        self.body = [pos]
        self.dx, self.dy = 0, 1

    def _update_dir(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: self.dx, self.dy = 1, 0
        if keys[pygame.K_LEFT]: self.dx, self.dy = -1, 0
        if keys[pygame.K_UP]: self.dx, self.dy = 0, -1
        if keys[pygame.K_DOWN]: self.dx, self.dy = 0, 1

    # Return true if move is okay, false otherwise.
    def move(self, apple):
        self._update_dir()
        x, y = self.body[0]
        nx, ny = (x + self.dx) % self.cols, (y + self.dy) % self.rows
        if (nx, ny) in self.body:
            return False
        self.body.insert(0, (nx, ny))
        if not (nx, ny) == apple:
            self.body.pop()
        return True

    # Return the head of the snake.
    def head(self):
        return self.body[0]


class SnakeApp:
    def __init__(self):
        # Initialize surface
        self.rows, self.cols = 32, 32
        self.snake_size = 20
        self.surface = pygame.display.set_mode((self.cols * self.snake_size, self.rows * self.snake_size))
        pygame.display.set_caption('Snake Game')
        # Initialize snake
        snake_start_pos = self._choose_random_pos()
        self.snake = Snake(snake_start_pos, self.rows, self.cols)
        # Initialize apple. Make sure it's not the same as snake start position.
        self.apple = self._choose_random_pos()
        while self.apple == snake_start_pos: self.apple = self._choose_random_pos()
        # Flag to indicate if game is over.
        self.game_over = False

    def _choose_random_pos(self):
        x = random.randrange(self.cols)
        y = random.randrange(self.rows)
        return x, y

    def _draw_rect(self, pos, color):
        x, y = pos
        pygame.draw.rect(self.surface, color,
                         (x*self.snake_size+1, y*self.snake_size+1, self.snake_size-2 , self.snake_size-2))

    def _render(self):
        self.surface.fill(WHITE)
        self._draw_rect(self.apple, GREEN)
        for pos in self.snake.body:
            self._draw_rect(pos, RED)
        pygame.display.flip()

    def run_once(self):
        if self.game_over: return
        if not self.snake.move(self.apple):
            self.game_over = True
            self._draw_game_over()
            return
        if self.snake.head() == self.apple:
            while self.apple in self.snake.body:
                self.apple = self._choose_random_pos()
        self._render()

    def _draw_game_over(self):
        self._render()
        assert pygame.font.get_init()
        font = pygame.font.Font(None, 60)
        text = font.render("Game Over", True, BLUE)
        text_rect = text.get_rect()
        text_x = self.surface.get_width() / 2 - text_rect.width / 2
        text_y = self.surface.get_height() / 2 - text_rect.height / 2
        self.surface.blit(text, [text_x, text_y])
        pygame.display.flip()


if __name__ == "__main__":
    clock = pygame.time.Clock()
    FPS = 10  # frames-per-second
    game = SnakeApp()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        game.run_once()
