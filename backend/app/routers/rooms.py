from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import RoomCreate, RoomJoin, RoomResponse, RoomBasicResponse
from ..services import room_service

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("", response_model=RoomResponse)
def create_room(room_data: RoomCreate, db: Session = Depends(get_db)):
    """Create a new game room."""
    room = room_service.create_room(db, room_data)
    return room


@router.get("/{room_code}", response_model=RoomResponse)
def get_room(room_code: str, db: Session = Depends(get_db)):
    """Get room details by code."""
    room = room_service.get_room_by_code(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("/{room_code}/exists", response_model=RoomBasicResponse)
def check_room_exists(room_code: str, db: Session = Depends(get_db)):
    """Check if a room exists and get basic info."""
    room = room_service.get_room_by_code(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomBasicResponse(
        room_code=room.room_code,
        status=room.status,
        player_count=len(room.players)
    )


@router.post("/{room_code}/join", response_model=RoomResponse)
def join_room(room_code: str, join_data: RoomJoin, db: Session = Depends(get_db)):
    """Join an existing room."""
    room = room_service.get_room_by_code(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.status == "ended":
        raise HTTPException(status_code=400, detail="Game has ended")

    room_service.join_room(db, room, join_data)

    # Refresh to get updated players
    db.refresh(room)
    return room


@router.delete("/{room_code}/leave/{player_id}")
def leave_room(room_code: str, player_id: str, db: Session = Depends(get_db)):
    """Leave a room."""
    room = room_service.get_room_by_code(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room_deleted = room_service.leave_room(db, room, player_id)

    return {"message": "Left room", "room_deleted": room_deleted}
