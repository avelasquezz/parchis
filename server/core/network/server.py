import socket as s
import json

from core.network.thread import ReceiveThread, ResponseThread
from rich                import print as rprint 

class Server:
  def __init__(self, ip, port):
    self.ip = ip
    self.port = port

    self.socket = s.socket()

    self.socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    self.socket.bind((self.ip, self.port))
    self.socket.listen(1)
    rprint("[bold green]The server is listening.[/]")

    self.clients = dict()
  
  def connect_client(self):
    try:
      client, client_id = self.socket.accept()

      rprint(f"\n[magenta]Client connected. (IP: {client_id[0]}, PORT: {client_id[1]})[/]\n")
    except Exception as e:
      rprint(f"\n[red]Error connecting client.\n{e}[/]")

    self.clients.update({
      client_id : (client, None, None)
    })

    return client, client_id
  
  def receive(self, client, client_id, callback):
    thread = ReceiveThread(client, client_id, callback)
    thread.start()
  
  def response(self, client, client_id, response):
    thread = ResponseThread(client, client_id, response)
    thread.start()

  def disconnect_client(self, client_id):
    client = self.clients.pop(client_id, None)[0]
    if client:
      client.close()
  
  def close_server(self):
    self.socket.close()
