# game.py
import random
import os
from core.game_logic.player import Player
from core.game_logic.board import Board
from core.game_logic.dice import Dice

class Game:
    def __init__(self, id=None):
        self.__id = id
        self.__board = Board()
        self.__dice = Dice()
        self.__players = []
        self.__turn_order = {}
        self.__current_turn = None
        self.__playing = False

        # internal dice state for GUI
        self.__last_roll = (None, None)
        self.__dice_used = [False, False]  # flags para cada dado

        # iniciar orden de turnos
        self.determine_turn_order()

    # --------------- GETTERS ----------------
    def get_board(self):
        return self.__board

    def get_players(self):
        return self.__players

    def get_last_roll(self):
        return self.__last_roll

    def get_dice_used(self):
        return list(self.__dice_used)

    # --------------- PLAYERS ----------------
    def enter_player(self, name, color, auto_release=False):
        number_of_players = len(self.__players)
        if number_of_players == 4:
            raise Exception("The game cannot have more than four players")

        player_id = number_of_players + 1
        pieces = [(player_id * 10) + i for i in range(1, 5)]
        player = Player(player_id, name, color, pieces)
        self.__players.append(player)

        if auto_release:
            self.__board.release_pieces(player_id)

    # --------------- TURNS ----------------
    def determine_turn_order(self):
        # orden 1..n en orden de entrada
        self.__turn_order = {i: i for i in range(1, 5)}
        self.__current_turn = 1 if self.__players else 1

    def get_current_player_id(self):
        return self.__current_turn

    def get_current_player(self):
        for p in self.__players:
            if p.get_id() == self.__current_turn:
                return p
        return None

    def next_turn(self):
        next_turn = self.__current_turn + 1 if self.__current_turn < 4 else 1
        self.__current_turn = self.__turn_order[next_turn]
        self.__dice_used = [False, False]
        self.__last_roll = (None, None)

    # --------------- DICE API ----------------
    def roll_dice(self):
        a, b = self.__dice.roll()
        self.__last_roll = (a, b)
        self.__dice_used = [False, False]
        return self.__last_roll

    def is_last_roll_pair(self):
        a, b = self.__last_roll
        return a is not None and b is not None and a == b

    # --------------- MOVIMIENTO ----------------
    def move_piece_with_die(self, piece_id, die_index, is_pair=False):
        """
        Mueve piece_id usando la tirada die_index (0 o 1)
        is_pair indica si la ficha puede salir de base
        """
        if die_index not in (0, 1):
            return (None, {"moved": False, "error": "die_index debe ser 0 o 1"})

        if self.__last_roll[0] is None or self.__last_roll[1] is None:
            return (None, {"moved": False, "error": "No hay tirada registrada. Llama a roll_dice()."})

        if self.__dice_used[die_index]:
            return (None, {"moved": False, "error": f"Dado {die_index} ya usado."})

        value = self.__last_roll[die_index]

        # PASAR is_pair a Board
        new_cell = self.__board.move_piece(piece_id, value, is_pair=is_pair)

        if new_cell is None:
            self.__dice_used[die_index] = True
            if not self.is_last_roll_pair():
                self.next_turn()
            return (None, {"moved": False, "error": "Movimiento inválido o ficha en base/no puede moverse."})

        # Movimiento válido
        self.__dice_used[die_index] = True
        if all(self.__dice_used):
            if not self.is_last_roll_pair():
                self.next_turn()
        else:
            if not self.is_last_roll_pair():
                self.next_turn()

        return (new_cell, {"moved": True, "error": None})

    # --------------- DEBUG ----------------
    def print_state(self, player, value_a, value_b, movement=None, value=None, piece_id=None):
        self.__board.print_jails()
        self.__board.print_ends()
        print(f"Dice: {value_a}, {value_b}")

        if value:
            if movement:
                print(f"Player '{player.get_name()}' moving '{piece_id}' {value} cells\n")
            else:
                print(f"Piece {piece_id} of player '{player.get_name()}' "
                      f"is in jail, finished or movement exceeds board\n")
        else:
            print(f"Player '{player.get_name()}' releasing pieces from jail\n")

        self.__board.print()
        input("\nPress Enter to continue...")
        os.system("clear")
