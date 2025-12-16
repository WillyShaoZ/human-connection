# Card Game - "We Are Not Really Strangers" Style

A real-time multiplayer card game where players draw question cards to get to know each other better. Built with UniApp (Vue 3) and FastAPI.

## Features

- **Real-time multiplayer** - Join rooms with 6-digit codes and play together
- **Anonymous play** - No login required, just enter a nickname
- **Draw & switch cards** - Reveal questions and switch if you want a different one
- **Custom questions** - Add your own private questions to the pool
- **Colorful & playful UI** - Vibrant gradients and smooth animations

## Tech Stack

- **Frontend**: UniApp (Vue 3 + Pinia)
- **Backend**: FastAPI + WebSocket
- **Database**: PostgreSQL

## Project Structure

```
SocialPlatform/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Settings
│   │   ├── database.py      # DB connection
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   └── services/        # Business logic
│   ├── requirements.txt
│   └── init_db.sql          # Seed questions
│
└── frontend/
    ├── pages/
    │   ├── index/           # Home - Create/Join room
    │   ├── room/            # Game room
    │   └── questions/       # Custom questions
    ├── components/          # Vue components
    ├── stores/              # Pinia store
    └── utils/               # API & WebSocket
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 16+
- PostgreSQL 13+

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create PostgreSQL database:
   ```bash
   createdb card_game
   ```

5. Configure environment (copy .env.example to .env and edit if needed):
   ```bash
   cp .env.example .env
   ```

6. Run the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. Seed initial questions (optional, tables are created automatically):
   ```bash
   psql card_game < init_db.sql
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server (H5/Web):
   ```bash
   npm run dev:h5
   ```

4. Access at `http://localhost:5173`

### Build for Production

```bash
# Web
npm run build:h5

# WeChat Mini Program
npm run build:mp-weixin
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rooms` | Create a new room |
| GET | `/api/rooms/{code}` | Get room info |
| POST | `/api/rooms/{code}/join` | Join a room |
| GET | `/api/questions` | Get system questions |
| POST | `/api/questions` | Add custom question |
| GET | `/api/questions/custom/{room}` | Get custom questions |
| WS | `/ws/{room}/{player}` | WebSocket for game |

## WebSocket Events

**Client → Server:**
- `start_game` - Host starts game
- `draw_card` - Draw a question card
- `switch_card` - Switch current card
- `end_game` - Host ends game
- `restart_game` - Host restarts

**Server → Client:**
- `game_state` - Current game state
- `card_drawn` - New card revealed
- `card_switched` - Card was switched
- `game_started/ended/restarted` - Game status changes
- `player_connected/disconnected` - Player events

## How to Play

1. **Create or Join a Room**
   - Enter your nickname
   - Create a new room or enter a 6-digit code to join

2. **Wait for Players**
   - Share the room code with friends
   - Host can start when ready

3. **Play the Game**
   - Tap "Draw Card" to reveal a question
   - Answer the question honestly
   - Tap "Switch" if you want a different question

4. **Add Custom Questions**
   - Tap "Add Custom Questions" to add your own
   - Custom questions are private to your games

## License

MIT
