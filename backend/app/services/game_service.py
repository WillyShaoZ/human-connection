import random
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models import Room, Question, GameHistory


def get_available_questions(db: Session, room: Room) -> list[Question]:
    """Get all available questions for a room (system + room's custom)."""
    # Get IDs of already drawn questions
    drawn_ids = db.query(GameHistory.question_id).filter(
        GameHistory.room_id == room.id
    ).all()
    drawn_ids = [id[0] for id in drawn_ids]

    # Get available questions (system OR created by this room's host)
    query = db.query(Question).filter(
        or_(
            Question.is_system == True,
            Question.created_by == room.room_code
        )
    )

    if drawn_ids:
        query = query.filter(Question.id.notin_(drawn_ids))

    return query.all()


def draw_card(db: Session, room: Room) -> Question | None:
    """Draw a random card for the room."""
    available = get_available_questions(db, room)

    if not available:
        # Reset history if all cards drawn
        db.query(GameHistory).filter(GameHistory.room_id == room.id).delete()
        db.commit()
        available = get_available_questions(db, room)

    if not available:
        return None

    card = random.choice(available)

    # Record in history
    history = GameHistory(room_id=room.id, question_id=card.id)
    db.add(history)

    # Update room's current card
    room.current_card_id = card.id
    db.commit()
    db.refresh(room)

    return card


def switch_card(db: Session, room: Room) -> Question | None:
    """Switch the current card for a new one."""
    return draw_card(db, room)


def add_custom_question(db: Session, content: str, room_code: str) -> Question:
    """Add a custom question for a room."""
    question = Question(
        content=content,
        is_system=False,
        created_by=room_code
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_room_questions(db: Session, room_code: str) -> list[Question]:
    """Get all questions available for a room."""
    return db.query(Question).filter(
        or_(
            Question.is_system == True,
            Question.created_by == room_code
        )
    ).all()


def get_custom_questions(db: Session, room_code: str) -> list[Question]:
    """Get only custom questions for a room."""
    return db.query(Question).filter(
        Question.created_by == room_code
    ).all()


def delete_custom_question(db: Session, question_id: int, room_code: str) -> bool:
    """Delete a custom question. Returns True if deleted."""
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.created_by == room_code,
        Question.is_system == False
    ).first()

    if question:
        db.delete(question)
        db.commit()
        return True
    return False
