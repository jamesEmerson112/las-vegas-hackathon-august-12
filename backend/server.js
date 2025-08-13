const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const ChessValidator = require('./ChessValidator');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Game state storage (in production, use a database)
let gameStates = new Map();

// Chess game class (simplified for API)
class ChessGame {
  constructor(gameId) {
    this.gameId = gameId;
    this.board = this.initBoard();
    this.currentPlayer = 'white';
    this.moveHistory = [];
    this.gameOver = false;
    this.winner = null;
  }

  initBoard() {
    const board = {};

    // White pieces
    Object.assign(board, {
      'a1': '♖', 'b1': '♘', 'c1': '♗', 'd1': '♕', 'e1': '♔', 'f1': '♗', 'g1': '♘', 'h1': '♖',
      'a2': '♙', 'b2': '♙', 'c2': '♙', 'd2': '♙', 'e2': '♙', 'f2': '♙', 'g2': '♙', 'h2': '♙'
    });

    // Black pieces
    Object.assign(board, {
      'a8': '♜', 'b8': '♞', 'c8': '♝', 'd8': '♛', 'e8': '♚', 'f8': '♝', 'g8': '♞', 'h8': '♜',
      'a7': '♟', 'b7': '♟', 'c7': '♟', 'd7': '♟', 'e7': '♟', 'f7': '♟', 'g7': '♟', 'h7': '♟'
    });

    return board;
  }

  makeMove(fromSquare, toSquare) {
    if (!ChessValidator.isValidSquare(fromSquare) || !ChessValidator.isValidSquare(toSquare)) {
      return false;
    }

    if (!this.board[fromSquare]) {
      return false;
    }

    // Validate the move using proper chess rules
    if (!ChessValidator.isValidMove(this.board, fromSquare, toSquare, this.currentPlayer)) {
      return false;
    }

    const piece = this.board[fromSquare];

    // Move the piece
    this.board[toSquare] = piece;
    delete this.board[fromSquare];

    // Record move
    this.moveHistory.push({
      from: fromSquare,
      to: toSquare,
      piece: piece,
      player: this.currentPlayer,
      timestamp: new Date().toISOString()
    });

    // Switch players
    this.currentPlayer = this.currentPlayer === 'white' ? 'black' : 'white';

    return true;
  }

  isValidSquare(square) {
    return square.length === 2 &&
           'abcdefgh'.includes(square[0]) &&
           '12345678'.includes(square[1]);
  }

  getBoardState() {
    let state = "Current board position:\\n";
    state += "  a b c d e f g h\\n";

    for (let rank = 8; rank >= 1; rank--) {
      state += `${rank} `;
      for (let file of 'abcdefgh') {
        const square = `${file}${rank}`;
        const piece = this.board[square] || '.';
        state += `${piece} `;
      }
      state += ` ${rank}\\n`;
    }

    state += "  a b c d e f g h\\n";
    state += `\\nCurrent turn: ${this.currentPlayer}\\n`;

    if (this.moveHistory.length > 0) {
      const lastMove = this.moveHistory[this.moveHistory.length - 1];
      state += `Last move: ${lastMove.from}-${lastMove.to}\\n`;
    }

    return state;
  }

  getGameState() {
    return {
      gameId: this.gameId,
      board: this.board,
      currentPlayer: this.currentPlayer,
      moveHistory: this.moveHistory,
      gameOver: this.gameOver,
      winner: this.winner,
      moveCount: this.moveHistory.length
    };
  }
}

// Helper function to call Python chess AI
async function getAIMove(game) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, 'chess_ai_api.py');
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

// API Routes

// Create new game
app.post('/api/game/new', (req, res) => {
  const gameId = Date.now().toString();
  const game = new ChessGame(gameId);
  gameStates.set(gameId, game);

  res.json({
    success: true,
    gameId: gameId,
    gameState: game.getGameState()
  });
});

// Get game state
app.get('/api/game/:gameId', (req, res) => {
  const game = gameStates.get(req.params.gameId);

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

// Make player move
app.post('/api/game/:gameId/move', (req, res) => {
  const game = gameStates.get(req.params.gameId);
  const { from, to } = req.body;

  if (!game) {
    return res.status(404).json({
      success: false,
      error: 'Game not found'
    });
  }

  if (game.currentPlayer !== 'white') {
    return res.status(400).json({
      success: false,
      error: 'Not your turn'
    });
  }

  const moveSuccess = game.makeMove(from, to);

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

// Get AI move
app.post('/api/game/:gameId/ai-move', async (req, res) => {
  const game = gameStates.get(req.params.gameId);

  if (!game) {
    return res.status(404).json({
      success: false,
      error: 'Game not found'
    });
  }

  if (game.currentPlayer !== 'black') {
    return res.status(400).json({
      success: false,
      error: 'Not AI turn'
    });
  }

  try {
    const aiResponse = await getAIMove(game);

    if (aiResponse.success && aiResponse.move) {
      const moveSuccess = game.makeMove(aiResponse.move.from, aiResponse.move.to);

      if (moveSuccess) {
        res.json({
          success: true,
          aiMove: aiResponse.move,
          gameState: game.getGameState(),
          aiThinking: aiResponse.thinking,
          opikTrackingUrl: aiResponse.opik_tracking_url || null
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
    console.error('AI Error:', error);
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
    message: 'Chess API server is running',
    activeGames: gameStates.size
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Chess API server running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
});
