class Piece:
  def __init__(self, id, color):
    self.__id = id
    self.__color = color 
  
  def get_id(self):
    return self.__id

  def get_color(self):
    return self.__color