from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
from typing import Dict, Set
from ..database import get_db, SessionLocal
from ..services import room_service, game_service
from ..schemas import PlayerResponse, QuestionResponse

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections per room."""

    def __init__(self):
        # room_code -> set of (websocket, player_id)
        self.rooms: Dict[str, Set[tuple]] = {}

    async def connect(self, websocket: WebSocket, room_code: str, player_id: str):
        await websocket.accept()
        if room_code not in self.rooms:
            self.rooms[room_code] = set()
        self.rooms[room_code].add((websocket, player_id))

    def disconnect(self, websocket: WebSocket, room_code: str, player_id: str):
        if room_code in self.rooms:
            self.rooms[room_code].discard((websocket, player_id))
            if not self.rooms[room_code]:
                del self.rooms[room_code]

    async def broadcast_to_room(self, room_code: str, message: dict, exclude_player: str = None):
        if room_code not in self.rooms:
            return
        for ws, pid in self.rooms[room_code].copy():
            if exclude_player and pid == exclude_player:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                self.rooms[room_code].discard((ws, pid))

    async def send_to_player(self, room_code: str, player_id: str, message: dict):
        if room_code not in self.rooms:
            return
        for ws, pid in self.rooms[room_code]:
            if pid == player_id:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass
                break


manager = ConnectionManager()


def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        pass


@router.websocket("/ws/{room_code}/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_code: str,
    player_id: str
):
    db = SessionLocal()

    try:
        # Verify room exists
        room = room_service.get_room_by_code(db, room_code)
        if not room:
            await websocket.close(code=4004, reason="Room not found")
            return

        await manager.connect(websocket, room_code, player_id)

        # Send current game state to the joining player
        players_data = [
            {
                "id": p.id,
                "player_id": p.player_id,
                "nickname": p.nickname,
                "is_host": p.is_host,
                "joined_at": p.joined_at.isoformat()
            }
            for p in room.players
        ]

        current_card_data = None
        if room.current_card:
            current_card_data = {
                "id": room.current_card.id,
                "content": room.current_card.content,
                "is_system": room.current_card.is_system,
                "created_by": room.current_card.created_by,
                "created_at": room.current_card.created_at.isoformat()
            }

        await websocket.send_json({
            "type": "game_state",
            "status": room.status,
            "current_card": current_card_data,
            "players": players_data
        })

        # Notify others that a player connected
        await manager.broadcast_to_room(
            room_code,
            {
                "type": "player_connected",
                "player_id": player_id,
                "player_count": len(room.players)
            },
            exclude_player=player_id
        )

        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            db.refresh(room)  # Refresh room state

            if message_type == "start_game":
                # Only host can start
                if room.host_id != player_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Only the host can start the game"
                    })
                    continue

                room = room_service.update_room_status(db, room, "playing")
                await manager.broadcast_to_room(room_code, {
                    "type": "game_started",
                    "status": "playing"
                })

            elif message_type == "draw_card":
                if room.status != "playing":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Game is not in progress"
                    })
                    continue

                card = game_service.draw_card(db, room)
                if card:
                    card_data = {
                        "id": card.id,
                        "content": card.content,
                        "is_system": card.is_system,
                        "created_by": card.created_by,
                        "created_at": card.created_at.isoformat()
                    }
                    await manager.broadcast_to_room(room_code, {
                        "type": "card_drawn",
                        "card": card_data,
                        "drawn_by": player_id
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No cards available"
                    })

            elif message_type == "switch_card":
                if room.status != "playing":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Game is not in progress"
                    })
                    continue

                card = game_service.switch_card(db, room)
                if card:
                    card_data = {
                        "id": card.id,
                        "content": card.content,
                        "is_system": card.is_system,
                        "created_by": card.created_by,
                        "created_at": card.created_at.isoformat()
                    }
                    await manager.broadcast_to_room(room_code, {
                        "type": "card_switched",
                        "card": card_data,
                        "switched_by": player_id
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No cards available"
                    })

            elif message_type == "end_game":
                # Only host can end
                if room.host_id != player_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Only the host can end the game"
                    })
                    continue

                room = room_service.update_room_status(db, room, "ended")
                await manager.broadcast_to_room(room_code, {
                    "type": "game_ended",
                    "status": "ended"
                })

            elif message_type == "restart_game":
                # Only host can restart
                if room.host_id != player_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Only the host can restart the game"
                    })
                    continue

                # Clear history and reset status
                from ..models import GameHistory
                db.query(GameHistory).filter(GameHistory.room_id == room.id).delete()
                room.current_card_id = None
                room = room_service.update_room_status(db, room, "waiting")

                await manager.broadcast_to_room(room_code, {
                    "type": "game_restarted",
                    "status": "waiting"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code, player_id)
        # Notify others
        await manager.broadcast_to_room(room_code, {
            "type": "player_disconnected",
            "player_id": player_id
        })
    except Exception as e:
        manager.disconnect(websocket, room_code, player_id)
        print(f"WebSocket error: {e}")
    finally:
        db.close()
