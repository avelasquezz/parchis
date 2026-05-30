import pygame
import time
import sys

from core.view.board_map import BOARD_MAP

pygame.init()
pygame.font.init()

font       = pygame.font.Font("./assets/dyna-puff.ttf", 32)
font_small = pygame.font.Font("./assets/dyna-puff.ttf", 20)

main_menu        = pygame.image.load("./assets/main-menu.png")
main_menu_hover1 = pygame.image.load("./assets/main-menu-hover1.png")
main_menu_hover2 = pygame.image.load("./assets/main-menu-hover2.png")

create_game_menu        = pygame.image.load("./assets/create-game-menu.png")
create_game_menu_hover1 = pygame.image.load("./assets/create-game-menu-hover1.png")
create_game_menu_hover2 = pygame.image.load("./assets/create-game-menu-hover2.png")

join_game_menu            = pygame.image.load("./assets/join-game-menu.png")
join_game_menu_focus      = pygame.image.load("./assets/join-game-menu-focus.png")
join_game_menu_hover      = pygame.image.load("./assets/join-game-menu-hover.png")
join_game_menu_hover_focus = pygame.image.load("./assets/join-game-menu-hover-focus.png")

board = pygame.image.load("./assets/board.png")

button1 = pygame.Rect(145, 275, 307, 102)
button2 = pygame.Rect(145, 412, 307, 102)

pieces = {
  1: pygame.image.load("./assets/blue-piece.svg"),
  2: pygame.image.load("./assets/yellow-piece.svg"),
  3: pygame.image.load("./assets/green-piece.svg"),
  4: pygame.image.load("./assets/red-piece.svg"),
}

dice_images = {
  1: pygame.image.load("./assets/dice-one.png"),
  2: pygame.image.load("./assets/dice-two.png"),
  3: pygame.image.load("./assets/dice-three.png"),
  4: pygame.image.load("./assets/dice-four.png"),
  5: pygame.image.load("./assets/dice-five.png"),
  6: pygame.image.load("./assets/dice-six.png"),
}

WIDTH, HEIGHT = main_menu.get_width(), main_menu.get_height()

PLAYER_COLORS = {
  1: (  0,  71, 132),   # blue
  2: (244, 210,  58),   # yellow
  3: ( 77, 131,  69),   # green
  4: (164,  37,  48),   # red
}

PLAYER_NAMES = {1: "Blue", 2: "Yellow", 3: "Green", 4: "Red"}

# Internal UI states
STATE_ORDER_ROLL  = "order_roll"   # ceremony: it's MY turn to roll for order
STATE_ORDER_WAIT  = "order_wait"   # ceremony: waiting for another player to roll
STATE_WAIT_TURN   = "wait_turn"    # waiting for another player's turn to finish
STATE_ROLL        = "roll"         # my turn: must click dice
STATE_PICK_PIECE  = "pick_piece"   # must click a piece to move (first die)
STATE_PICK_PIECE2 = "pick_piece2"  # must click a piece to move (second die)
STATE_GAME_OVER   = "game_over"

def main_menu_screen(client):
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Parchis")

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.MOUSEBUTTONDOWN:
        if button1.collidepoint(event.pos):
          response = client.create_game()
          game_id  = response.get("game_id")
          return create_game_menu_screen(client, game_id)
        elif button2.collidepoint(event.pos):
          return join_game_menu_screen(client)

    current_image = main_menu
    mx, my = pygame.mouse.get_pos()
    if button1.collidepoint(mx, my):
      current_image = main_menu_hover1
    elif button2.collidepoint(mx, my):
      current_image = main_menu_hover2

    screen.blit(current_image, (0, 0))
    pygame.display.flip()

def create_game_menu_screen(client, game_id):
  response = client.enter_player(game_id, "Player")
  my_player_id = response.get("player_id")

  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Create")

  error_text = ""

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.MOUSEBUTTONDOWN:
        if button1.collidepoint(event.pos):
          response = client.start_game(game_id)
          if response.get("code") == 31:
            error_text = "You must wait for more players!"
          else:
            return board_screen(client, game_id, my_player_id, response)
        elif button2.collidepoint(event.pos):
          client.exit_game()
          return main_menu_screen(client)

    current_image = create_game_menu
    mx, my = pygame.mouse.get_pos()
    if button1.collidepoint(mx, my):
      current_image = create_game_menu_hover1
    elif button2.collidepoint(mx, my):
      current_image = create_game_menu_hover2

    screen.blit(current_image, (0, 0))

    text_surface = font.render(f"Pin: {game_id}", True, (150, 88, 18))
    tr = text_surface.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 25)
    screen.blit(text_surface, tr)

    err_surface = font.render(error_text, True, (255, 255, 255))
    er = err_surface.get_rect(centerx=WIDTH // 2, top=25)
    screen.blit(err_surface, er)

    pygame.display.flip()

def join_game_menu_screen(client):
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Join")

  text_field        = button1
  active            = False
  user_text         = ""
  waiting_for_start = False
  error_text        = ""
  my_player_id      = None

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.MOUSEBUTTONDOWN:
        active = text_field.collidepoint(event.pos)
        if button2.collidepoint(event.pos):
          if waiting_for_start:
            client.exit_game()
          return main_menu_screen(client)

      if event.type == pygame.KEYDOWN and active:
        if event.key == pygame.K_RETURN:
          pin      = int(user_text)
          response = client.enter_player(pin, "Player")
          if response.get("code") == 21:
            error_text = "Error entering the game!"
          else:
            my_player_id      = response.get("player_id")
            waiting_for_start = True
            error_text        = "Waiting for the game to start!"
            # Block until the host starts; server sends code 9
            code9 = client.wait()
            return board_screen(client, pin, my_player_id, code9)

        elif event.key == pygame.K_BACKSPACE:
          user_text = user_text[:-1]
        else:
          if event.unicode.isdigit() and len(user_text) < 5:
            user_text += event.unicode

    current_image = join_game_menu_focus if active else join_game_menu
    mx, my_pos = pygame.mouse.get_pos()
    if button2.collidepoint(mx, my_pos):
      current_image = join_game_menu_hover_focus if active else join_game_menu_hover

    screen.blit(current_image, (0, 0))

    ts = font.render(user_text, True, (150, 88, 18))
    screen.blit(ts, (text_field.centerx - ts.get_width() // 2,
                     text_field.centery - ts.get_height() // 1.5))

    es = font.render(error_text, True, (255, 255, 255))
    screen.blit(es, es.get_rect(centerx=WIDTH // 2, top=25))

    pygame.display.flip()

def board_screen(client, game_id, my_player_id, initial_response):
  """
  Main game screen. Also handles the turn-order ceremony (code 9).
  initial_response is code 9 (ceremony start) from the server.
  """
  import threading, queue

  screen = pygame.display.set_mode((WIDTH, HEIGHT + 60))
  pygame.display.set_caption("Parchis")

  msg_queue: queue.Queue = queue.Queue()

  def _receiver():
    while True:
      try:
        msg = client.wait()
        msg_queue.put(msg)
      except Exception:
        break

  recv_thread = threading.Thread(target=_receiver, daemon=True)
  recv_thread.start()

  import time as _time

  ui_state      = STATE_ORDER_WAIT
  board_state   = None
  dice_a        = None
  dice_b        = None
  available     = []
  status_text   = ""
  winner_text   = ""
  last_used_die = None

  order_player_order = []
  order_rolls_so_far = {}
  ceremony_end_time  = None          # set when final code 9 arrives
  CEREMONY_END_DELAY = 3.0           # seconds to show final result before game starts
  pending_code10     = None          # holds code 10 while waiting out the delay

  def _build_ceremony_status():
    pending = [pid for pid in order_player_order if pid not in order_rolls_so_far]
    if pending:
      next_pid  = pending[0]
      next_name = PLAYER_NAMES.get(next_pid, f"Player {next_pid}")
      if next_pid == my_player_id:
        return "Press the dice to roll!"
      else:
        return f"Waiting for {next_name} to roll..."
    return "Rolling the dice to determine turn order..."

  def _set_state(resp):
    nonlocal ui_state, board_state, dice_a, dice_b, available
    nonlocal status_text, winner_text, last_used_die
    nonlocal order_player_order, order_rolls_so_far
    nonlocal ceremony_end_time, pending_code10

    code = resp.get("code")

    if resp.get("cells") is not None:
      board_state = resp

    if code == 9:
      order_player_order = resp.get("player_order", order_player_order)
      rolls_raw          = resp.get("rolls_so_far", {})
      order_rolls_so_far = {int(k): v for k, v in rolls_raw.items()}

      if order_rolls_so_far:
        last_roll = order_rolls_so_far[list(order_rolls_so_far.keys())[-1]]
        dice_a    = last_roll["value_a"]
        dice_b    = last_roll["value_b"]

      if "first_player" in resp:
        first       = resp["first_player"]
        fname       = PLAYER_NAMES.get(first, f"Player {first}")
        status_text       = f"{fname} goes first!"
        ui_state          = STATE_ORDER_WAIT
        ceremony_end_time = _time.time()
      else:
        pending = [pid for pid in order_player_order if pid not in order_rolls_so_far]
        ui_state    = STATE_ORDER_ROLL if (pending and pending[0] == my_player_id) else STATE_ORDER_WAIT
        status_text = _build_ceremony_status()

    # Code 10: delay if ceremony just ended 
    elif code == 10:
      if ceremony_end_time is not None:
        # Store it; the main loop will apply it once the delay has passed
        pending_code10 = resp
      else:
        _apply_code10(resp)

    # Normal game codes 
    elif code == 11:
      turn_player = resp.get("player_id")
      available   = list(resp.get("available_pieces", {}).get(str(my_player_id), []))
      if resp.get("dice_value_a") is not None:
        dice_a = resp["dice_value_a"]
        dice_b = resp["dice_value_b"]
      if turn_player == my_player_id:
        ui_state    = STATE_PICK_PIECE if available else STATE_WAIT_TURN
        status_text = "Pick a piece to move with the left die." if available else "No pieces available, turn skipped"
      else:
        ui_state    = STATE_WAIT_TURN
        status_text = f"{PLAYER_NAMES.get(turn_player, f'Player {turn_player}')} is picking piece..."

    elif code == 35:
      if resp.get("dice_value_a") is not None:
        dice_a = resp["dice_value_a"]
        dice_b = resp["dice_value_b"]
      turn_player = resp.get("player_id")
      if turn_player == my_player_id:
        available   = list(resp.get("available_pieces", {}).get(str(my_player_id), []))
        ui_state    = STATE_PICK_PIECE2
        status_text = "Pick a piece to move with the right die."
      else:
        ui_state    = STATE_WAIT_TURN
        status_text = f"{PLAYER_NAMES.get(turn_player, f'Player {turn_player}')} is moving their second piece..."

    elif code in (36, 33):
      if resp.get("dice_value_a") is not None:
        dice_a = resp["dice_value_a"]
        dice_b = resp["dice_value_b"]
      next_player = resp.get("next_player_id")
      if next_player == my_player_id:
        ui_state    = STATE_ROLL
        status_text = "Your turn! Press the dice to roll."
      else:
        ui_state    = STATE_WAIT_TURN
        status_text = f"{PLAYER_NAMES.get(next_player, f'Player {next_player}')}'s turn..."

    elif code == 34:
      ui_state    = STATE_GAME_OVER
      winner_id   = resp.get('winner')
      winner_text = f"{PLAYER_NAMES.get(winner_id, f'Player {winner_id}')} wins!"
      status_text = winner_text

    elif code == 41:
      status_text = "That die has already been used. Pick another piece."

    elif code == 42:
      status_text = "That piece just left jail. Move another one."

  def _apply_code10(resp):
    nonlocal ui_state, status_text
    turn_player = resp.get("player_id")
    if turn_player == my_player_id:
      ui_state    = STATE_ROLL
      status_text = "Your turn! Press the dice to roll."
    else:
      ui_state    = STATE_WAIT_TURN
      status_text = f"{PLAYER_NAMES.get(turn_player, f'Player {turn_player}')}'s turn..."

  # Apply initial code 9
  _set_state(initial_response)

  # piece_rects: updated every draw frame 
  piece_rects: dict = {}
  dice_rect_a = pygame.Rect(0, 0, 0, 0)
  dice_rect_b = pygame.Rect(0, 0, 0, 0)

  # Main loop 
  clock = pygame.time.Clock()

  while True:
    while not msg_queue.empty():
      _set_state(msg_queue.get_nowait())

    # Apply pending code 10 once the ceremony display delay has passed
    if pending_code10 is not None and ceremony_end_time is not None:
      if _time.time() - ceremony_end_time >= CEREMONY_END_DELAY:
        _apply_code10(pending_code10)
        pending_code10    = None
        ceremony_end_time = None

    # Handle pygame events
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my_pos = event.pos

        # Ceremony roll
        if ui_state == STATE_ORDER_ROLL:
          if dice_rect_a.collidepoint(mx, my_pos) or dice_rect_b.collidepoint(mx, my_pos):
            client.send({"code": 8, "game_id": game_id})

        # Regular turn roll
        elif ui_state == STATE_ROLL:
          if dice_rect_a.collidepoint(mx, my_pos) or dice_rect_b.collidepoint(mx, my_pos):
            client.send({"code": 6, "game_id": game_id})

        elif ui_state == STATE_PICK_PIECE:
          clicked = _piece_at(mx, my_pos, piece_rects, available)
          if clicked is not None:
            last_used_die = 'a'
            client.send({"code": 7, "game_id": game_id, "piece_id": clicked, "dice_index": "a"})

        elif ui_state == STATE_PICK_PIECE2:
          clicked = _piece_at(mx, my_pos, piece_rects, available)
          if clicked is not None:
            last_used_die = 'b'
            client.send({"code": 7, "game_id": game_id, "piece_id": clicked, "dice_index": "b"})

    # Draw
    screen.fill((98, 35, 131))
    screen.blit(board, (0, 0))

    if board_state is not None:
      piece_rects = _draw_board(screen, board_state)

    rollable = ui_state in (STATE_ROLL, STATE_ORDER_ROLL)
    dice_rect_a, dice_rect_b = _draw_dice(screen, dice_a, dice_b, rollable)
    _draw_hud(screen, ui_state, status_text, available, winner_text, my_player_id)

    pygame.display.flip()
    clock.tick(30)

# Drawing helpers
def _piece_at(mx, my, piece_rects, available):
  """Return the piece_id that was clicked, or None."""
  for pid, rect in piece_rects.items():
    if pid in available and rect.collidepoint(mx, my):
      return pid
  return None

def _draw_dice(screen, value_a, value_b, rollable=False):
  """
  Draw both dice on the board and return their pygame.Rects.
  When rollable=True draws a yellow highlight so the player knows to click.
  Uses value 1 as placeholder before the first roll.
  """
  img_a = dice_images[int(value_a) if value_a is not None else 1]
  img_b = dice_images[int(value_b) if value_b is not None else 1]

  x_a, y_a = BOARD_MAP["dice_value_a"]
  x_b, y_b = BOARD_MAP["dice_value_b"]

  rect_a = pygame.Rect(x_a, y_a, img_a.get_width(), img_a.get_height())
  rect_b = pygame.Rect(x_b, y_b, img_b.get_width(), img_b.get_height())

  if rollable:
    pygame.draw.rect(screen, (98, 35, 131), rect_a.inflate(6, 6), border_radius=4, width=3)
    pygame.draw.rect(screen, (98, 35, 131), rect_b.inflate(6, 6), border_radius=4, width=3)

  screen.blit(img_a, (x_a, y_a))
  screen.blit(img_b, (x_b, y_b))

  return rect_a, rect_b

def _draw_hud(screen, ui_state, status_text, available, winner_text, my_player_id=None):
  """Draw the status bar below the board. No roll button — dice are clickable."""
  MY_TURN_STATES = (STATE_ROLL, STATE_PICK_PIECE, STATE_PICK_PIECE2, STATE_ORDER_ROLL)
  if ui_state in MY_TURN_STATES and my_player_id is not None:
    bg_color  = PLAYER_COLORS[my_player_id]
    # Use dark text on light backgrounds (yellow), white on dark ones
    r, g, b   = bg_color
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    txt_color = (30, 30, 30) if luminance > 140 else (255, 255, 255)
  else:
    bg_color  = (60, 20, 90)
    txt_color = (255, 255, 255)

  pygame.draw.rect(screen, bg_color, pygame.Rect(0, HEIGHT, WIDTH, 60))

  surf = font_small.render(status_text, True, txt_color)
  screen.blit(surf, surf.get_rect(centerx=WIDTH // 2, top=HEIGHT + 18))

def _draw_board(screen, response) -> dict:
  """
  Draw all pieces on the board.
  Returns a dict of {piece_id: pygame.Rect} for click detection.
  """
  piece_rects = {}

  response_cells       = response.get("cells", {})
  response_jails       = response.get("jails", {})
  response_final_paths = response.get("final_paths", {})
  response_ends        = response.get("finished_pieces", {})

  cells = BOARD_MAP["cells"]
  for cell_id_str, pieces_list in response_cells.items():
    if not pieces_list:
      continue
    cell_id = int(cell_id_str)
    x, y = cells[cell_id]
    for piece_id in pieces_list:
      img  = pieces[piece_id // 10]
      rect = screen.blit(img, (x, y))
      piece_rects[piece_id] = rect
      if cell_id in BOARD_MAP["horizontal_cells"]:
        x += 15
      else:
        y += 15

  jails_map = BOARD_MAP["jails"]
  for player_id_str, pieces_list in response_jails.items():
    if not pieces_list:
      continue
    player_id = int(player_id_str)
    for coords, piece_id in zip(jails_map[player_id], pieces_list):
      x, y = coords
      rect = screen.blit(pieces[piece_id // 10], (x, y))
      piece_rects[piece_id] = rect

  final_paths_map = BOARD_MAP["final_paths"]
  for player_id_str, final_path in response_final_paths.items():
    player_id = int(player_id_str)
    for cell_id_str, pieces_list in final_path.items():
      if not pieces_list:
        continue
      cell_id = int(cell_id_str)
      x, y = final_paths_map[player_id][cell_id]
      for piece_id in pieces_list:
        rect = screen.blit(pieces[piece_id // 10], (x, y))
        piece_rects[piece_id] = rect
        if player_id in (1, 3):
          x += 15
        else:
          y += 15

  ends_map = BOARD_MAP["ends"]
  for player_id_str, pieces_list in response_ends.items():
    if not pieces_list:
      continue
    player_id = int(player_id_str)
    for coords, piece_id in zip(ends_map[player_id], pieces_list):
      x, y = coords
      rect = screen.blit(pieces[piece_id // 10], (x, y))
      piece_rects[piece_id] = rect

  return piece_rects
