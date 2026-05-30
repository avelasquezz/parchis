import socket as s
import json

class Client:
  def __init__(self, server_ip, server_port):
    self.socket = s.socket() 
    self.server_ip = server_ip
    self.server_port = server_port
    self.buffer = ""

    self.socket.connect((self.server_ip, self.server_port))
  
  def send(self, data):
    message = json.dumps(data)
    self.socket.send(message.encode())
  
  def receive(self):
    while "\n" not in self.buffer:
      chunk = self.socket.recv(2048).decode()
      if not chunk:
        raise ConnectionError("Connection closed by the server")
      self.buffer += chunk

    line, self.buffer = self.buffer.split("\n", 1)
    return json.loads(line)
  
  def close(self):
    self.socket.close()