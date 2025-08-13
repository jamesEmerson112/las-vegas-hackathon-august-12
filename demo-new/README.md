# TicTacToe vs AI - MVP

A unified TicTacToe game with AI opponent using Ollama/Strategic AI fallback.

## Project Structure

```
demo-new/
├── backend/           # Node.js API server + Python AI
│   ├── server.js      # Express server with TicTacToe endpoints
│   ├── tictactoe_ai_api.py  # Python AI using Ollama (with fallback)
│   ├── requirements.txt     # Python dependencies
│   └── package.json         # Node.js dependencies
├── src/              # React frontend
│   └── tictactoe/    # TicTacToe React components
└── package.json      # Frontend dependencies
```

## Features

- **Human vs AI TicTacToe** - Play against an intelligent AI opponent
- **Ollama Integration** - Uses llama3.2 model for AI moves (when available)
- **Strategic Fallback** - Built-in strategic AI when Ollama is unavailable
- **React Frontend** - Modern UI with Tailwind CSS
- **Express API** - RESTful backend API

## Setup & Installation

### 1. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
cd backend
npm install
pip install -r requirements.txt
```

### 2. Start the Services

**Terminal 1 - Backend API:**
```bash
cd backend
npm start
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)
The backend API will be available at `http://localhost:3002`

## API Endpoints

- `POST /api/tictactoe/new` - Create new game
- `POST /api/tictactoe/:gameId/move` - Make player move
- `POST /api/tictactoe/:gameId/ai-move` - Get AI move
- `GET /api/health` - Health check

## AI Features

### Ollama Integration (Optional)
- Install and run Ollama locally
- Pull the llama3.2 model: `ollama pull llama3.2`
- The AI will use Ollama for intelligent moves

### Strategic Fallback
- When Ollama is unavailable, uses built-in strategic AI
- Implements classic TicTacToe strategy:
  1. Try to win
  2. Block opponent wins
  3. Take center
  4. Take corners
  5. Take edges

## Development

### Frontend Development
```bash
npm run dev
```

### Backend Development
```bash
cd backend
npm run dev  # Uses nodemon for auto-restart
```

## Troubleshooting

**AI moves failing?**
- Check if Ollama is running: `ollama serve`
- Pull the model: `ollama pull llama3.2`
- Strategic fallback should work regardless

**CORS issues?**
- Backend includes CORS middleware for all origins

**Port conflicts?**
- Backend uses port 3002
- Frontend uses Vite's default port (usually 5173)
