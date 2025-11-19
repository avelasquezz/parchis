class Player:
  def __init__(self, id, name, color, pieces):
    self.__id = id
    self.__name = name
    self.__color = color
    self.__pieces = pieces
  
  def get_id(self):
    return self.__id
  
  def get_name(self):
    return self.__name

  def get_color(self):
    return self.__color

  def get_pieces(self):
    return self.__pieces