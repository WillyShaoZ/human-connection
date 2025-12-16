import random
import string
from sqlalchemy.orm import Session
from ..models import Room, Player
from ..schemas import RoomCreate, RoomJoin


def generate_room_code(length: int = 6) -> str:
    """Generate a random uppercase alphanumeric room code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def create_room(db: Session, room_data: RoomCreate) -> Room:
    """Create a new room with the host as the first player."""
    # Generate unique room code
    while True:
        room_code = generate_room_code()
        existing = db.query(Room).filter(Room.room_code == room_code).first()
        if not existing:
            break

    # Create room
    room = Room(
        room_code=room_code,
        host_id=room_data.host_id,
        status="waiting"
    )
    db.add(room)
    db.flush()

    # Add host as first player
    host_player = Player(
        room_id=room.id,
        player_id=room_data.host_id,
        nickname=room_data.host_nickname,
        is_host=True
    )
    db.add(host_player)
    db.commit()
    db.refresh(room)

    return room


def get_room_by_code(db: Session, room_code: str) -> Room | None:
    """Get room by its code."""
    return db.query(Room).filter(Room.room_code == room_code.upper()).first()


def join_room(db: Session, room: Room, join_data: RoomJoin) -> Player:
    """Add a player to an existing room."""
    # Check if player already in room
    existing_player = db.query(Player).filter(
        Player.room_id == room.id,
        Player.player_id == join_data.player_id
    ).first()

    if existing_player:
        return existing_player

    player = Player(
        room_id=room.id,
        player_id=join_data.player_id,
        nickname=join_data.nickname,
        is_host=False
    )
    db.add(player)
    db.commit()
    db.refresh(player)

    return player


def leave_room(db: Session, room: Room, player_id: str) -> bool:
    """Remove a player from a room. Returns True if room should be deleted."""
    player = db.query(Player).filter(
        Player.room_id == room.id,
        Player.player_id == player_id
    ).first()

    if not player:
        return False

    was_host = player.is_host
    db.delete(player)

    # Check remaining players
    remaining = db.query(Player).filter(Player.room_id == room.id).all()

    if not remaining:
        # No players left, delete room
        db.delete(room)
        db.commit()
        return True

    # If host left, assign new host
    if was_host and remaining:
        remaining[0].is_host = True
        room.host_id = remaining[0].player_id

    db.commit()
    return False


def update_room_status(db: Session, room: Room, status: str) -> Room:
    """Update room status."""
    room.status = status
    db.commit()
    db.refresh(room)
    return room
