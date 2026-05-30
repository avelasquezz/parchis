import sys
from core.network.parchis_server import ParchisServer
from rich                        import print as rprint

def callback(client, client_id, code, game_id, name, piece_id, dice_index):
  match code:
    case 1:
      parchis_server.create_game(client, client_id)

    case 2:
      parchis_server.enter_player(client, client_id, name, game_id)

    case 3:
      parchis_server.start_game(client, client_id, game_id)

    case 4:
      parchis_server.exit_game(client_id)

    case 8:
      parchis_server.roll_order(client, client_id, game_id)

    case 6:
      parchis_server.roll_dice(client, client_id, game_id)

    case 7:
      parchis_server.move_piece(client, client_id, game_id, piece_id, dice_index)


def main():
  if len(sys.argv) != 3:
    print("Usage: python main.py [IP] [PORT]")
    exit(1)

  ip   = sys.argv[1]
  port = int(sys.argv[2])

  global parchis_server
  try:
    parchis_server = ParchisServer(ip, port)
  except Exception as e:
    rprint(f"[red]Error initializing server!\n{e}[/]")
    exit(1)

  while True:
    client, client_id = parchis_server.connect_client()
    parchis_server.receive(client, client_id, callback)


if __name__ == "__main__":
  main()
