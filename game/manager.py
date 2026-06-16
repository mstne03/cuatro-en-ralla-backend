import uuid
from game.room import GameRoom, RoomState


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, GameRoom] = {}

    def create_room(self) -> GameRoom:
        room_id = str(uuid.uuid4())
        return self.create_room_with_id(room_id)

    def create_room_with_id(self, room_id: str) -> GameRoom:
        room = GameRoom(room_id=room_id)
        self._rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> GameRoom | None:
        return self._rooms.get(room_id)

    def list_rooms(self) -> list[GameRoom]:
        return list(self._rooms.values())

    def remove_room(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)


room_manager = RoomManager()
