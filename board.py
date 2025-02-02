from pieces import Piece, Rook, Bishop, Queen, Knight, King, Pawn

class Board:
    def __init__(self, ply=0) -> None:
        self.piece_map = {}  # (row, col) -> Piece
        self.king_positions = {"white": None, "black": None}
        self.ply = ply
    
    def display(self, player_color="white"):
        """Prints the board with the player's color at the bottom."""
        flipped = player_color == "black"

        row_range = range(8) if not flipped else range(7, -1, -1)
        col_range = range(8) if not flipped else range(7, -1, -1)

        for row in row_range:
            row_label = 8 - row if not flipped else row + 1
            line = f"{row_label} "

            for col in col_range:
                piece = self.piece_map.get((row, col), ".")
                line += str(piece) + " "
            print(line)
        
        col_labels = "  a b c d e f g h" if not flipped else "  h g f e d c b a"
        print(col_labels)
        print()
    
    def initial_setup(self):
        back_line = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_class in enumerate(back_line):
            self.piece_map[(0,col)] = piece_class("black")
            self.piece_map[(1,col)] = Pawn("black")
            self.piece_map[(7,col)] = piece_class("white")
            self.piece_map[(6,col)] = Pawn("white")
        
        self.king_positions["black"] = (0,4)
        self.king_positions["white"] = (7,4)

    def in_check(self, color):
        curr_king_square = self.king_positions[color]
        # Check for knights and kings
        for piece_class in [Knight, King]:
            for dr, dc in piece_class.directions:
                row, col = curr_king_square
                row += dr
                col += dc
                attacking_piece = self.piece_map.get((row,col))
                if (isinstance(attacking_piece, piece_class)
                    and attacking_piece.color != color):
                    return True
            
        # Check the vertical and horizontal lines
        for dr, dc in Rook.directions:
            row, col = curr_king_square
            row += dr
            col += dc
            while (row,col) not in self.piece_map and Piece.in_bounds((row,col)):
                row += dr
                col += dc
            if ((row,col) in self.piece_map
                and self.piece_map[(row,col)].color != color
                and isinstance(self.piece_map[(row,col)], (Rook, Queen))):
                return True
        
        # Check diagonals
        for dr, dc in Bishop.directions:
            row, col = curr_king_square
            row += dr
            col += dc
            while (row,col) not in self.piece_map and Piece.in_bounds((row,col)):
                row += dr
                col += dc
            
            if ((row,col) in self.piece_map 
                and self.piece_map[(row,col)].color != color
                and isinstance(self.piece_map[(row,col)], (Bishop, Queen))):
                return True
            
        # Check for pawns
        diagonals = [(-1,1), (-1,-1)] if color == "white" else [(1,1), (1,-1)]
        for dr, dc in diagonals:
            row, col = curr_king_square
            row += dr
            col += dc
            attacking_piece = self.piece_map.get((row,col))
            if (isinstance(attacking_piece, Pawn)
                and attacking_piece.color != color):
                return True

        return False

    def move_causes_check(self, piece_position, target):
        in_check = False
        # store previous board state
        piece = self.piece_map.pop(piece_position)
        target_square_piece = self.piece_map.get(target)
        
        # modify board temporarily for simulation
        self.piece_map[target] = piece
        if isinstance(piece, King):
            self.king_positions[piece.color] = target

        # check for checks
        if self.in_check(piece.color):
            in_check = True
        
        # return board to initial state
        self.piece_map[piece_position] = piece
        if target_square_piece is None:
            del self.piece_map[target]
        else:
            self.piece_map[target] = target_square_piece
        if isinstance(piece, King):
            self.king_positions[piece.color] = piece_position

        return in_check

    def can_castle(self, color, kingside):
        """Returns True if castling (kingside or queenside) is legal for the given color."""
        king_pos = self.king_positions[color]
        king = self.piece_map[king_pos]
        if king.has_moved or self.in_check(king.color):
            return False
        
        row = king_pos[0]
        rook_col = 7 if kingside else 0
        rook = self.piece_map.get((row, rook_col))
        
        if rook is None or rook.has_moved:
            return False

        path = [(row, col) for col in (range(5,7) if kingside else range(1,4))]
        for square in path:
            if square in self.piece_map or self.move_causes_check(king_pos, square):
                return False
        
        # Check if a knight is blocking queenside castle
        # as the above only checks the king's path
        if not kingside and (7,1) in self.piece_map:
            return False
        
        return True

    def get_legal_moves(self, piece_position):
        if (piece_position not in self.piece_map
            or (self.ply % 2 == 0 and self.piece_map[piece_position].color != "white")
            or (self.ply % 2 == 1 and self.piece_map[piece_position].color != "black")):
            return []
        
        piece = self.piece_map[piece_position]
        moves = piece.valid_moves(piece_position, self)

        legal_moves = []
        for move in moves:
            if not self.move_causes_check(piece_position, move):
                legal_moves.append(move)
        
        # add castles
        if isinstance(piece, King):
            king_row, king_col = piece_position
            if self.can_castle(piece.color, kingside=True):
                legal_moves.append((king_row, king_col + 2))
            if self.can_castle(piece.color, kingside=False):
                legal_moves.append((king_row, king_col - 2))

        return legal_moves

    def move(self, piece_position, target):
        legal_moves = self.get_legal_moves(piece_position)
        if not Piece.in_bounds(piece_position) or target not in legal_moves:
            raise ValueError("Not a legal move. Try again.")
        
        piece = self.piece_map.pop(piece_position)
        self.piece_map[target] = piece

        # update king_positions and move rook if castle
        if isinstance(piece, King):
            self.king_positions[piece.color] = target
            king_row, king_col = piece_position
            if king_col - target[1] == -2:  # kingside
                rook = self.piece_map.pop((king_row, 7))
                self.piece_map[(king_row, 5)] = rook
                rook.has_moved = True
            elif king_col - target[1] == 2:  # queenside
                rook = self.piece_map.pop((king_row, 0))
                self.piece_map[(king_row, 3)] = rook
                rook.has_moved = True

        piece.has_moved = True
        self.ply += 1
    
    def algebraic_to_index(self, notation):
        """Converts standard chess notation (e.g., 'e4') to board coordinates (row, col)."""
        if len(notation) != 2:
            raise ValueError(f"Invalid notation: {notation}")

        file_to_col = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        rank_to_row = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}

        file, rank = notation[0], notation[1]

        if file not in file_to_col or rank not in rank_to_row:
            raise ValueError(f"Invalid notation: {notation}")

        return (rank_to_row[rank], file_to_col[file])
