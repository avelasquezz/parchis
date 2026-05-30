from core.network.client import Client

class ParchisClient(Client):
  def __init__(self, server_ip, server_port):
    super().__init__(server_ip, server_port)

  def create_game(self):
    self.send({"code": 1})
    return self.receive()

  def enter_player(self, game_id, name):
    self.send({"code": 2, "name": name, "game_id": game_id})
    return self.receive()

  def start_game(self, game_id):
    self.send({"code": 3, "game_id": game_id})
    return self.receive()   # expects code 10 (first turn notification)

  def exit_game(self):
    self.send({"code": 4})

  def roll_order(self, game_id):
    """Send code 8 to roll dice during the turn-order ceremony."""
    self.send({"code": 8, "game_id": game_id})

  def roll_dice(self, game_id):
    """
    Send code 6 to request a dice roll.
    Server will reply with code 11 (dice values + board state).
    """
    self.send({"code": 6, "game_id": game_id})
    return self.receive()

  def move_piece(self, game_id, piece_id, dice_index):
    """
    Send code 7 to move a piece.

    piece_id   : int  – the piece the player chose
    dice_index : 'a' or 'b' – which of the two dice to consume
    """
    self.send({
      "code"       : 7,
      "game_id"    : game_id,
      "piece_id"   : piece_id,
      "dice_index" : dice_index,
    })
    return self.receive()

  def wait(self):
    """
    Block until the server sends any message.
    Used when it is not this client's turn.
    """
    return self.receive()
