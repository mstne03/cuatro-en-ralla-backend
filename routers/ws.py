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

    room = room_manager.get_room(room_id)
    if room is None:
        await websocket.send_json({"type": "error", "message": "Room not found"})
        await websocket.close(code=4004)
        return

    uid = user["uid"]
    if uid not in (room.player1_uid, room.player2_uid):
        await websocket.send_json({"type": "error", "message": "Not in this room"})
        await websocket.close(code=4003)
        return

    room.connections[uid] = websocket

    await websocket.send_json({
        "type": "state",
        "board": room.board.to_dict(),
        "current_turn": room.current_turn.value,
        "state": room.state.value,
        "your_role": "player1" if uid == room.player1_uid else "player2",
    })

    if room.full() and len(room.connections) == 2:
        for conn in room.connections.values():
            await conn.send_json({"type": "start", "state": RoomState.IN_PROGRESS.value})

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
        for conn in room.connections.values():
            await conn.send_json({"type": "opponent_disconnected"})
