from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_system = Column(Boolean, default=True)
    created_by = Column(String(50), nullable=True)  # room_code for user-created
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_code = Column(String(6), unique=True, nullable=False, index=True)
    host_id = Column(String(50), nullable=False)
    status = Column(String(20), default="waiting")  # waiting, playing, ended
    current_card_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    current_card = relationship("Question", foreign_keys=[current_card_id])
    players = relationship("Player", back_populates="room", cascade="all, delete-orphan")
    history = relationship("GameHistory", back_populates="room", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(String(50), nullable=False)  # UUID from client
    nickname = Column(String(50), nullable=False)
    is_host = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="players")


class GameHistory(Base):
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    drawn_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="history")
    question = relationship("Question")
