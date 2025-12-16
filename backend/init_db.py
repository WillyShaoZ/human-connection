"""Initialize database tables and seed data."""
from app.database import engine, Base
from app.models import Question, Room, Player, GameHistory
from sqlalchemy.orm import Session

def init_tables():
    """Create all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def seed_questions():
    """Seed initial system questions."""
    from app.database import SessionLocal

    db = SessionLocal()

    # Check if questions already exist
    existing = db.query(Question).filter(Question.is_system == True).count()
    if existing > 0:
        print(f"Questions already exist ({existing} found). Skipping seed.")
        db.close()
        return

    questions = [
        # Deep/Meaningful questions
        "What's something you wish more people knew about you?",
        "What's a fear you've never told anyone?",
        "What's the nicest thing someone has done for you?",
        "What's something you're proud of but rarely talk about?",
        "What do you wish you could tell your younger self?",
        "What's a dream you've given up on?",
        "What's something you need to forgive yourself for?",
        "What's the hardest thing you've ever had to do?",
        "What makes you feel most alive?",
        "What's a belief you held strongly that you've changed your mind about?",
        "What do you need more of in your life right now?",
        "What's something you're currently struggling with?",
        "If you could change one decision from your past, what would it be?",
        "What's the best advice you've ever received?",
        "What does love mean to you?",
        # Fun/Casual questions
        "What's the most embarrassing song on your playlist?",
        "If you could have any superpower for a day, what would it be?",
        "What's your guilty pleasure TV show?",
        "What's the weirdest food combination you enjoy?",
        "If you won the lottery tomorrow, what's the first thing you'd buy?",
        "What's your go-to karaoke song?",
        "If you could live in any fictional world, which would it be?",
        "What's the most useless talent you have?",
        "What's your most unpopular opinion?",
        "If you could only eat one food for the rest of your life, what would it be?",
        "What's the craziest thing on your bucket list?",
        "If you were a superhero, what would your weakness be?",
        "What's the worst fashion choice you've ever made?",
        "What's your most irrational fear?",
        "If you could instantly become an expert in something, what would it be?",
        # Connection questions
        "What's something you've always wanted to ask me?",
        "What was your first impression of me?",
        "What do you think we have in common?",
        "What's something you admire about the person to your left?",
        "Describe me in three words.",
        "What's something you think I'm really good at?",
        "What's a memory you have of us that makes you smile?",
        "What do you think is my biggest strength?",
        "If we could go on any adventure together, what would it be?",
        "What's something you've learned from me?",
        "What's one thing you wish we did more together?",
        "What do you value most about our friendship?",
        "If you had to describe our relationship to a stranger, what would you say?",
        "What's something you think I should know about you?",
        "What's a compliment you've been meaning to give me?",
    ]

    print(f"Seeding {len(questions)} questions...")
    for content in questions:
        question = Question(content=content, is_system=True, created_by=None)
        db.add(question)

    db.commit()
    db.close()
    print("Questions seeded successfully!")

if __name__ == "__main__":
    init_tables()
    seed_questions()
