// Tic-Tac-Toe Game Logic

export type Player = 'X' | 'O';
export type CellValue = Player | null;
export type Board = CellValue[];

export interface GameState {
  board: Board;
  currentPlayer: Player;
  winner: Player | null;
  isDraw: boolean;
  isGameOver: boolean;
  moveCount: number;
}

export interface GameStats {
  xWins: number;
  oWins: number;
  draws: number;
  totalGames: number;
}

export class TicTacToeLogic {
  // Initialize a new game state
  static createInitialState(): GameState {
    return {
      board: Array(9).fill(null),
      currentPlayer: 'X',
      winner: null,
      isDraw: false,
      isGameOver: false,
      moveCount: 0,
    };
  }

  // Check if a position is valid for a move
  static isValidMove(board: Board, position: number): boolean {
    return position >= 0 && position < 9 && board[position] === null;
  }

  // Make a move and return new game state
  static makeMove(gameState: GameState, position: number): GameState {
    if (!this.isValidMove(gameState.board, position) || gameState.isGameOver) {
      return gameState; // Invalid move, return current state
    }

    const newBoard = [...gameState.board];
    newBoard[position] = gameState.currentPlayer;

    const newMoveCount = gameState.moveCount + 1;
    const winner = this.checkWinner(newBoard);
    const isDraw = !winner && newMoveCount === 9;
    const isGameOver = winner !== null || isDraw;

    return {
      board: newBoard,
      currentPlayer: gameState.currentPlayer === 'X' ? 'O' : 'X',
      winner,
      isDraw,
      isGameOver,
      moveCount: newMoveCount,
    };
  }

  // Check for a winner
  static checkWinner(board: Board): Player | null {
    const winPatterns = [
      [0, 1, 2], // Top row
      [3, 4, 5], // Middle row
      [6, 7, 8], // Bottom row
      [0, 3, 6], // Left column
      [1, 4, 7], // Middle column
      [2, 5, 8], // Right column
      [0, 4, 8], // Diagonal top-left to bottom-right
      [2, 4, 6], // Diagonal top-right to bottom-left
    ];

    for (const pattern of winPatterns) {
      const [a, b, c] = pattern;
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }

    return null;
  }

  // Get winning pattern positions (for highlighting)
  static getWinningPattern(board: Board): number[] {
    const winPatterns = [
      [0, 1, 2], // Top row
      [3, 4, 5], // Middle row
      [6, 7, 8], // Bottom row
      [0, 3, 6], // Left column
      [1, 4, 7], // Middle column
      [2, 5, 8], // Right column
      [0, 4, 8], // Diagonal top-left to bottom-right
      [2, 4, 6], // Diagonal top-right to bottom-left
    ];

    for (const pattern of winPatterns) {
      const [a, b, c] = pattern;
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return pattern;
      }
    }

    return [];
  }

  // Get game result message
  static getGameResultMessage(gameState: GameState): string {
    if (gameState.winner) {
      return `Player ${gameState.winner} wins! 🎉`;
    }
    if (gameState.isDraw) {
      return "It's a draw! 🤝";
    }
    return `Player ${gameState.currentPlayer}'s turn`;
  }

  // Update game statistics
  static updateStats(prevStats: GameStats, gameState: GameState): GameStats {
    if (!gameState.isGameOver) {
      return prevStats;
    }

    const newStats = { ...prevStats };
    newStats.totalGames += 1;

    if (gameState.winner === 'X') {
      newStats.xWins += 1;
    } else if (gameState.winner === 'O') {
      newStats.oWins += 1;
    } else if (gameState.isDraw) {
      newStats.draws += 1;
    }

    return newStats;
  }

  // Create initial stats
  static createInitialStats(): GameStats {
    return {
      xWins: 0,
      oWins: 0,
      draws: 0,
      totalGames: 0,
    };
  }
}
