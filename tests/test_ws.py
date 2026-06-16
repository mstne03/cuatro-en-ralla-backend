import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from game.manager import room_manager
from game.room import RoomState

client = TestClient(app)

def make_room_with_two_players():
    room = room_manager.create_room()
    room.join("uid1")
    room.join("uid2")
    room.state = RoomState.IN_PROGRESS
    return room

def test_ws_connect_without_token_closes():
    room = make_room_with_two_players()
    with client.websocket_connect(f"/ws/{room.room_id}") as ws:
        data = ws.receive_json()
        assert data["type"] == "error"

def test_ws_connect_with_invalid_token_closes():
    room = make_room_with_two_players()
    with patch("routers.ws.firebase_auth.verify_id_token", side_effect=Exception("bad")):
        with client.websocket_connect(f"/ws/{room.room_id}?token=bad") as ws:
            data = ws.receive_json()
            assert data["type"] == "error"
