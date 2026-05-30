class Board:
  def __init__(self):
    """
    The board is represented using a dictionary like that:

    {
      1:  [],
      2:  [],
      ...
      68: []
    }

    Each key of the dictionary represents a cell and the value of the each key represents the list of pieces into that cell
    """
    self.__cells = dict()
    for i in range(1, 69): # Initialize each cell of the board with empty lists
      self.__cells[i] = []
    
    self.__safe_cells = [5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63, 68]

    self.__start_cells = {
      1 : 5,
      2 : 22,
      3 : 39,
      4 : 56
    }

    self.__final_cells = {
      1 : 68,
      2 : 17,
      3 : 34,
      4 : 51
    }
  
    # All pieces starts in the their jails
    self.__jails = {
      1 : [11, 12, 13, 14],
      2 : [21, 22, 23, 24],
      3 : [31, 32, 33, 34],
      4 : [41, 42, 43, 44]
    }

    self.__final_paths = {
      1: { 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
      2: { 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
      3: { 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
      4: { 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
    }

    self.__finished_pieces = {
      1: [],
      2: [],
      3: [],
      4: []
    }

    self.__available_pieces = {
      1: [],
      2: [],
      3: [],
      4: []
    }

    # Set to True by __capture_piece when an enemy piece is sent to jail.
    # Reset to False at the start of every move_piece call.
    self.__last_move_captured = False

  def get_cells(self):
    return self.__cells
  
  def get_start_cells(self):
    return self.__start_cells
  
  def get_jails(self):
    return self.__jails
  
  def get_final_paths(self):
    return self.__final_paths
  
  def get_finished_pieces(self):
    return self.__finished_pieces
  
  def get_available_pieces(self):
    return self.__available_pieces

  def is_safe_cell(self, cell):
    return cell in self.__safe_cells
  
  def has_captured_pieces(self, player_id):
    return len(self.__jails[player_id]) > 0
  
  def has_available_pieces(self, player_id):
    return len(self.__available_pieces[player_id]) > 0
  
  def release_pieces(self, player_id):
    start_cell = self.__start_cells[player_id]

    piece_id = self.__jails[player_id][0]
    self.__capture_piece(piece_id, start_cell, ignore_safe_cell=True)
    self.__cells[start_cell] += self.__jails[player_id]
    self.__available_pieces[player_id] += self.__jails[player_id]
    self.__jails[player_id] = []

  def __get_current_cell(self, piece_id):
    for cell in self.__cells:
      if piece_id in self.__cells[cell]:
        return cell

    for cell in self.__final_paths[piece_id // 10]:
      if piece_id in self.__final_paths[piece_id // 10][cell]:
        return cell

    return None
  
  def __remove_piece(self, piece_id):
    cell = self.__get_current_cell(piece_id)

    if cell < 100:
      self.__cells[cell].remove(piece_id)
    else:
      self.__final_paths[piece_id // 10][cell].remove(piece_id)

  def __capture_piece(self, piece_id, new_cell, ignore_safe_cell=False):
    if self.is_safe_cell(new_cell) and not ignore_safe_cell:
      return

    # Iterate over a copy: __remove_piece modifies self.__cells[new_cell]
    # in place, so iterating the original list would skip occupants.
    occupants = list(self.__cells[new_cell])

    for occupant in occupants:
      if (piece_id // 10) != (occupant // 10):
        self.__remove_piece(occupant)
        self.__available_pieces[occupant // 10].remove(occupant)
        self.__jails[occupant // 10].append(occupant)
        self.__last_move_captured = True
        print(f"'{occupant}' captured by '{piece_id}'\n")
  
  def __enter_the_final_path(self, piece_id, value):
    player_id = piece_id // 10
    final_path = self.__final_paths[player_id]
    final_path[value].append(piece_id)
  
  def can_move_piece(self, piece_id, value):
    """
    Returns True if moving piece_id by value would be a valid move.
    Does not modify any state.
    """
    current_cell = self.__get_current_cell(piece_id)
    if current_cell is None:
      return False

    new_cell = current_cell + value

    crossed_cells = list(range(current_cell, new_cell))
    if self.__final_cells[piece_id // 10] in crossed_cells:
      new_cell = (new_cell - self.__final_cells[piece_id // 10]) + 100
    elif not new_cell > 100:
      new_cell = new_cell - 68 if new_cell > 68 else new_cell

    return new_cell <= 108

  def has_any_valid_move(self, player_id, value):
    """
    Returns True if at least one available piece of player_id
    can legally move by value.
    """
    for piece_id in self.__available_pieces[player_id]:
      if self.can_move_piece(piece_id, value):
        return True
    return False

  def did_capture_on_last_move(self):
    """Returns True if the last move_piece call sent an enemy piece to jail."""
    return self.__last_move_captured

  def move_piece(self, piece_id, value):
    self.__last_move_captured = False  # reset before each move
    current_cell = self.__get_current_cell(piece_id)

    if current_cell is None: # The piece is in jail or is already finished
      return 0
    
    new_cell = current_cell + value

    crossed_cells = list(range(current_cell, new_cell))
    if self.__final_cells[piece_id // 10] in crossed_cells:
      new_cell = (new_cell - self.__final_cells[piece_id // 10]) + 100
    elif not new_cell > 100:
      new_cell = new_cell - 68 if new_cell > 68 else new_cell
    
    if new_cell > 108: # The piece exceeds the board
      return -1 
    
    self.__remove_piece(piece_id)

    if new_cell == 108: # The piece is finished
      self.__finished_pieces[piece_id // 10].append(piece_id)
      self.__available_pieces[piece_id // 10].remove(piece_id)
      return -2 

    if new_cell > 100:
      self.__final_paths[piece_id // 10][new_cell].append(piece_id)
      return new_cell

    self.__capture_piece(piece_id, new_cell)
    self.__cells[new_cell].append(piece_id)
    return new_cell
