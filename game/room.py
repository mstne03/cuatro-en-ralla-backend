from enum import Enum
from fastapi import WebSocket
from game.board import Board, CellState, GameResult

class RoomState(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class GameRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.player1_uid: str | None = None
        self.player2_uid: str | None = None
        self.board = Board()
        self.state = RoomState.WAITING
        self.current_turn = CellState.PLAYER1
        self.winner: GameResult | None = None
        self.connections: dict[str, WebSocket] = {}

    def join(self, uid: str) -> CellState:
        if self.player1_uid is None:
            self.player1_uid = uid
            return CellState.PLAYER1
        if self.player2_uid is None:
            self.player2_uid = uid
            return CellState.PLAYER2
        raise ValueError("Room is full")

    def make_move(self, uid: str, col: int) -> dict:
        expected_uid = (
            self.player1_uid if self.current_turn == CellState.PLAYER1
            else self.player2_uid
        )
        if uid != expected_uid:
            raise ValueError("Not your turn")
        self.board.drop(col, self.current_turn)
        result = self.board.check_winner()
        if result != GameResult.ONGOING:
            self.state = RoomState.FINISHED
            self.winner = result
        else:
            self.current_turn = (
                CellState.PLAYER2
                if self.current_turn == CellState.PLAYER1
                else CellState.PLAYER1
            )
        return {
            "result": result,
            "board": self.board.to_dict(),
            "current_turn": self.current_turn,
        }

    def full(self) -> bool:
        return self.player1_uid is not None and self.player2_uid is not None
