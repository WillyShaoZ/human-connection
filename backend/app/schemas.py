from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Question schemas
class QuestionBase(BaseModel):
    content: str


class QuestionCreate(QuestionBase):
    created_by: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: int
    is_system: bool
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Player schemas
class PlayerBase(BaseModel):
    nickname: str
    player_id: str


class PlayerCreate(PlayerBase):
    pass


class PlayerResponse(PlayerBase):
    id: int
    is_host: bool
    joined_at: datetime

    class Config:
        from_attributes = True


# Room schemas
class RoomCreate(BaseModel):
    host_nickname: str
    host_id: str


class RoomJoin(BaseModel):
    nickname: str
    player_id: str


class RoomResponse(BaseModel):
    id: int
    room_code: str
    host_id: str
    status: str
    current_card: Optional[QuestionResponse]
    players: List[PlayerResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class RoomBasicResponse(BaseModel):
    room_code: str
    status: str
    player_count: int


# WebSocket message schemas
class WSMessage(BaseModel):
    type: str
    data: dict


class CardDrawnMessage(BaseModel):
    type: str = "card_drawn"
    card: QuestionResponse


class PlayerJoinedMessage(BaseModel):
    type: str = "player_joined"
    player: PlayerResponse
    player_count: int


class PlayerLeftMessage(BaseModel):
    type: str = "player_left"
    player_id: str
    player_count: int


class GameStateMessage(BaseModel):
    type: str = "game_state"
    status: str
    current_card: Optional[QuestionResponse]
    players: List[PlayerResponse]
