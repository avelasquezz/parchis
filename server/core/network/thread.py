import threading
import json

from rich.console import Console
from rich         import print as rprint

global console
console = Console()

class ReceiveThread(threading.Thread):
  def __init__(self, client, client_id, callback):
    super(ReceiveThread, self).__init__()
    self.client    = client
    self.client_id = client_id
    self.callback  = callback

  def run(self):
    try:
      while True:
        data = self.client.recv(1024).decode()

        if data:
          received_data = json.loads(data)

          rprint(f"[blue]Received data from {self.client_id}:[/]\n{data}")
          console.rule(style="grey50")

          self.callback(
            client     = self.client,
            client_id  = self.client_id,
            code       = received_data.get("code"),
            game_id    = received_data.get("game_id"),
            name       = received_data.get("name"),
            piece_id   = received_data.get("piece_id"),
            dice_index = received_data.get("dice_index"),
          )
    except Exception as e:
      rprint(f"\n[red]Error receiving data.\n{e}[/]")


class ResponseThread(threading.Thread):
  def __init__(self, client, client_id, response):
    super(ResponseThread, self).__init__()
    self.client_id = client_id
    self.client    = client
    self.response  = response

  def run(self):
    try:
      sended_data = json.dumps(self.response) + "\n"
      self.client.send(sended_data.encode())

      rprint(f"[blue]Sent data to {self.client_id}:[/]\n{sended_data}")
      console.rule(style="grey50")
    except Exception as e:
      rprint(f"\n[red]Error sending data.\n{e}[/]")
