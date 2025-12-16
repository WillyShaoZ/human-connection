from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import QuestionCreate, QuestionResponse
from ..services import game_service
from ..models import Question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=List[QuestionResponse])
def get_system_questions(db: Session = Depends(get_db)):
    """Get all system questions."""
    questions = db.query(Question).filter(Question.is_system == True).all()
    return questions


@router.post("", response_model=QuestionResponse)
def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    """Add a custom question for a room."""
    if not question_data.created_by:
        raise HTTPException(status_code=400, detail="Room code required for custom questions")

    question = game_service.add_custom_question(
        db,
        content=question_data.content,
        room_code=question_data.created_by
    )
    return question


@router.get("/room/{room_code}", response_model=List[QuestionResponse])
def get_room_questions(room_code: str, db: Session = Depends(get_db)):
    """Get all questions available for a room (system + custom)."""
    questions = game_service.get_room_questions(db, room_code)
    return questions


@router.get("/custom/{room_code}", response_model=List[QuestionResponse])
def get_custom_questions(room_code: str, db: Session = Depends(get_db)):
    """Get only custom questions for a room."""
    questions = game_service.get_custom_questions(db, room_code)
    return questions


@router.delete("/{question_id}")
def delete_question(question_id: int, room_code: str, db: Session = Depends(get_db)):
    """Delete a custom question."""
    deleted = game_service.delete_custom_question(db, question_id, room_code)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found or cannot be deleted")
    return {"message": "Question deleted"}
