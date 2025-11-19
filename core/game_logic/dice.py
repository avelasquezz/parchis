import random

class Dice:
  def __init__(self):
    self.__value_a = None
    self.__value_b = None
  
  def get_value_a(self):
    return self.__value_a

  def get_value_b(self):
    return self.__value_b
  
  def roll(self):
    self.__value_a = random.randint(1, 6)
    self.__value_b = random.randint(1, 6)

    return (self.__value_a, self.__value_b)
  
  def is_pair(self):
    return self.__value_a == self.__value_b