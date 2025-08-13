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
let ticTacToeStates = new Map();

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
    message: 'Game API server is running',
    activeChessGames: gameStates.size,
    activeTicTacToeGames: ticTacToeStates.size
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Game API server running on http://localhost:${PORT}`);
  console.log(`♔ Chess endpoints: /api/game/*`);
  console.log(`⭕ TicTacToe endpoints: /api/tictactoe/*`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
});
