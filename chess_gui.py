# I used these pieces: https://github.com/lichess-org/lila/tree/master/public/piece/merida

import pygame
import os
import cairosvg
from io import BytesIO
from board import Board

class ChessGUI:
    def __init__(self, width=600, height=600):
        pygame.init()

        self.width = width
        self.height = height
        self.board_size = min(self.width, self.height)
        self.square_size = self.board_size // 8
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Chess")

        self.update_board_size()
        self.pieces = self.load_pieces()

        self.chess_board = Board()
        self.chess_board.initial_setup()
        self.selected_piece_pos = None

    def update_board_size(self):
        """Updates square size dynamically when the window is resized."""
        self.board_size = min(self.width, self.height)
        self.square_size = self.board_size // 8

    def load_pieces(self, piece_set="merida"):
        """Loads SVG pieces and converts them to Pygame surfaces at the correct size."""
        pieces = {}
        piece_names = ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]

        def load_svg_as_surface(svg_path, size):
            png_data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
            return pygame.image.load(BytesIO(png_data))

        for color in ["white", "black"]:
            for piece in piece_names:
                filename = f"{color}_{piece}.svg"
                svg_path = os.path.join(f"assets/{piece_set}", filename)
                pieces[f"{color}_{piece}"] = load_svg_as_surface(svg_path, self.square_size)
        
        return pieces

    def resize_pieces(self):
        """Rescales all piece images when the board size changes."""
        for key in self.pieces:
            piece_image = self.pieces[key]
            self.pieces[key] = pygame.transform.scale(piece_image, (self.square_size, self.square_size))
    
    def draw_board(self):
        """Draws the chessboard with alternating colors."""
        WHITE = (255, 255, 255)
        GREEN = (118, 150, 86)
        YELLOW = (255, 255, 0)
        for row in range(8):
            for col in range(8):
                color = (
                    YELLOW if self.selected_piece_pos == (col,row) 
                    else WHITE if (row + col) % 2 == 0
                    else GREEN
                )
                rect = pygame.Rect(row * self.square_size, col * self.square_size, self.square_size, self.square_size)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        """Draws pieces at their correct positions after resizing."""
        for position, piece in self.chess_board.piece_map.items():
            row, col = position
            piece_image = self.pieces[f"{piece.color}_{piece.__class__.__name__}"]
            self.screen.blit(piece_image, (col * self.square_size, row * self.square_size))

    def handle_click(self, x, y):
        row, col = y // self.square_size, x // self.square_size

        if self.selected_piece_pos is None:  # 1st click
            if (row, col) in self.chess_board.piece_map:  # ignore blank selections
                self.selected_piece_pos = (row, col)
        else:  # 2nd click
            target = (row, col)
            piece = self.chess_board.piece_map[self.selected_piece_pos]
            promotion_choice = None
            if (piece.__class__.__name__ == "Pawn" 
                and (self.selected_piece_pos[0] == 0 or self.selected_piece_pos[0] == 7)):
                promotion_choice = self.promotion_promt(target, piece.color)
            try:
                self.chess_board.move(self.selected_piece_pos, target, promotion_choice)
            except ValueError as e:
                print(e)
            
            self.selected_piece_pos = None
    
    def promotion_prompt(self, color):
        """Displays a GUI popup for the player to choose a promotion piece."""
        BUTTON_WIDTH, BUTTON_HEIGHT = 120, 50
        SPACING = 10
        BG_COLOR = (30, 30, 30)
        BUTTON_COLOR = (200, 200, 200)

        options = {"Q": Queen, "R": Rook, "B": Bishop, "N": Knight}

        menu_x = (self.width - len(options) * (BUTTON_WIDTH + SPACING))
        menu_y = self.height // 2

        font = pygame.font.Font(None, 36)
        text_surface = font.render("Choose Promotion Piece:", True, "white")
        self.screen.blit(text_surface, (menu_x + 60, menu_y - 40))

    def handle_resize(self, new_width, new_height):
        """Handles dynamic resizing of the board."""
        self.width, self.height = new_width, new_height
        self.update_board_size()
        self.resize_pieces()

    def run(self):
        """Runs the game loop, allowing interaction and resizing."""
        running = True
        while running:
            self.screen.fill("black")

            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    self.handle_click(x, y)
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
        
        pygame.quit()


if __name__ == "__main__":
    gui = ChessGUI()
    gui.run()
