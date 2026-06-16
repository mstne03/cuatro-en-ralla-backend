from enum import Enum

ROWS = 6
COLS = 7

class CellState(str, Enum):
    EMPTY = "empty"
    PLAYER1 = "player1"
    PLAYER2 = "player2"

class GameResult(str, Enum):
    ONGOING = "ongoing"
    PLAYER1_WINS = "player1_wins"
    PLAYER2_WINS = "player2_wins"
    DRAW = "draw"

class Board:
    def __init__(self):
        self.grid: list[list[CellState]] = [
            [CellState.EMPTY] * COLS for _ in range(ROWS)
        ]

    def drop(self, col: int, player: CellState) -> int:
        if col < 0 or col >= COLS:
            raise ValueError(f"Column {col} out of range")
        for row in range(ROWS - 1, -1, -1):
            if self.grid[row][col] == CellState.EMPTY:
                self.grid[row][col] = player
                return row
        raise ValueError(f"Column {col} is full")

    def check_winner(self) -> GameResult:
        for player, result in [
            (CellState.PLAYER1, GameResult.PLAYER1_WINS),
            (CellState.PLAYER2, GameResult.PLAYER2_WINS),
        ]:
            if self._has_four(player):
                return result
        if all(self.grid[0][c] != CellState.EMPTY for c in range(COLS)):
            return GameResult.DRAW
        return GameResult.ONGOING

    def _has_four(self, player: CellState) -> bool:
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(self.grid[r][c + i] == player for i in range(4)):
                    return True
        # Vertical
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(self.grid[r + i][c] == player for i in range(4)):
                    return True
        # Diagonal down-right
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(self.grid[r + i][c + i] == player for i in range(4)):
                    return True
        # Diagonal down-left
        for r in range(ROWS - 3):
            for c in range(3, COLS):
                if all(self.grid[r + i][c - i] == player for i in range(4)):
                    return True
        return False

    def to_dict(self) -> dict:
        return {"grid": [[cell.value for cell in row] for row in self.grid]}
