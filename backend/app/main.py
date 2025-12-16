from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import rooms, questions, websocket

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Card Game API",
    description="API for 'We Are Not Really Strangers' style card game",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rooms.router)
app.include_router(questions.router)
app.include_router(websocket.router)


@app.get("/")
def root():
    return {"message": "Card Game API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
