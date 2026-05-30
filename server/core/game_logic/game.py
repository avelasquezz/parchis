import random

from core.game_logic.player import Player
from core.game_logic.board  import Board
from core.game_logic.dice   import Dice

class Game:
  def __init__(self, id):
    self.__id            = id
    self.__board         = Board()
    self.__dice          = Dice()
    self.__players       = list()
    self.__current_turn = None
    self.__playing       = False
    self.__winner        = None

    # Tracks which dice values have been used this turn.
    # Each turn starts with {'a': False, 'b': False}.
    self.__used_dice = {'a': False, 'b': False}

    # piece_id of the piece that just left jail this turn (if any).
    # That piece cannot be moved until the next turn.
    self.__just_released = None

    # piece_id of the piece that captured an enemy this turn (if any).
    # That piece cannot be moved again in the same turn.
    self.__last_captor = None

    # Stores {player_id: (value_a, value_b)} during turn-order ceremony
    self.__order_rolls = {}

  # Getters 

  def get_id(self):
    return self.__id

  def get_board(self):
    return self.__board

  def get_dice(self):
    return self.__dice

  def get_players(self):
    return self.__players

  def get_current_turn(self):
    return self.__current_turn

  def get_winner(self):
    return self.__winner

  def get_used_dice(self):
    return self.__used_dice

  # Player management 

  def enter_player(self, name):
    number_of_players = len(self.__players)

    if number_of_players == 4:
      raise Exception("The game cannot have more than four players")

    player_id = number_of_players + 1
    player    = Player(player_id, name)
    self.__players.append(player)
    return player_id

  def exit_player(self, player_id):
    for player in self.__players:
      if player.get_id() == player_id:
        self.__players.remove(player)

  # Turn management 

  def start_order_ceremony(self):
    """Called when the host starts the game. Returns the list of player IDs
    in registration order so the server knows who still needs to roll."""
    if len(self.__players) < 2:
      raise Exception("The game must have at least two players")
    # order_rolls stores {player_id: (value_a, value_b)} as players roll
    self.__order_rolls = {}
    return [p.get_id() for p in self.__players]

  def register_order_roll(self, player_id):
    """
    Roll dice for player_id during the turn-order ceremony.
    Returns (value_a, value_b).
    Raises if this player already rolled.
    """
    if player_id in self.__order_rolls:
      raise Exception("Player already rolled for order")
    value_a, value_b = self.__dice.roll()
    self.__order_rolls[player_id] = (value_a, value_b)
    return value_a, value_b

  def all_players_rolled_order(self):
    """True when every player has rolled for turn order."""
    return len(self.__order_rolls) == len(self.__players)

  def finalize_turn_order(self):
    """
    Must be called after all_players_rolled_order() is True.
    Determines who goes first (highest sum), sets __current_turn,
    and returns sorted results list [{player_id, value_a, value_b, total}].
    """
    greater_value = 0
    first_turn    = 0
    results       = []

    for player_id, (value_a, value_b) in self.__order_rolls.items():
      total = value_a + value_b
      results.append({
        "player_id" : player_id,
        "value_a"   : value_a,
        "value_b"   : value_b,
        "total"     : total,
      })
      if total > greater_value:
        greater_value = total
        first_turn    = player_id

    self.__current_turn = first_turn
    self.__reset_used_dice()
    return sorted(results, key=lambda r: r["total"], reverse=True)

  def get_order_rolls(self):
    return self.__order_rolls

  def next_turn(self):
    number_of_players   = len(self.__players)
    self.__current_turn = (
      self.__current_turn + 1 if self.__current_turn < number_of_players else 1
    )
    self.__reset_used_dice()

  def __reset_used_dice(self):
    self.__used_dice     = {'a': False, 'b': False}
    self.__just_released = None
    self.__last_captor   = None

  def both_dice_used(self):
    """Returns True when the player has consumed both dice values."""
    return self.__used_dice['a'] and self.__used_dice['b']

  # Game phases

  def check_release(self, player_id):
    """
    Phase 1 – called right after rolling.
    If the player rolled a pair AND has pieces in jail, release them.
    Returns the number of pieces that were in jail (0 means nothing released).
    When exactly one piece is released, stores its id in __just_released so
    move() can block it from being moved this turn.
    """
    jail_count = len(self.__board.get_jails()[player_id])
    if self.__dice.is_pair() and jail_count > 0:
      # Remember which piece is about to leave jail (first in list)
      # before release_pieces clears the jail.
      released_piece = self.__board.get_jails()[player_id][0] if jail_count == 1 else None
      self.__board.release_pieces(player_id)
      self.__just_released = released_piece  # None when multiple pieces freed
      return jail_count
    return 0

  def get_just_released(self):
    return self.__just_released

  def move(self, piece_id, dice_index, player_id):
    """
    Phase 2 – move one piece using one of the two dice values.

    dice_index : 'a' or 'b'

    Return codes
    ------------
    -6  – piece just released from jail, cannot move this turn (die kept)
    -4  – this player just won  (avoids collision with cell number 34)
    -3  – that die was already used this turn
    -2  – piece reached the end (finished)
    -1  – move exceeds board (piece can't advance that far)
     0  – piece not on board (jail / already finished)
    >0  – new cell number (1-68 for main track, 101-107 for final path)
    """
    if self.__used_dice[dice_index]:
      return -3

    # Block the piece that just left jail this turn
    if piece_id == self.__just_released:
      return -6  # die is NOT consumed

    # Block the piece that captured an enemy on the previous die
    if piece_id == self.__last_captor:
      return -6  # die is NOT consumed

    value = (
      self.__dice.get_value_a() if dice_index == 'a'
      else self.__dice.get_value_b()
    )

    if not self.__board.has_available_pieces(player_id):
      self.next_turn()
      return -5  # fallback skip (should normally be caught in roll_dice)

    result = self.__board.move_piece(piece_id, value)

    # If this move sent an enemy to jail, remember the piece so it
    # cannot be moved again with the second die this turn.
    if self.__board.did_capture_on_last_move():
      self.__last_captor = piece_id

    if result == -1:
      # The chosen piece cannot advance that far. Only consume the die if
      # no other available piece could move with this value either — that
      # way the player can try a different piece without losing the die.
      if not self.__board.has_any_valid_move(player_id, value):
        self.__used_dice[dice_index] = True
    else:
      # Valid move (including -2 finished, 0 jail, >0 cell): consume die.
      self.__used_dice[dice_index] = True

    if len(self.__board.get_finished_pieces()[player_id]) == 4:
      self.__winner = player_id
      return -4  # victory — safe, can never be a cell number

    return result

  def reset_dice_for_pair(self):
    """Called by the server when the player rolled a pair and consumed
    both dice, granting an extra roll.  Kept as a method to avoid
    exposing the internal dict via get_used_dice()."""
    self.__reset_used_dice()
