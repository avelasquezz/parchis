import os

from core.game_logic.game import Game

def main():
  players = {
    "Peter" : "Red",
    "Steve" : "Blue",
    "Natasha" : "Yellow",
    "Tony" : "Green",
  }

  game = Game(1)

  for name, color in players.items():
    try:
      game.enter_player(name, color)
    except Exception as e:
      print(e)
  
  for player in game.get_players():
    print(player.get_id(), player.get_name(), player.get_color(), player.get_pieces())

  print("\n")
  
  game.get_board().print()

  game.determine_turn_order()

  input("\nPress Enter to continue...")
  os.system("clear")

  game.play()

if __name__ == "__main__":
  main()
