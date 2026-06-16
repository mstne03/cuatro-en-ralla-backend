import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from firebase_admin import auth as firebase_auth
from game.manager import room_manager
from game.room import RoomState

router = APIRouter()


async def _verify_ws_token(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        return firebase_auth.verify_id_token(token)
    except Exception:
        return None


@router.websocket("/ws/{room_id}")
async def game_ws(
    websocket: WebSocket,
    room_id: str,
    token: str | None = Query(default=None),
):
    await websocket.accept()

    user = await _verify_ws_token(token)
    if user is None:
        await websocket.send_json({"type": "error", "message": "Unauthorized"})
        await websocket.close(code=4001)
        return

    uid = user["uid"]

    # Get or create the room
    room = room_manager.get_room(room_id)
    if room is None:
        room = room_manager.create_room_with_id(room_id)

    # Assign player slot
    if uid == room.player1_uid or uid == room.player2_uid:
        # Reconnect — already in room
        pass
    elif not room.full():
        slot = room.join(uid)
        if room.full():
            room.state = RoomState.IN_PROGRESS
    else:
        await websocket.send_json({"type": "error", "message": "Room is full"})
        await websocket.close(code=4003)
        return

    room.connections[uid] = websocket

    # Send current state to the newly connected player
    await websocket.send_json({
        "type": "state",
        "board": room.board.to_dict(),
        "current_turn": room.current_turn.value,
        "state": room.state.value,
        "your_role": "player1" if uid == room.player1_uid else "player2",
        "players": room.player_count(),
    })

    # Notify both players when room becomes full
    if room.full() and len(room.connections) == 2:
        for conn in room.connections.values():
            await conn.send_json({
                "type": "start",
                "state": RoomState.IN_PROGRESS.value,
            })

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type != "move":
                continue

            if room.state != RoomState.IN_PROGRESS:
                await websocket.send_json({"type": "error", "message": "Game not started"})
                continue

            col = int(msg.get("col", -1))
            try:
                move_result = room.make_move(uid=uid, col=col)
            except ValueError as e:
                await websocket.send_json({"type": "error", "message": str(e)})
                continue

            broadcast = {
                "type": "move",
                "col": col,
                "board": move_result["board"],
                "current_turn": move_result["current_turn"].value,
                "result": move_result["result"].value,
            }
            for conn in room.connections.values():
                await conn.send_json(broadcast)

    except WebSocketDisconnect:
        room.connections.pop(uid, None)
        # Notify remaining player
        for conn in room.connections.values():
            await conn.send_json({"type": "opponent_disconnected"})
        # Clean up finished or empty rooms
        if not room.connections:
            room_manager.remove_room(room_id)
