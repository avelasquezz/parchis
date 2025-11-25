# interactive_parques.py
import pygame
from game import Game  # tu backend
import random

pygame.init()
WIDTH, HEIGHT = 700, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Parques Interactivo")

ROWS, COLS = 15, 15
CELL_SIZE = 40
BOARD_WIDTH = CELL_SIZE * COLS
BOARD_HEIGHT = CELL_SIZE * ROWS

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 50, 220)
GREEN = (50, 220, 50)
YELLOW = (220, 220, 50)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
PLAYER_COLORS = {1: RED, 2: BLUE, 3: GREEN, 4: YELLOW}

FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 28, bold=True)

DICE_BUTTON = pygame.Rect(BOARD_WIDTH + 30, 10, 120, 40)

# ------------------ FUNCIONES ------------------

def draw_board(win, game, selected_piece=None, blink=False):
    win.fill(WHITE)
    # Dibujar tablero
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = WHITE
            if row < 6 and col < 6: color = RED
            elif row < 6 and col > 8: color = BLUE
            elif row > 8 and col < 6: color = GREEN
            elif row > 8 and col > 8: color = YELLOW
            elif 6 <= row <= 8 and 6 <= col <= 8: color = BLACK
            elif row == 7 or col == 7: color = GRAY
            pygame.draw.rect(win, color, rect)
            pygame.draw.rect(win, BLACK, rect, 1)

    # ------------------- CASILLAS DE SALIDA -------------------
    exits = {
        1: (2, 6),    # rojo
        2: (6, 12),   # azul
        3: (8, 2),    # verde
        4: (12, 8)    # amarillo
    }
    for pid, (r, c) in exits.items():
        exit_rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(win, PLAYER_COLORS[pid], exit_rect)
        pygame.draw.rect(win, BLACK, exit_rect, 2)  # borde negro

    # Dibujar fichas
    for player in game.get_players():
        color = PLAYER_COLORS[player.get_id()]
        for piece_id in player.get_pieces():
            pos = game.get_board().get_piece_position(piece_id)
            if pos is None:
                if player.get_id() == 1: pos = (0,0)
                elif player.get_id() == 2: pos = (0,14)
                elif player.get_id() == 3: pos = (14,0)
                elif player.get_id() == 4: pos = (14,14)
            draw_piece(win, pos[0], pos[1], color, piece_id, selected=(selected_piece==piece_id))

    # Botón Tirar Dados
    pygame.draw.rect(win, LIGHT_GRAY, DICE_BUTTON)
    pygame.draw.rect(win, BLACK, DICE_BUTTON, 2)
    btn_text = FONT.render("Tirar Dados", True, BLACK)
    win.blit(btn_text, (DICE_BUTTON.x + 10, DICE_BUTTON.y + 10))

    # Dados
    draw_dice(win, game)

    # Turno
    current_player = game.get_current_player()
    if not blink:
        turn_text = BIG_FONT.render(f"Turno: {current_player.get_name()}", True, PLAYER_COLORS[current_player.get_id()])
        win.blit(turn_text, (10, BOARD_HEIGHT + 10))

    pygame.display.update()


def draw_piece(win, x, y, color, piece_id=None, selected=False):
    center = (y*CELL_SIZE + CELL_SIZE//2, x*CELL_SIZE + CELL_SIZE//2)
    radius = CELL_SIZE//3
    pygame.draw.circle(win, color, center, radius)
    pygame.draw.circle(win, BLACK, center, radius, 2)
    if piece_id:
        font = pygame.font.SysFont("Arial", 16, bold=True)
        num_text = font.render(str(piece_id%10), True, BLACK)
        win.blit(num_text, num_text.get_rect(center=center))
    if selected:
        pygame.draw.circle(win, WHITE, center, radius+3, 3)


def draw_dice(win, game):
    dice1, dice2 = game.get_last_roll()
    for i, val in enumerate([dice1, dice2]):
        x = BOARD_WIDTH + 30
        y = 70 + i*80
        size = 60
        pygame.draw.rect(win, WHITE, (x, y, size, size))
        pygame.draw.rect(win, BLACK, (x, y, size, size), 3)
        if val:
            draw_dice_pips(win, x, y, size, val)


def draw_dice_pips(win, x, y, size, val):
    mid = size//2
    offset = size//4
    positions = {
        1: [(mid, mid)],
        2: [(offset, offset), (3*offset, 3*offset)],
        3: [(offset, offset), (mid, mid), (3*offset, 3*offset)],
        4: [(offset, offset), (offset, 3*offset), (3*offset, offset), (3*offset, 3*offset)],
        5: [(offset, offset), (offset, 3*offset), (mid, mid), (3*offset, offset), (3*offset, 3*offset)],
        6: [(offset, offset), (offset, mid), (offset, 3*offset), (3*offset, offset), (3*offset, mid), (3*offset, 3*offset)]
    }
    for px, py in positions[val]:
        pygame.draw.circle(win, BLACK, (x+px, y+py), 5)


# ------------------ BUCLE PRINCIPAL ------------------

def main():
    game = Game()
    game.enter_player("Alice", RED, auto_release=True)
    game.enter_player("Bob", BLUE, auto_release=True)
    game.enter_player("Carol", GREEN, auto_release=True)
    game.enter_player("Dave", YELLOW, auto_release=True)

    clock = pygame.time.Clock()
    run = True
    selected_piece = None
    dice_rolled = False
    last_player_id = game.get_current_player_id()
    blink_counter = 0
    blink_on = False

    while run:
        clock.tick(30)
        current_player_id = game.get_current_player_id()
        if current_player_id != last_player_id:
            last_player_id = current_player_id
            blink_counter = 0
            blink_on = True

        if blink_on:
            blink_counter += 1
            if (blink_counter // 15) % 2 == 0:
                draw_board(WIN, game, selected_piece, blink=True)
            else:
                draw_board(WIN, game, selected_piece)
            if blink_counter > 60:
                blink_on = False
        else:
            draw_board(WIN, game, selected_piece)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Tirar dado
                if DICE_BUTTON.collidepoint(mx, my):
                    game.roll_dice()
                    dice_rolled = True
                    selected_piece = None

                # Seleccionar ficha SOLO si tiró dado
                elif dice_rolled:
                    row, col = my // CELL_SIZE, mx // CELL_SIZE
                    for player in game.get_players():
                        for piece_id in player.get_pieces():
                            pos = game.get_board().get_piece_position(piece_id)
                            if pos is None:
                                if player.get_id() == 1: pos = (0,0)
                                elif player.get_id() == 2: pos = (0,14)
                                elif player.get_id() == 3: pos = (14,0)
                                elif player.get_id() == 4: pos = (14,14)
                            if pos == (row, col) and player.get_id() == game.get_current_player_id():
                                selected_piece = piece_id

                    # Mover ficha con primer dado disponible
                    if selected_piece:
                        a, b = game.get_last_roll()
                        is_pair = a == b
                        for die_index in range(2):
                            if not game.get_dice_used()[die_index]:
                                new_pos, info = game.move_piece_with_die(selected_piece, die_index, is_pair=is_pair)
                                if info["moved"]:
                                    selected_piece = None
                                    dice_rolled = False
                                    break

    pygame.quit()


main()
