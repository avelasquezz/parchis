# board.py
class Board:
    def __init__(self):
        # id_ficha -> (row, col)
        self.piece_positions = {}
        self.white_path = self.create_white_path()
        self.color_paths = self.create_color_paths()
        self.exit_positions = {1:(2,6), 2:(6,12), 3:(8,2), 4:(12,8)}  # salidas por color

    # ----- Rutas -----
    def create_white_path(self):
        path = []
        for col in range(1, 14):
            path.append((7, col))
        for row in range(6, -1, -1):
            path.append((row, 13))
        for col in range(12, 0, -1):
            path.append((0, col))
        for row in range(1, 7):
            path.append((row, 0))
        return path

    def create_color_paths(self):
        paths = {}
        paths[1] = [(i,7) for i in range(0,7)]     # rojo
        paths[2] = [(7,i) for i in range(14,7,-1)] # azul
        paths[3] = [(7,i) for i in range(0,7)]    # verde
        paths[4] = [(i,7) for i in range(14,7,-1)]# amarillo
        return paths

    # ----- Base y salida -----
    def get_base_position(self, piece_id):
        pid = self.get_player_id(piece_id)
        bases = {1:(0,0),2:(0,14),3:(14,0),4:(14,14)}
        return bases[pid]

    def get_start_path_position(self, piece_id):
        pid = self.get_player_id(piece_id)
        # devuelve la casilla de salida del color
        return self.exit_positions[pid]

    def get_player_id(self, piece_id):
        return piece_id // 10

    # ----- Liberar fichas -----
    def release_pieces(self, player_id):
        for i in range(1,5):
            pid = player_id*10 + i
            self.piece_positions[pid] = self.get_base_position(pid)

    # ----- Movimiento -----
    def move_piece(self, piece_id, steps, is_pair=False):
        if piece_id not in self.piece_positions:
            return None
        pos = self.piece_positions[piece_id]
        base = self.get_base_position(piece_id)

        # Si está en casa solo sale con par
        if pos == base:
            if not is_pair:
                return None
            else:
                # Sale a su casilla de salida
                new_pos = self.get_start_path_position(piece_id)
                self.piece_positions[piece_id] = new_pos
                return new_pos

        # Camino blanco
        if pos in self.white_path:
            idx = self.white_path.index(pos)
            new_idx = idx + steps
            if new_idx < len(self.white_path):
                new_pos = self.white_path[new_idx]
            else:
                overflow = new_idx - len(self.white_path)
                pid = self.get_player_id(piece_id)
                color_path = self.color_paths[pid]
                if overflow < len(color_path):
                    new_pos = color_path[overflow]
                else:
                    new_pos = color_path[-1]  # meta
            self.piece_positions[piece_id] = new_pos
            return new_pos

        # Camino de color
        pid = self.get_player_id(piece_id)
        color_path = self.color_paths[pid]
        if pos in color_path:
            idx = color_path.index(pos)
            new_idx = min(idx + steps, len(color_path)-1)
            new_pos = color_path[new_idx]
            self.piece_positions[piece_id] = new_pos
            return new_pos

        return None

    def get_piece_position(self, piece_id):
        return self.piece_positions.get(piece_id,None)
