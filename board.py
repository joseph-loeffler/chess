from pieces import Piece, Rook, Bishop, Queen, Knight, King, Pawn

class Board:
    def __init__(self, ply=0) -> None:
        self.board = {}  # Dictionary: (row, col) -> Piece
        self.king_positions = {"white": None, "black": None}
        self.ply = ply

        pass
