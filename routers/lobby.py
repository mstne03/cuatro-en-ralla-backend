from fastapi import APIRouter, Depends
from dependencies import get_current_user
from game.manager import room_manager
from game.room import RoomState

router = APIRouter()


@router.get("/rooms")
async def list_rooms(user: dict = Depends(get_current_user)):
    rooms = [
        {
            "room_id": r.room_id,
            "state": r.state.value,
            "players": r.player_count(),
            "joinable": r.state == RoomState.WAITING and not r.full(),
        }
        for r in room_manager.list_rooms()
        if r.state != RoomState.FINISHED
    ]
    return {"rooms": rooms}
