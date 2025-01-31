from pieces import Piece, Rook, Bishop, Queen, Knight, King, Pawn

class Board:
    def __init__(self, ply=0) -> None:
        self.board = {}  # (row, col) -> Piece
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
                piece = self.board.get((row, col), ".")
                line += str(piece) + " "
            print(line)
        
        col_labels = "  a b c d e f g h" if not flipped else "  h g f e d c b a"
        print(col_labels)
        print()
    
    def initial_setup(self):
        back_line = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_class in enumerate(back_line):
            self.board[(0,col)] = piece_class("black")
            self.board[(1,col)] = Pawn("black")
            self.board[(7,col)] = piece_class("white")
            self.board[(6,col)] = Pawn("white")
        
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
                attacking_piece = self.board.get((row,col), None)
                if (isinstance(attacking_piece, piece_class)
                    and attacking_piece.color != color):
                    return True
            
        # Check the vertical and horizontal lines
        for dr, dc in Rook.directions:
            row, col = curr_king_square
            row += dr
            col += dc
            while (row,col) not in self.board and Piece.in_bounds((row,col)):
                row += dr
                col += dc
            if ((row,col) in self.board
                and self.board[(row,col)].color != color
                and isinstance(self.board[(row,col)], (Rook, Queen))):
                return True
        
        # Check diagonals
        for dr, dc in Bishop.directions:
            row, col = curr_king_square
            row += dr
            col += dc
            while (row,col) not in self.board and Piece.in_bounds((row,col)):
                row += dr
                col += dc
            
            if ((row,col) in self.board 
                and self.board[(row,col)].color != color
                and isinstance(self.board[(row,col)], (Bishop, Queen))):
                return True
            
        # Check for pawns
        diagonals = [(-1,1), (-1,-1)] if color == "white" else [(1,1), (1,-1)]
        for dr, dc in diagonals:
            row, col = curr_king_square
            row += dr
            col += dc
            attacking_piece = self.board.get((row,col), None)
            if (isinstance(attacking_piece, Pawn)
                and attacking_piece.color != color):
                return True

        return False

    def get_legal_moves(self, piece_position):
        if (piece_position not in self.board
            or (self.ply % 2 == 0 and self.board[piece_position].color != "white")
            or (self.ply % 2 == 1 and self.board[piece_position].color != "black")):
            return []
        
        piece = self.board[piece_position]
        moves = piece.valid_moves(piece_position, self)

        legal_moves = []
        for move in moves:
            # store previous board state
            starting_square_piece = self.board[piece_position]
            target_square_piece = None
            if move in self.board:
                target_square_piece = self.board[move]
            
            # modify board temporarily for simulation
            del self.board[piece_position]
            self.board[move] = piece
            if isinstance(piece, King):
                self.king_positions[piece.color] = move

            # check for checks
            if not self.in_check(piece.color):
                legal_moves.append(move)
            
            # return board to initial state
            self.board[piece_position] = starting_square_piece
            if target_square_piece is None:
                del self.board[move]
            else:
                self.board[move] = target_square_piece
            if isinstance(piece, King):
                self.king_positions[piece.color] = piece_position
        
        return legal_moves

    def move(self, piece_position, target):
        legal_moves = self.get_legal_moves(piece_position)
        if not Piece.in_bounds(piece_position) or target not in legal_moves:
            raise ValueError("Not a legal move. Try again.")
        
        self.board[target] = self.board[piece_position]
        del self.board[piece_position]

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

        
