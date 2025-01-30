from pieces import Piece, Rook, Bishop, Queen, Knight, King, Pawn

class Board:
    def __init__(self, ply=0) -> None:
        self.board = {}  # (row, col) -> Piece
        self.king_positions = {"white": None, "black": None}
        self.ply = ply
    
    def display(self):
        """Prints the board in a simple text format."""
        for row in range(8):
            line = ""
            for col in range(8):
                piece = self.board.get((row, col), ".")
                line += str(piece) + " " if isinstance(piece, Piece) else ". "
            print(line)
        print()
    
    def initial_setup(self, color):
        back_line = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_class in enumerate(back_line):
            if color == "white":
                self.board[(0,col)] = piece_class("black")
                self.board[(1,col)] = Pawn("black")
                self.board[(7,col)] = piece_class("white")
                self.board[(6,col)] = Pawn("white")
                self.king_positions["black"] = (0,4)
                self.king_positions["white"] = (7,4)
            elif color == "black":
                self.board[(0,col)] = piece_class("white")
                self.board[(1,col)] = Pawn("white")
                self.board[(7,col)] = piece_class("black")
                self.board[(6,col)] = Pawn("black")
                self.king_positions["white"] = (0,4)
                self.king_positions["black"] = (7,4)
            else:
                raise ValueError("player color should be either 'black' or 'white'.")
            
