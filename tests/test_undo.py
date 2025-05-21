import pytest
from board import Board
from pieces import Pawn, Queen, King

def make_move_and_undo(board: Board, action):
    before_key = board.compute_position_key()
    before_time = board.time_since_capture
    piece = board.piece_map[action[0]]
    was_first_move = not piece.has_moved

    if board.is_capture(action):
        capture_details = board.get_capture_details(action)
    else:
        capture_details = [None, None, None]
    board.update_legal_moves()
    board.move(action)

    board.undo_move(
        position=action[0],
        target=action[1],
        promo=action[2],
        was_first_move=was_first_move,
        captured_piece=capture_details[0],
        captured_piece_pos=capture_details[1],
        prev_time_since_capture=capture_details[2]
    )

    after_key = board.compute_position_key()
    assert before_key == after_key, f"Undo failed! \nBefore: {before_key}\nAfter:  {after_key}"

def test_undo_regular_pawn_move():
    board = Board()
    board.initial_setup()
    move = ((6, 4), (4, 4), None)  # e2 to e4
    make_move_and_undo(board, move)

def test_undo_capture():
    board = Board()
    board.initial_setup()
    board.move(((6, 3), (4, 3), None))  # d2 to d4
    board.move(((1, 4), (3, 4), None))  # e7 to e5
    board.move(((7, 6), (5, 5), None))  # Nf3
    board.move(((1, 0), (2, 0), None))  # random black move to alternate turn

    board.piece_map[(4, 7)] = Queen("black")  # manually place a black queen
    board.update_legal_moves()
    move = ((5, 5), (4, 7), None)
    make_move_and_undo(board, move)

def test_undo_en_passant():
    board = Board()
    board.initial_setup()
    board.update_legal_moves()
    board.move(((6, 4), (4, 4), None))  # e2 to e4
    board.move(((1, 3), (3, 3), None))  # d7 to d5
    move = ((4, 4), (3, 3), None)       # en passant
    make_move_and_undo(board, move)

def test_undo_castling_kingside():
    board = Board()
    board.initial_setup()
    board.piece_map.pop((7, 5))
    board.piece_map.pop((7, 6))
    board.update_legal_moves()
    move = ((7, 4), (7, 6), None)
    make_move_and_undo(board, move)

def test_undo_promotion():
    board = Board()
    board.ply = 1  # ensure it's black's turn
    board.piece_map[(6, 0)] = Pawn("black")
    board.piece_map[(7, 4)] = Queen("white")  # white queen
    board.piece_map[(7, 3)] = King("white")
    board.piece_map[(0, 4)] = Queen("black")  # black queen
    board.piece_map[(0, 3)] = King("black")
    
    board.king_positions["white"] = (7, 3)
    board.king_positions["black"] = (0, 3)
    board.update_legal_moves()
    move = ((6, 0), (7, 0), Queen)
    make_move_and_undo(board, move)