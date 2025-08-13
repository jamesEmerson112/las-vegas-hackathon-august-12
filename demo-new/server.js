import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3002;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from the dist directory in production
const isProduction = process.env.NODE_ENV === 'production';
if (isProduction) {
  app.use(express.static(path.join(__dirname, 'dist')));
}

// Game state storage (in production, use a database)
let ticTacToeStates = new Map();

// TicTacToe game class
class TicTacToeGame {
  constructor(gameId) {
    this.gameId = gameId;
    this.board = Array(9).fill(null); // 9 positions: 0-8
    this.currentPlayer = 'X'; // Human player is X, AI is O
    this.winner = null;
    this.isDraw = false;
    this.isGameOver = false;
    this.moveCount = 0;
  }

  isValidMove(position) {
    return position >= 0 && position < 9 && this.board[position] === null;
  }

  makeMove(position) {
    if (!this.isValidMove(position) || this.isGameOver) {
      return false;
    }

    this.board[position] = this.currentPlayer;
    this.moveCount++;

    // Check for winner
    this.winner = this.checkWinner();
    this.isDraw = !this.winner && this.moveCount === 9;
    this.isGameOver = this.winner !== null || this.isDraw;

    // Switch players
    this.currentPlayer = this.currentPlayer === 'X' ? 'O' : 'X';

    return true;
  }

  checkWinner() {
    const winPatterns = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
      [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
      [0, 4, 8], [2, 4, 6] // diagonals
    ];

    for (const pattern of winPatterns) {
      const [a, b, c] = pattern;
      if (this.board[a] && this.board[a] === this.board[b] && this.board[a] === this.board[c]) {
        return this.board[a];
      }
    }

    return null;
  }

  getGameState() {
    return {
      gameId: this.gameId,
      board: this.board,
      currentPlayer: this.currentPlayer,
      winner: this.winner,
      isDraw: this.isDraw,
      isGameOver: this.isGameOver,
      moveCount: this.moveCount
    };
  }
}

// Helper function to get TicTacToe AI move using Python AI script
async function getTicTacToeAIMove(game) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, 'tictactoe_ai_api.py');
    const gameState = JSON.stringify(game.getGameState());

    const pythonProcess = spawn('python', [pythonScript], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    pythonProcess.stdin.write(gameState);
    pythonProcess.stdin.end();

    let output = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code === 0 && output.trim()) {
        try {
          const result = JSON.parse(output.trim());
          resolve(result);
        } catch (e) {
          reject(new Error('Failed to parse AI response'));
        }
      } else {
        reject(new Error(error || 'AI process failed'));
      }
    });
  });
}

// TicTacToe API Routes

// Create new TicTacToe game
app.post('/api/tictactoe/new', (req, res) => {
  const gameId = Date.now().toString();
  const game = new TicTacToeGame(gameId);
  ticTacToeStates.set(gameId, game);

  res.json({
    success: true,
    gameId: gameId,
    gameState: game.getGameState()
  });
});

// Get TicTacToe game state
app.get('/api/tictactoe/:gameId', (req, res) => {
  const game = ticTacToeStates.get(req.params.gameId);

  if (!game) {
    return res.status(404).json({
      success: false,
      error: 'Game not found'
    });
  }

  res.json({
    success: true,
    gameState: game.getGameState()
  });
});

// Make player move in TicTacToe
app.post('/api/tictactoe/:gameId/move', (req, res) => {
  const game = ticTacToeStates.get(req.params.gameId);
  const { position } = req.body;

  if (!game) {
    return res.status(404).json({
      success: false,
      error: 'Game not found'
    });
  }

  if (game.currentPlayer !== 'X') {
    return res.status(400).json({
      success: false,
      error: 'Not your turn'
    });
  }

  if (game.isGameOver) {
    return res.status(400).json({
      success: false,
      error: 'Game is already over'
    });
  }

  const moveSuccess = game.makeMove(position);

  if (!moveSuccess) {
    return res.status(400).json({
      success: false,
      error: 'Invalid move'
    });
  }

  res.json({
    success: true,
    gameState: game.getGameState()
  });
});

// Get TicTacToe AI move
app.post('/api/tictactoe/:gameId/ai-move', async (req, res) => {
  const game = ticTacToeStates.get(req.params.gameId);

  if (!game) {
    return res.status(404).json({
      success: false,
      error: 'Game not found'
    });
  }

  if (game.currentPlayer !== 'O') {
    return res.status(400).json({
      success: false,
      error: 'Not AI turn'
    });
  }

  if (game.isGameOver) {
    return res.status(400).json({
      success: false,
      error: 'Game is already over'
    });
  }

  try {
    const aiResponse = await getTicTacToeAIMove(game);

    if (aiResponse.success && typeof aiResponse.move === 'number') {
      const moveSuccess = game.makeMove(aiResponse.move);

      if (moveSuccess) {
        res.json({
          success: true,
          aiMove: aiResponse.move,
          gameState: game.getGameState(),
          aiThinking: aiResponse.thinking || 'AI made a move'
        });
      } else {
        res.status(500).json({
          success: false,
          error: 'AI made invalid move'
        });
      }
    } else {
      res.status(500).json({
        success: false,
        error: 'AI failed to generate move'
      });
    }
  } catch (error) {
    console.error('TicTacToe AI Error:', error);
    res.status(500).json({
      success: false,
      error: 'AI service unavailable'
    });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'TicTacToe AI API server is running',
    activeTicTacToeGames: ticTacToeStates.size
  });
});

// Serve frontend in production
if (isProduction) {
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`🚀 TicTacToe AI API server running on http://localhost:${PORT}`);
  console.log(`⭕ TicTacToe endpoints: /api/tictactoe/*`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  console.log(`🤖 AI service: Python + Ollama (with strategic fallback)`);
  if (!isProduction) {
    console.log(`🎨 Frontend: Run 'npm run dev' to start both frontend and backend`);
  } else {
    console.log(`🎨 Frontend: Serving from built files`);
  }
});
