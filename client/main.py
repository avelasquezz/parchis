import sys
from core.network.parchis_client import ParchisClient
from core.view.view              import main_menu_screen
from rich                        import print as rprint

def main():
  if len(sys.argv) != 3:
    print("Usage: python main.py [SERVER_IP] [SERVER_PORT]")
    exit(1)

  server_ip = sys.argv[1]
  server_port = int(sys.argv[2])

  try:
    client = ParchisClient(server_ip, server_port)
  except Exception as e:
    rprint(f"[red]Error connecting to server.\n{e}[/]")
    exit(1) 
  
  main_menu_screen(client)
      
if __name__ == "__main__":
  main()
