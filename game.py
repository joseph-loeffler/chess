from board import Board

class ChessGame:
    def __init__(self, ply=0) -> None:
        self.board = Board(ply)
    
    def newGame(self, color="white"):
        self.board.initial_setup()

        while True:
            self.board.display(color)
            color_to_move = "white: " if self.board.ply % 2 == 0 else "black: "
            while True:
                try:
                    move = input(color_to_move).strip().lower().split()
                    if len(move) != 2:
                        raise ValueError("Invalid input! Enter move in format: 'e2 e4'.")
                    piece_position = self.board.algebraic_to_index(move[0])
                    target = self.board.algebraic_to_index(move[1])
                    self.board.move(piece_position, target)
                    break
                except ValueError as e:
                    print(e)
            
            print()


            


if __name__ == "__main__":
    game = ChessGame()
    game.newGame()
    # print(game.board.board[(1,0)].color)
    print(game.board.get_legal_moves((6,0)))
    print(game.board.get_legal_moves((1,0)))
    print(game.board.get_legal_moves((7,1)))
