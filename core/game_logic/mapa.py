# mapa.py
import pygame
from game import Game

pygame.init()
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Parques con Backend")

ROWS, COLS = 15, 15
CELL_SIZE = WIDTH // COLS

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 50, 220)
GREEN = (50, 220, 50)
YELLOW = (220, 220, 50)
GRAY = (200, 200, 200)
PLAYER_COLORS = {1: RED, 2: BLUE, 3: GREEN, 4: YELLOW}

def draw_board(win, game):
    win.fill(WHITE)
    # Dibujar casillas
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = WHITE
            if row < 6 and col < 6:
                color = RED
            elif row < 6 and col > 8:
                color = BLUE
            elif row > 8 and col < 6:
                color = GREEN
            elif row > 8 and col > 8:
                color = YELLOW
            elif (col == 7 and 0 <= row <= 6):
                color = RED
            elif (row == 7 and 8 <= col <= 14):
                color = BLUE
            elif (col == 7 and 8 <= row <= 14):
                color = GREEN
            elif (row == 7 and 0 <= col <= 6):
                color = YELLOW
            elif 6 <= row <= 8 and 6 <= col <= 8:
                color = BLACK
            elif row == 0 or row == ROWS-1 or col == 0 or col == COLS-1 or row == 7 or col == 7:
                color = GRAY
            pygame.draw.rect(win, color, rect)
            pygame.draw.rect(win, BLACK, rect, 1)

    # Dibujar fichas
    for player in game.get_players():
        color = PLAYER_COLORS[player.get_id()]
        for piece_id in player.get_pieces():
            pos = game.get_board().get_piece_position(piece_id)
            if pos is None:
                # ficha en casa (esquinas)
                if player.get_id() == 1:
                    x, y = 0, 0
                elif player.get_id() == 2:
                    x, y = 0, 14
                elif player.get_id() == 3:
                    x, y = 14, 0
                elif player.get_id() == 4:
                    x, y = 14, 14
            else:
                x, y = pos
            pygame.draw.circle(win, color, (y*CELL_SIZE + CELL_SIZE//2, x*CELL_SIZE + CELL_SIZE//2), CELL_SIZE//3)

    pygame.display.update()

def main():
    game = Game()
    game.enter_player("Alice", RED, auto_release=True)
    game.enter_player("Bob", BLUE, auto_release=True)
    game.enter_player("Carol", GREEN, auto_release=True)
    game.enter_player("Dave", YELLOW, auto_release=True)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_board(WIN, game)

    pygame.quit()

main()
