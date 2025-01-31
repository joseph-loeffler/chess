class Piece:
    def __init__(self, color, has_moved=False) -> None:
        self.color = color
        self.has_moved = has_moved

    def __str__(self):
        """Returns a one-letter representation of the piece for board display."""
        symbol_map = {
            "King": "K",
            "Queen": "Q",
            "Rook": "R",
            "Bishop": "B",
            "Knight": "N",
            "Pawn": "P",
        }
        piece_symbol = symbol_map.get(self.__class__.__name__, "?")
        return piece_symbol if self.color == "white" else piece_symbol.lower()

    @staticmethod
    def in_bounds(position):
        """Check if a position is within the 8x8 chessboard."""
        row, col = position
        return 0 <= row < 8 and 0 <= col < 8

    def get_straight_line_moves(self, position, board, directions):
        """Helper method for pieces that move in straight lines (Rook, Bishop, Queen)."""
        moves = []
        for dr, dc in directions:
            row, col = position
            row += dr
            col += dc
            while Piece.in_bounds((row, col)) and (
                (row, col) not in board or board[(row, col)].color != self.color):

                if (row, col) in board and board[(row, col)].color != self.color:
                    moves.append((row, col))  # Capture opponent piece
                    break  # Stop moving in this direction
                moves.append((row, col))
                row += dr
                col += dc
        return moves
    
    def get_one_away_moves(self, position, board, directions):
        row, col = position
        moves = []
        for dir in directions:
            dr, dc = dir
            if Piece.in_bounds((row + dr, col + dc)) and (
                (row + dr, col + dc) not in board or board[(row + dr, col + dc)].color != self.color):
                moves.append((row + dr, col + dc))
        return moves

    def valid_moves(self, piece_position, board_object):
        """Default method; should be overridden by subclasses."""
        raise NotImplementedError("Each piece must implement its own valid_moves method.")


class Rook(Piece):
    directions = [(0,1),(0,-1),(1, 0),(-1,0)]
    def valid_moves(self, piece_position, board_object):
        return self.get_straight_line_moves(piece_position, board_object.board, self.directions)
    

class Bishop(Piece):
    directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
    def valid_moves(self, piece_position, board_object):
        return self.get_straight_line_moves(piece_position, board_object.board, self.directions)


class Queen(Piece):
    directions = [(0,1),(0,-1),(1, 0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    def valid_moves(self, piece_position, board_object):
        return self.get_straight_line_moves(piece_position, board_object.board, self.directions)
        
    
class Knight(Piece):
    directions = [(1,2), (1,-2), (-1, 2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]
    def valid_moves(self, piece_position, board_object):
        return self.get_one_away_moves(piece_position, board_object.board, self.directions)


class King(Piece):
    directions = [(0,1),(0,-1),(1, 0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    def valid_moves(self, piece_position, board_object):
        return self.get_one_away_moves(piece_position, board_object.board, self.directions)
    

class Pawn(Piece):
    def __init__(self, color, has_moved=False, moved_two_ply = -1) -> None:
        super().__init__(color, has_moved)
        self.moved_two_ply = moved_two_ply

    def valid_moves(self, piece_position, board_object):
        moves = []
        row, col = piece_position
        board = board_object.board
        # Moving forward (one or two) (if nothing blocking)
        direction = -1 if self.color == "white" else 1
        one_forward = (row + direction, col)
        
        if self.in_bounds(one_forward) and one_forward not in board:
            moves.append(one_forward)
            if not self.has_moved:
                two_forward = (row + 2*direction, col)
                if self.in_bounds(two_forward) and two_forward not in board:
                    moves.append(two_forward)
        
        # Moving diagonally (if piece to be captured)
        for dc in [-1,1]:
            diagonal_move = (row + direction, col + dc)
            if diagonal_move in board and board[diagonal_move].color != self.color:
                moves.append(diagonal_move)
            # En passant
            side_pawn_pos = (row, col + dc)
            if (side_pawn_pos in board 
                and board[side_pawn_pos].color != self.color
                and isinstance(board[side_pawn_pos], Pawn)
                and board[side_pawn_pos].moved_two_ply == board_object.ply - 1):
                
                moves.append(diagonal_move)
        
        return moves

if __name__ == "__main__":
    pieces = [King("white"), Queen("white"), Rook("black"), Pawn("black")]

    for piece in pieces:
        print(f"{piece.color}: {piece}")