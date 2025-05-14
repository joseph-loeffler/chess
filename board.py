from pieces import Piece, Rook, Bishop, Queen, Knight, King, Pawn
from typing import Generator
import copy

class Board:
    def __init__(self) -> None:
        self.piece_map: dict[tuple[int, int]: Piece] = {}  # (row, col) -> Piece
        self.king_positions = {"white": None, "black": None}
        self.ply = 0
        self.time_since_capture = 0
        self.legal_moves: dict[tuple: list[tuple]] = {}  # pos: (target, promo)
        self.position_history: dict[str, int] = {}
    
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

        self.update_legal_moves()
        self.record_position()

    def in_check(self, color: str) -> bool:
        """Returns True if the king of the given color is in check."""
        return self._in_check_static(self.piece_map, self.king_positions, color)
    
    @staticmethod
    def _in_check_static(piece_map, king_positions, color: str) -> bool:
        """Determines whether the king of the specified color is in check given a board state."""
        curr_king_square = king_positions[color]
        # Check for knights and kings
        for piece_class in [Knight, King]:
            for dr, dc in piece_class.directions:
                row, col = curr_king_square
                row += dr
                col += dc
                attacking_piece = piece_map.get((row, col))
                if isinstance(attacking_piece, piece_class) and attacking_piece.color != color:
                    return True

        # Check vertical and horizontal lines
        for dr, dc in Rook.directions:
            row, col = curr_king_square
            row += dr
            col += dc
            while (row, col) not in piece_map and Piece.in_bounds((row, col)):
                row += dr
                col += dc
            if ((row, col) in piece_map
                and piece_map[(row, col)].color != color
                and isinstance(piece_map[(row, col)], (Rook, Queen))):
                return True

        # Check diagonals
        for dr, dc in Bishop.directions:
            row, col = curr_king_square
            row += dr
            col += dc
            while (row, col) not in piece_map and Piece.in_bounds((row, col)):
                row += dr
                col += dc
            if ((row, col) in piece_map
                and piece_map[(row, col)].color != color
                and isinstance(piece_map[(row, col)], (Bishop, Queen))):
                return True

        # Check for pawns
        diagonals = [(-1, 1), (-1, -1)] if color == "white" else [(1, 1), (1, -1)]
        for dr, dc in diagonals:
            row, col = curr_king_square
            row += dr
            col += dc
            attacking_piece = piece_map.get((row, col))
            if isinstance(attacking_piece, Pawn) and attacking_piece.color != color:
                return True

        return False

    def move_causes_check(self, piece_position: tuple[int, int], target: tuple[int, int]) -> bool:
        """Returns True if moving a piece to the target would place its own king in check."""
        piece = self.piece_map[piece_position]
        simulated_map = self.piece_map.copy()
        simulated_king_positions = self.king_positions.copy()

        simulated_map.pop(piece_position)
        simulated_map[target] = piece

        if isinstance(piece, King):
            simulated_king_positions[piece.color] = target

        return self._in_check_static(simulated_map, simulated_king_positions, piece.color)

    def can_castle(self, color: str, kingside: bool) -> bool:
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

    def update_legal_moves(self) -> None:
        self.legal_moves = {}
        for pos, piece in self.piece_map.items():
            if ((self.ply % 2 == 0 and piece.color != "white")
                or (self.ply % 2 == 1 and piece.color != "black")):
                continue
            self.legal_moves[pos] = []
            moves = piece.valid_moves(pos, self)
            for target, _ in moves:
                if not self.move_causes_check(pos, target):
                    # Handle pawn promotion
                    if isinstance(piece, Pawn) and (target[0] == 0 or target[0] == 7):
                        for promo_piece in [Queen, Knight, Rook, Bishop]:
                            self.legal_moves[pos].append((target, promo_piece))
                    else:
                        self.legal_moves[pos].append((target, None))
            
            # add castles
            if isinstance(piece, King):
                king_row, king_col = pos
                if self.can_castle(piece.color, kingside=True):
                    self.legal_moves[pos].append(((king_row, king_col + 2), None))
                if self.can_castle(piece.color, kingside=False):
                    self.legal_moves[pos].append(((king_row, king_col - 2), None))

    def move(self, piece_position: tuple, target: tuple, promotion_choice: Piece=None):
        """Moves a piece from piece_position to target, handling promotion, castling, en passant,
        and updating game state (ply and legal_moves). Raises ValueError if the move is illegal."""
        if (piece_position) not in self.legal_moves:
            raise ValueError("Not a legal move. Try again.")

        legal_moves = self.legal_moves[piece_position]
        if (not Piece.in_bounds(piece_position) 
            or target not in {move[0] for move in legal_moves}):
            raise ValueError("Not a legal move. Try again.")
        
        piece = self.piece_map.pop(piece_position)

        # if capture or pawn move, reset counter
        if target in self.piece_map or isinstance(piece, Pawn):
            self.time_since_capture = 0
        
        # move the piece
        self.piece_map[target] = piece

        # handle promotion
        if promotion_choice is not None:
            self.piece_map[target] = promotion_choice(piece.color, has_moved=True)

        # remove the taken piece for en passant
        opp_pawn_pos = (piece_position[0], target[1])
        if (isinstance(piece, Pawn)
            and abs(piece_position[0] - target[0]) == abs(piece_position[1] - target[1]) == 1 #diag move
            and opp_pawn_pos in self.piece_map
            and isinstance(self.piece_map[opp_pawn_pos], Pawn)
            and self.piece_map[opp_pawn_pos].color != self.piece_map[target].color):
            
            del self.piece_map[opp_pawn_pos]
            

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
                
        # update pawn if moved two
        if isinstance(piece, Pawn) and abs(piece_position[0] - target[0]) == 2:
            piece.moved_two_ply = self.ply
        piece.has_moved = True

        self.ply += 1
        self.time_since_capture += 1
        if isinstance(piece, Pawn):
            self.position_history = {}  # after pawn move, other positions will never be seen
        self.update_legal_moves()
        self.record_position()
    
    def algebraic_to_index(self, notation: str) -> tuple[int, int]:
        """Converts standard chess notation (e.g., 'e4') to board coordinates (row, col)."""
        if len(notation) != 2:
            raise ValueError(f"Invalid notation: {notation}")

        file_to_col = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        rank_to_row = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}

        file, rank = notation[0], notation[1]

        if file not in file_to_col or rank not in rank_to_row:
            raise ValueError(f"Invalid notation: {notation}")

        return (rank_to_row[rank], file_to_col[file])
    
    def in_checkmate(self, color: str) -> bool:
        """Returns true if color is in checkmate"""
        if self.in_check(color) and all(not moves for moves in self.legal_moves.values()):
            return True
        return False
    
    def is_draw(self):
        """Returns true if the game is a draw"""
        curr_color = "white" if self.ply % 2 == 0 else "black"
        # Stalemate
        if (all(not moves for moves in self.legal_moves.values()) 
            and not self.in_check(curr_color)):
            return True
        
        # Threefold repetition
        if self.position_history[self.compute_position_key()] >= 3:
            return True

        # 50-move rule
        if self.time_since_capture >= 100:
            return True

        # Insufficient material
        pieces = list(self.piece_map.values())
        if all(isinstance(p, (King, Bishop, Knight)) for p in pieces):
            if len(pieces) <= 3:
                # King vs King or King and Bishop/Knight vs King
                return True
            if len(pieces) == 4:
                # King and bishop vs king and bishop (same color bishops)
                bishops = [p for p in pieces if isinstance(p, Bishop)]
                if len(bishops) == 2:
                    bishop_squares = [pos for pos, p in self.piece_map.items() if isinstance(p, Bishop)]
                    same_color = lambda square: (square[0] + square[1]) % 2
                    if same_color(bishop_squares[0]) == same_color(bishop_squares[1]):
                        return True

        return False
    
    def record_position(self):
        key = self.compute_position_key()
        self.position_history[key] = self.position_history.get(key, 0) + 1

    def compute_position_key(self) -> str:
        pieces = []
        for pos in sorted(self.piece_map.keys()):
            piece = self.piece_map[pos]
            pieces.append(f"{piece.color[0]}{type(piece).__name__[0]}{pos[0]}{pos[1]}")
        castling_rights = []
        for color in ["white", "black"]:
            row = 7 if color == "white" else 0
            if isinstance(self.piece_map.get((row, 0)), Rook) and not self.piece_map[(row, 0)].has_moved:
                castling_rights.append(f"{color[0]}Q")
            if isinstance(self.piece_map.get((row, 7)), Rook) and not self.piece_map[(row, 7)].has_moved:
                castling_rights.append(f"{color[0]}K")
        king_moved = ''.join(f"{color[0]}Km" for color in ["white", "black"] if self.piece_map.get(self.king_positions[color], None) and self.piece_map[self.king_positions[color]].has_moved)
        return '|'.join([
            ''.join(pieces),
            ''.join(castling_rights),
            king_moved,
            str(self.ply % 2)
        ])
    
    def generate_successor_state(self, pos, target, promo_choice=None):
        newState = Board()

        # Copy over data
        newState.piece_map = copy.deepcopy(self.piece_map)
        newState.king_positions = copy.deepcopy(self.king_positions)
        newState.ply = self.ply
        newState.time_since_capture = self.time_since_capture
        newState.position_history = copy.deepcopy(self.position_history)

        # Assume move is legal and set legal_moves to include move 
        # (so we don't need to compute legal_moves 2x)
        newState.legal_moves = {pos: [(target, promo_choice)]}

        # Make move
        newState.move(pos, target, promo_choice)

        return newState
    
    def get_all_legal_moves(self) -> Generator:
        """Yields (start_pos, target_pos, promotion_choice) for all legal moves."""
        for pos, moves in self.legal_moves.items():
            for target, promo in moves:
                yield (pos, target, promo)

if __name__ == "__main__":
    pass
