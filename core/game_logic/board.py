from rich.console import Console
from rich.table   import Table
from rich.text    import Text

class Board:
  def __init__(self):
    self.__cells = dict()
    for i in range(1, 69):
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
  
    self.__jails = {
      1 : [11, 12, 13, 14],
      2 : [21, 22, 23, 24],
      3 : [31, 32, 33, 34],
      4 : [41, 42, 43, 44]
    }

    self.__ends = {
      1: { 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
      2: { 201: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
      3: { 301: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
      4: { 401: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [] },
    }

  def get_cells(self):
    return self.__cells
  
  def get_start_cells(self):
    return self.__start_cells

  def is_safe_cell(self, cell):
    return cell in self.__safe_cells
  
  def has_capured_pieces(self, player_id):
    return len(self.__jails[player_id]) > 0
  
  def release_pieces(self, player_id):
    start_cell = self.__start_cells[player_id]

    self.__cells[start_cell] = self.__jails[player_id]
    self.__jails[player_id] = []
  
  def __remove_piece(self, piece_id):
    for cell in self.__cells:
      if piece_id in self.__cells[cell]:
        self.__cells[cell].remove(piece_id)
        return cell

    # for cell in self.__ends[piece_id // 10]:
    #   if piece_id in self.__ends[piece_id // 10][cell]:
    #     self.__ends[piece_id // 10][cell].remove(piece_id)
    #     return cell
    
    return None
  
  def __capture_piece(self, piece_id, new_cell):
    if self.is_safe_cell(new_cell):
      return

    occupants = self.__cells[new_cell]

    for occupant in occupants:
      if (piece_id // 10) != (occupant // 10):
        self.__remove_piece(occupant)
        self.__jails[occupant // 10].append(occupant)
        print(f"'{occupant}' captured by '{piece_id}'\n")
  
  def move_piece(self, piece_id, value):
    current_cell = self.__remove_piece(piece_id)

    in_jail_or_finished = current_cell is None
    if in_jail_or_finished:
      return None

    new_cell = current_cell + value
    new_cell = new_cell - 68 if new_cell > 68 else new_cell

    self.__capture_piece(piece_id, new_cell)
    self.__cells[new_cell].append(piece_id)
    return new_cell
  
  def print_jails(self):
    print("Jails")
    for key, value in self.__jails.items():
      print(f"{key} : {value}")
    print("\n")
  
  def print_ends(self):
    print("Ends")
    for key, value in self.__ends.items():
      print(f"{key} : {value}")
    print("\n")

  def print(self, group_size=8):
    console = Console()
    table = Table(show_header=False)

    cells = list(self.__cells.items())
    for i in range(0, len(cells), group_size):
      row = []
      for key, value in cells[i:i + group_size]:
        if self.is_safe_cell(key):
          cell_info = f"[green]{key}: [/green]"
        elif key in self.__start_cells.values():
          cell_info = f"[orange]{key}: [/orange]"
        else:
          cell_info = f"[cyan]{key}: [/cyan]"
        cell_info += ", ".join(str(v) for v in value) if value else "[grey]—[/grey]"
        row.append(cell_info)
      table.add_row(*row)

    console.print(table)