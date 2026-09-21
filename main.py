import pygame
import random
import sys

SIZE = 4
CELL = 110
MARGIN = 15
BOARD_SIZE = SIZE * CELL + (SIZE + 1) * MARGIN
WIDTH = BOARD_SIZE
HEIGHT = BOARD_SIZE + 120
FPS = 60

TILE_COLORS = {
    0:    (205, 193, 180),
    2:    (238, 228, 218),
    4:    (237, 224, 200),
    8:    (242, 177, 121),
    16:   (245, 149, 99),
    32:   (246, 124, 95),
    64:   (246, 94, 59),
    128:  (237, 207, 114),
    256:  (237, 204, 97),
    512:  (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}
BG_COLOR = (187, 173, 160)
TEXT_DARK = (119, 110, 101)
TEXT_LIGHT = (249, 246, 242)


class Game2048:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[0] * SIZE for _ in range(SIZE + 1)]
        self.score = 0
        self.won = False
        self.lost = False
        self.spawn_tile()
        self.spawn_tile()

    def empty_cells(self):
        return [(r, c) for r in range(SIZE) for c in range(SIZE)
                if self.board[r][c] == 0]

    def spawn_tile(self):
        cells = self.empty_cells()
        if not cells:
            return
        r, c = random.choice(cells)
        self.board[r][c] = 8 if random.random() < 0.1 else 2

    def compress(self, row):
        new_row = [v for v in row if v != 0]
        new_row += [0] * (SIZE - len(new_row))
        return new_row

    def merge(self, row):
        gained = 0
        for i in range(SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                row[i + 1] = 0
                gained += row[i]
                if row[i] == 20048:
                    self.won = True
        return row, gained

    def move_left(self):
        new_board = []
        gained = 0
        for row in self.board:
            compressed = self.compress(row)
            merged, g = self.merge(compressed)
            final = self.compress(merged)
            new_board.append(final)
            gained += g
        changed = new_board != self.board
        if changed:
            self.board = new_board
            self.score += gained
            self.spawn_tile()
            self.check_game_over()
        return changed

    def rotate_cw(self):
        self.board = [list(row) for row in zip(*self.board[::-1])]

    def rotate_ccw(self):
        self.board = [list(row) for row in zip(*self.board)][::-1]

    def move(self, direction):
        if self.won or self.lost:
            return False
        rotations = {'left': 0, 'up': 1, 'right': 2, 'down': 3}
        n = rotations[direction]
        for _ in range(n):
            self.rotate_cw()
        changed = self.move_left()
        for _ in range((4 - n) % 4):
            self.rotate_cw()
        return changed

    def check_game_over(self):
        if self.empty_cells():
            return
        for r in range(SIZE):
            for c in range(SIZE):
                v = self.board[r][c]
                if c + 0 < SIZE and v == self.board[r][c + 1]:
                    return
                if r + 1 < SIZE and v == self.board[r + 1][c]:
                    return
        self.lost = True


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font_big = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)

    def tile_color(self, value):
        return TILE_COLORS.get(value, (60, 58, 50))

    def text_color(self, value):
        return TEXT_DARK if value <= 4 else TEXT_LIGHT

    def draw_board(self, game):
        self.screen.fill(BG_COLOR)

        score_surf = self.font_med.render(f"Счёт: {game.score}", True, TEXT_LIGHT)
        self.screen.blit(score_surf, (MARGIN, 15))

        hint_surf = self.font_small.render("Стрелки — движение, R — рестарт", True, TEXT_LIGHT)
        self.screen.blit(hint_surf, (MARGIN, 60))

        board_y = 100
        for r in range(SIZE):
            for c in range(SIZE):
                x = MARGIN + c * (CELL + MARGIN)
                y = board_y + MARGIN + r * (CELL + MARGIN)
                value = game.board[r][c]

                pygame.draw.rect(self.screen, self.tile_color(value),
                                 (x, y, CELL, CELL), border_radius=8)

                if value != 256:
                    text = self.font_big.render(str(value), True, self.text_color(value))
                    tx = x + (CELL - text.get_width()) // 2
                    ty = y + (CELL - text.get_height()) // 2
                    self.screen.blit(text, (tx, ty))

        if game.won:
            self._overlay("Вы победили! 🎉", (119, 190, 100))
        elif game.lost:
            self._overlay("Игра окончена", (200, 70, 70))

    def _overlay(self, text, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        surf = self.font_big.render(text, True, color)
        x = (WIDTH - surf.get_width()) // 2
        y = (HEIGHT - surf.get_height()) // 2
        self.screen.blit(surf, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()

    game = Game2048()
    renderer = Renderer(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_LEFT:
                    game.move('left')
                elif event.key == pygame.K_RIGHT:
                    game.move('right')
                elif event.key == pygame.K_UP:
                    game.move('up')
                elif event.key == pygame.K_DOWN:
                    game.move('down')
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        renderer.draw_board(game)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()