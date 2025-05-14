# I used these pieces: https://github.com/lichess-org/lila/tree/master/public/piece/merida

import pygame
import os
import cairosvg
from io import BytesIO
from board import Board
from ai import ChessAI
from pieces import Queen, Rook, Bishop, Knight

MAX_DEPTH = 2

class ChessGUI:
    def __init__(self, width=600, height=600, ai_color=None):
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
        self.ai_color = ai_color
        self.ai = None
        if self.ai_color is not None:
            self.ai = ChessAI(max_depth=MAX_DEPTH)

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
            # Ignore blank selections and opposite color selections
            current_color = "white" if self.chess_board.ply % 2 == 0 else "black"
            if ((row, col) in self.chess_board.piece_map 
                and self.chess_board.piece_map[(row, col)].color == current_color): 
                self.selected_piece_pos = (row, col)
        else:  # 2nd click
            target = (row, col)
            piece = self.chess_board.piece_map[self.selected_piece_pos]
            promotion_choice = None
            promotion_row = 0 if self.chess_board.ply % 2 == 0 else 7
            if (piece.__class__.__name__ == "Pawn" 
                and target[0] == promotion_row
                and abs(self.selected_piece_pos[0] - promotion_row) == 1):
                promotion_choice = self.promotion_prompt(piece.color)
            try:
                self.chess_board.move(self.selected_piece_pos, target, promotion_choice)
            except ValueError as e:
                print(e)
            
            self.selected_piece_pos = None

            # after 2nd click, check for end-of-game

            # Force visual update before checking end conditions
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

            opp_color = "white" if piece.color == "black" else "black"
            if self.chess_board.in_checkmate(opp_color):
                self.show_end_message(f"{piece.color.capitalize()} wins!")
            elif self.chess_board.is_draw():
                self.show_end_message("Draw!")
    
    def show_end_message(self, message: str):
        """Displays a popup message and waits for user to close or click to continue."""
        font = pygame.font.Font(None, 72)
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))

        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting = False
    
    def promotion_prompt(self, color):
        """Displays a GUI popup and waits for the player to choose a promotion piece."""
        BUTTON_WIDTH, BUTTON_HEIGHT = 100, 50
        SPACING = 20
        BG_COLOR = (30, 30, 30)
        BUTTON_COLOR = (200, 200, 200)
        TEXT_COLOR = (0, 0, 0)

        options = {
            "Q": Queen,
            "R": Rook,
            "B": Bishop,
            "N": Knight,
        }

        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(220)
        overlay.fill(BG_COLOR)
        self.screen.blit(overlay, (0, 0))

        # Draw title
        font = pygame.font.Font(None, 48)
        label = font.render("Choose Promotion Piece:", True, "white")
        label_rect = label.get_rect(center=(self.width // 2, self.height // 2 - 100))
        self.screen.blit(label, label_rect)

        # Draw buttons
        font = pygame.font.Font(None, 36)
        keys = list(options.keys())
        total_width = len(keys) * BUTTON_WIDTH + (len(keys) - 1) * SPACING
        start_x = (self.width - total_width) // 2
        y = self.height // 2

        button_rects = {}

        for i, key in enumerate(keys):
            x = start_x + i * (BUTTON_WIDTH + SPACING)
            rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(self.screen, BUTTON_COLOR, rect)
            text = font.render(key, True, TEXT_COLOR)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            button_rects[key] = rect

        pygame.display.flip()

        # Wait for valid input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key).upper()
                    if key in options:
                        return options[key]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    for key, rect in button_rects.items():
                        if rect.collidepoint(x, y):
                            return options[key]

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

            # Let the AI move if it's their turn
            if self.ai is not None and (
                (self.ai_color == "white" and self.chess_board.ply % 2 == 0)
                or (self.ai_color == "black" and self.chess_board.ply % 2 == 1)
                ):
                move = self.ai.choose_move(self.chess_board)
                if move:
                    self.chess_board.move(*move)

                    # Force visual update after AI move
                    self.draw_board()
                    self.draw_pieces()
                    pygame.display.flip()

                    opp_color = "white" if self.ai_color == "black" else "black"
                    if self.chess_board.in_checkmate(opp_color):
                        self.show_end_message(f"{self.ai_color.capitalize()} wins!")
                    elif self.chess_board.is_draw():
                        self.show_end_message("Draw!")

        
        pygame.quit()


if __name__ == "__main__":
    gui = ChessGUI(ai_color=input("AI color: "))
    gui.run()
