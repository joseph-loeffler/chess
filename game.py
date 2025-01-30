from board import Board

class ChessGame:
    def __init__(self, current_turn="white", ply=0) -> None:
        self.board = Board(ply)
        self.current_turn = current_turn
    
    def newGame(self, color):
        self.board.initial_setup(color)
        self.board.display()


if __name__ == "__main__":
    game = ChessGame()
    game.newGame("black")
