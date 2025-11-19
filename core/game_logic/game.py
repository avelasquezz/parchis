import random
import os

from core.game_logic.player import Player 
from core.game_logic.board  import Board
from core.game_logic.dice   import Dice 

class Game:
  def __init__(self, id):
    self.__id = id
    self.__board = Board()
    self.__dice = Dice()
    self.__players = list()
    self.__turn_order = dict()
    self.__current_turn = None
    self.__playing = False
  
  def get_board(self):
    return self.__board

  def get_players(self):
    return self.__players
  
  def enter_player(self, name, color):
    number_of_players = len(self.__players)

    if number_of_players == 4:
      raise Exception("The game cannot have more than four players") 
    
    player_id = number_of_players + 1

    pieces = [(player_id * 10) + i for i in range(1, 5)]

    player = Player(player_id, name, color, pieces)

    self.__players.append(player)
  
  def determine_turn_order(self):
    self.__turn_order = {
      1 : 1,
      2 : 2,
      3 : 3,
      4 : 4,
    }

    self.__current_turn = self.__turn_order[1]
  
  def next_turn(self):
    next_turn = self.__current_turn + 1 if self.__current_turn < 4 else 1
    self.__current_turn = self.__turn_order[next_turn] 
  
  def print_state(self, player, value_a, value_b, movement=None, value=None, piece_id=None):
    self.__board.print_jails()
    self.__board.print_ends()
    print(f"Dice: {value_a}, {value_b}")

    if value:
      if movement:
        print(f"Player '{player.get_name()}' moving '{piece_id}' {value} cells\n")
      else:
        print(f"Piece {piece_id} of player '{player.get_name()}' is in jail, finished or the movement exceeds the board\n")
    else:
      print(f"Player '{player.get_name()}' releasing pieces from jail\n")

    self.__board.print()

    input("\nPress Enter to continue...")
    os.system("clear")
  
  def play(self):
    while (True):
      value_a, value_b = self.__dice.roll()

      for player in self.__players:
        player_id = player.get_id()

        if player_id == self.__current_turn:
          if self.__dice.is_pair() and self.__board.has_capured_pieces(player_id):
            self.__board.release_pieces(player_id)
            self.print_state(player, value_a, value_b)
            self.next_turn()
            break

          piece_id = random.choice(player.get_pieces())
          movement = self.__board.move_piece(piece_id, value_a) 
          self.print_state(player, value_a, value_b, movement, value_a, piece_id)

          piece_id = random.choice(player.get_pieces())
          movement = self.__board.move_piece(piece_id, value_b) 
          self.print_state(player, value_a, value_b, movement, value_b, piece_id)

          if not self.__dice.is_pair():
            self.next_turn()

          break
