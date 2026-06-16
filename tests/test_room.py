import pytest
from game.board import CellState, GameResult
from game.room import GameRoom, RoomState
from game.manager import RoomManager

def test_room_has_two_slots():
    room = GameRoom(room_id="r1")
    assert room.player1_uid is None
    assert room.player2_uid is None

def test_join_room_assigns_players():
    room = GameRoom(room_id="r1")
    slot = room.join("uid1")
    assert slot == CellState.PLAYER1
    slot2 = room.join("uid2")
    assert slot2 == CellState.PLAYER2

def test_join_full_room_raises():
    room = GameRoom(room_id="r1")
    room.join("uid1")
    room.join("uid2")
    with pytest.raises(ValueError):
        room.join("uid3")

def test_make_move_updates_board():
    room = GameRoom(room_id="r1")
    room.join("uid1")
    room.join("uid2")
    room.state = RoomState.IN_PROGRESS
    result = room.make_move(uid="uid1", col=3)
    assert result["result"] == GameResult.ONGOING

def test_wrong_turn_raises():
    room = GameRoom(room_id="r1")
    room.join("uid1")
    room.join("uid2")
    room.state = RoomState.IN_PROGRESS
    with pytest.raises(ValueError, match="Not your turn"):
        room.make_move(uid="uid2", col=0)

def test_manager_creates_and_retrieves_room():
    mgr = RoomManager()
    room = mgr.create_room()
    fetched = mgr.get_room(room.room_id)
    assert fetched is room

def test_manager_list_rooms_returns_all():
    mgr = RoomManager()
    r1 = mgr.create_room()
    r2 = mgr.create_room()
    ids = [r.room_id for r in mgr.list_rooms()]
    assert r1.room_id in ids
    assert r2.room_id in ids
