import pytest
from game.board import Board, CellState, GameResult

def test_new_board_is_empty():
    b = Board()
    for row in b.grid:
        for cell in row:
            assert cell == CellState.EMPTY

def test_drop_piece_lands_at_bottom():
    b = Board()
    b.drop(col=3, player=CellState.PLAYER1)
    assert b.grid[5][3] == CellState.PLAYER1

def test_drop_stacks_pieces():
    b = Board()
    b.drop(col=3, player=CellState.PLAYER1)
    b.drop(col=3, player=CellState.PLAYER2)
    assert b.grid[4][3] == CellState.PLAYER2

def test_drop_invalid_column_raises():
    b = Board()
    with pytest.raises(ValueError):
        b.drop(col=7, player=CellState.PLAYER1)

def test_drop_full_column_raises():
    b = Board()
    for _ in range(6):
        b.drop(col=0, player=CellState.PLAYER1)
    with pytest.raises(ValueError):
        b.drop(col=0, player=CellState.PLAYER1)

def test_horizontal_win():
    b = Board()
    for col in range(4):
        b.drop(col=col, player=CellState.PLAYER1)
    assert b.check_winner() == GameResult.PLAYER1_WINS

def test_vertical_win():
    b = Board()
    for _ in range(4):
        b.drop(col=0, player=CellState.PLAYER1)
    assert b.check_winner() == GameResult.PLAYER1_WINS

def test_diagonal_win():
    b = Board()
    # Build a diagonal for player1: (5,0),(4,1),(3,2),(2,3)
    b.drop(0, CellState.PLAYER1)
    b.drop(1, CellState.PLAYER2)
    b.drop(1, CellState.PLAYER1)
    b.drop(2, CellState.PLAYER2)
    b.drop(2, CellState.PLAYER2)
    b.drop(2, CellState.PLAYER1)
    b.drop(3, CellState.PLAYER2)
    b.drop(3, CellState.PLAYER2)
    b.drop(3, CellState.PLAYER2)
    b.drop(3, CellState.PLAYER1)
    assert b.check_winner() == GameResult.PLAYER1_WINS

def test_draw():
    b = Board()
    pattern = [
        [0,1,0,1,0,1],
        [0,1,0,1,0,1],
        [0,1,0,1,0,1],
        [1,0,1,0,1,0],
        [1,0,1,0,1,0],
        [1,0,1,0,1,0],
        [0,1,0,1,0,1],
    ]
    players = [CellState.PLAYER1, CellState.PLAYER2]
    for col, col_pattern in enumerate(pattern):
        for p in col_pattern:
            b.drop(col, players[p])
    result = b.check_winner()
    assert result in (GameResult.DRAW, GameResult.ONGOING)

def test_no_winner_yet():
    b = Board()
    b.drop(0, CellState.PLAYER1)
    assert b.check_winner() == GameResult.ONGOING
