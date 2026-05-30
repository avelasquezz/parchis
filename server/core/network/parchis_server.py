import random

from core.game_logic.game import Game
from core.network.server  import Server

class ParchisServer(Server):
  def __init__(self, ip, port):
    super().__init__(ip, port)

  # Internal helpers

  def __get_game(self, game_id):
    """Return the Game object with the given id, or None."""
    for data in self.clients.values():
      if data[1] is None:
        continue
      if data[1].get_id() == game_id:
        return data[1]
    return None

  def __generate_game_id(self):
    while True:
      game_id = random.randint(10000, 99999)
      collision = any(
        data[1] is not None and data[1].get_id() == game_id
        for data in self.clients.values()
      )
      if not collision:
        return game_id

  def __broadcast(self, game_id, response):
    """Send response to every client that belongs to game_id."""
    for cid, data in self.clients.items():
      if data[1] is None:
        continue
      if data[1].get_id() == game_id:
        self.response(data[0], cid, response)

  def __board_snapshot(self, game):
    """Return a dict with the full board state."""
    board = game.get_board()
    return {
      "cells"            : board.get_cells(),
      "jails"            : board.get_jails(),
      "final_paths"      : board.get_final_paths(),
      "finished_pieces"  : board.get_finished_pieces(),
      "available_pieces" : board.get_available_pieces(),
    }

  def __notify_turn(self, game, game_id):
    """
    Tell every client whose turn it is.
    Code 10 includes a board snapshot so clients always have fresh state
    when a new turn begins (fixes black screen on game start).
    """
    player_id = game.get_current_turn()
    self.__broadcast(game_id, {
      "code"      : 10,
      "player_id" : player_id,
      **self.__board_snapshot(game),
    })

  # Protocol handlers

  def create_game(self, client, client_id):
    game_id = self.__generate_game_id()
    game    = Game(game_id)

    self.clients[client_id] = (client, game)

    self.response(client, client_id, {
      "code"    : 1,
      "game_id" : game_id,
    })

  def enter_player(self, client, client_id, name, game_id):
    game = self.__get_game(game_id)

    if game is None:
      self.response(client, client_id, {"code": 21})
      return

    try:
      player_id = game.enter_player(name)
      self.clients[client_id] = (client, game, player_id)
      self.response(client, client_id, {
        "code"      : 2,
        "player_id" : player_id,
      })
    except Exception:
      self.response(client, client_id, {"code": 21})

  def start_game(self, client, client_id, game_id):
    """
    Code 3 – host starts the game.
    Broadcasts code 9 (ceremony start) with the list of player IDs so
    every client knows whose turn it is to roll for order.
    Does NOT calculate turn order yet — that happens after all players roll.
    """
    game = self.__get_game(game_id)

    if game is None:
      self.response(client, client_id, {"code": 31})
      return

    try:
      player_order = game.start_order_ceremony()
    except Exception:
      self.response(client, client_id, {"code": 31})
      return

    # Code 9: ceremony starts; first player in list rolls first
    self.__broadcast(game_id, {
      "code"         : 9,
      "player_order" : player_order,   # [id, id, ...] in registration order
      "rolls_so_far" : {},             # empty at start
    })

  def roll_order(self, client, client_id, game_id):
    """
    Code 8 – a player rolls their dice during the turn-order ceremony.
    Broadcasts the partial results after each roll (code 9).
    When all players have rolled, broadcasts the final result (code 9 with
    first_player set) and then the first turn notification (code 10).
    """
    game      = self.__get_game(game_id)
    player_id = self.clients[client_id][2]

    try:
      value_a, value_b = game.register_order_roll(player_id)
    except Exception:
      # Already rolled — ignore silently
      return

    rolls_so_far = {
      str(pid): {"value_a": va, "value_b": vb, "total": va + vb}
      for pid, (va, vb) in game.get_order_rolls().items()
    }

    if game.all_players_rolled_order():
      results      = game.finalize_turn_order()
      first_player = game.get_current_turn()

      self.__broadcast(game_id, {
        "code"          : 9,
        "player_order"  : [r["player_id"] for r in results],
        "rolls_so_far"  : rolls_so_far,
        "first_player"  : first_player,
        "dice_value_a"  : value_a,   # last roller's dice shown on board
        "dice_value_b"  : value_b,
      })
      self.__notify_turn(game, game_id)
    else:
      self.__broadcast(game_id, {
        "code"          : 9,
        "player_order"  : list(game.get_order_rolls().keys()) + [
          p.get_id() for p in game.get_players()
          if p.get_id() not in game.get_order_rolls()
        ],
        "rolls_so_far"  : rolls_so_far,
        "dice_value_a"  : value_a,   # current roller's dice shown on board
        "dice_value_b"  : value_b,
      })

  def roll_dice(self, client, client_id, game_id):
    """
    Code 6 – the client whose turn it is requests to roll the dice.

    Response codes sent to all clients
    -----------------------------------
    40  – not your turn (only sent to the requesting client)
    11  – dice rolled; board snapshot included so clients can show
          which pieces are available to move
    """
    game      = self.__get_game(game_id)
    player_id = self.clients[client_id][2]

    if game.get_current_turn() != player_id:
      self.response(client, client_id, {"code": 40})
      return

    value_a, value_b = game.get_dice().roll()

    # Release jailed pieces if the player rolled a pair
    released_count = game.check_release(player_id)

    # If after releasing there are still no available pieces, skip turn now.
    if not game.get_board().has_available_pieces(player_id):
      game.next_turn()
      next_player_id = game.get_current_turn()
      self.__broadcast(game_id, {
        "code"           : 33,
        "next_player_id" : next_player_id,
        "dice_value_a"   : value_a,
        "dice_value_b"   : value_b,
        "winner"         : None,
        **self.__board_snapshot(game),
      })
      return

    # Rule: if more than one piece was released from jail this turn,
    # the player cannot move — turn ends immediately.
    if released_count > 1:
      game.next_turn()
      next_player_id = game.get_current_turn()
      self.__broadcast(game_id, {
        "code"           : 33,
        "next_player_id" : next_player_id,
        "dice_value_a"   : value_a,
        "dice_value_b"   : value_b,
        "winner"         : None,
        **self.__board_snapshot(game),
      })
      return

    # Rule: if exactly one piece was released, the player can only move
    # using one die — mark die 'b' as already used so only 'a' is available.
    if released_count == 1:
      game.get_used_dice()['b'] = True

    self.__broadcast(game_id, {
      "code"         : 11,
      "player_id"    : player_id,
      "dice_value_a" : value_a,
      "dice_value_b" : value_b,
      "released"     : released_count,
      **self.__board_snapshot(game),
    })

  def move_piece(self, client, client_id, game_id, piece_id, dice_index):
    """
    Code 7 – the client sends which piece to move and which die to use.

    dice_index : 'a' or 'b'

    After a valid move the server checks whether both dice have been used:
      - If the player rolled a pair and both values are equal, only one
        move is needed per die (the second move is still required).
      - When both dice are consumed → next turn → broadcast code 10.
      - If the winner is decided → broadcast code 34 instead.

    Response codes sent to all clients
    ------------------------------------
    40  – not your turn
    41  – invalid die index or die already used
    33  – no available pieces, turn skipped
    34  – someone won
    35  – move ok, still has dice to use (sent to all)
    36  – move ok, turn ends (both dice used)
    """
    game      = self.__get_game(game_id)
    player_id = self.clients[client_id][2]

    if game.get_current_turn() != player_id:
      self.response(client, client_id, {"code": 40})
      return

    if dice_index not in ('a', 'b'):
      self.response(client, client_id, {"code": 41})
      return

    result = game.move(piece_id, dice_index, player_id)

    if result == -3:
      # Die already used - silent error, don't consume the die
      self.response(client, client_id, {"code": 41})
      return

    if result == -6:
      # Piece just released from jail, not allowed to move this turn
      self.response(client, client_id, {"code": 42})
      return

    if result == -4:
      # Someone won
      self.__broadcast(game_id, {
        "code"         : 34,
        "winner"       : game.get_winner(),
        "dice_value_a" : game.get_dice().get_value_a(),
        "dice_value_b" : game.get_dice().get_value_b(),
        **self.__board_snapshot(game),
      })
      self.__cleanup_game(game_id)
      return

    # Move was valid – decide whether the turn continues
    if game.both_dice_used():
      if game.get_dice().is_pair():
        # Pair = same player rolls again with fresh dice
        game.reset_dice_for_pair()
      else:
        game.next_turn()

      # Merge the turn notification directly into the move response.
      # This way clients always receive exactly ONE message per action,
      # which prevents buffer desync and blocking in client.wait().
      next_player_id = game.get_current_turn()
      self.__broadcast(game_id, {
        "code"          : 36,
        "player_id"     : player_id,       # who just moved
        "next_player_id": next_player_id,  # whose turn is next
        "dice_value_a"  : game.get_dice().get_value_a(),
        "dice_value_b"  : game.get_dice().get_value_b(),
        "winner"        : None,
        **self.__board_snapshot(game),
      })
    else:
      # Still has one die left – but only keep the turn if the player
      # actually has pieces that can be moved with it.
      if not game.get_board().has_available_pieces(player_id):
        game.next_turn()
        next_player_id = game.get_current_turn()
        self.__broadcast(game_id, {
          "code"           : 33,
          "next_player_id" : next_player_id,
          "dice_value_a"   : game.get_dice().get_value_a(),
          "dice_value_b"   : game.get_dice().get_value_b(),
          "winner"         : None,
          **self.__board_snapshot(game),
        })
      else:
        self.__broadcast(game_id, {
          "code"         : 35,
          "player_id"    : player_id,
          "dice_value_a" : game.get_dice().get_value_a(),
          "dice_value_b" : game.get_dice().get_value_b(),
          "winner"       : None,
          **self.__board_snapshot(game),
        })

  # Cleanup 

  def exit_game(self, client_id):
    data = self.clients.get(client_id)
    if data is None or len(data) < 3:
      return
    client, game, player_id = data
    if game:
      game.exit_player(player_id)
    self.clients[client_id] = (client, None)

  def __cleanup_game(self, game_id):
    """Remove all clients from a finished game."""
    for cid in list(self.clients):
      data = self.clients[cid]
      if data[1] is not None and data[1].get_id() == game_id:
        self.exit_game(cid)
