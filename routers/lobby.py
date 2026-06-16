from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_current_user
from game.manager import room_manager
from game.room import RoomState

router = APIRouter()

@router.post("/rooms")
async def create_room(user: dict = Depends(get_current_user)):
    """Any authenticated player creates a new waiting room and auto-joins as player 1."""
    room = room_manager.create_room()
    room.join(user["uid"])
    return {
        "room_id": room.room_id,
        "state": room.state,
        "player1": room.player1_uid,
        "player2": room.player2_uid,
    }

@router.post("/rooms/{room_id}/join")
async def join_room(room_id: str, user: dict = Depends(get_current_user)):
    """A second player joins an existing waiting room."""
    room = room_manager.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.full():
        raise HTTPException(status_code=409, detail="Room is full")
    if room.state != RoomState.WAITING:
        raise HTTPException(status_code=409, detail="Room is not waiting")
    if room.player1_uid == user["uid"]:
        raise HTTPException(status_code=409, detail="Already in this room")
    room.join(user["uid"])
    room.state = RoomState.IN_PROGRESS
    return {
        "room_id": room.room_id,
        "state": room.state,
        "player1": room.player1_uid,
        "player2": room.player2_uid,
    }

@router.get("/rooms")
async def list_rooms(user: dict = Depends(get_current_user)):
    """Return all rooms (waiting or in progress) for the lobby feed."""
    rooms = [
        {
            "room_id": r.room_id,
            "state": r.state,
            "player1": r.player1_uid,
            "player2": r.player2_uid,
            "joinable": r.state == RoomState.WAITING and not r.full(),
        }
        for r in room_manager.list_rooms()
    ]
    return {"rooms": rooms}
