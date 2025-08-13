export interface ChessMove {
  from: string;
  to: string;
  piece: string;
  player: string;
  timestamp: string;
}

export interface GameState {
  gameId: string;
  board: Record<string, string>;
  currentPlayer: 'white' | 'black';
  moveHistory: ChessMove[];
  gameOver: boolean;
  winner: string | null;
  moveCount: number;
}

export class ChessLogic {
  static isValidSquare(square: string): boolean {
    return square.length === 2 &&
           'abcdefgh'.includes(square[0]) &&
           '12345678'.includes(square[1]);
  }

  static isWhitePiece(piece: string): boolean {
    return '♔♕♖♗♘♙'.includes(piece);
  }

  static isBlackPiece(piece: string): boolean {
    return '♚♛♜♝♞♟'.includes(piece);
  }

  static getPieceColor(piece: string): 'white' | 'black' | null {
    if (this.isWhitePiece(piece)) return 'white';
    if (this.isBlackPiece(piece)) return 'black';
    return null;
  }

  static getPieceType(piece: string): string {
    const pieceMap: Record<string, string> = {
      '♔': 'king', '♚': 'king',
      '♕': 'queen', '♛': 'queen',
      '♖': 'rook', '♜': 'rook',
      '♗': 'bishop', '♝': 'bishop',
      '♘': 'knight', '♞': 'knight',
      '♙': 'pawn', '♟': 'pawn'
    };
    return pieceMap[piece] || 'unknown';
  }

  static getSquareCoordinates(square: string): { file: number; rank: number } {
    return {
      file: square.charCodeAt(0) - 'a'.charCodeAt(0),
      rank: parseInt(square[1]) - 1
    };
  }

  static isValidMove(board: Record<string, string>, from: string, to: string, currentPlayer: 'white' | 'black'): boolean {
    // Basic validation
    if (!this.isValidSquare(from) || !this.isValidSquare(to)) {
      return false;
    }

    const piece = board[from];
    if (!piece) {
      return false;
    }

    const pieceColor = this.getPieceColor(piece);
    if (pieceColor !== currentPlayer) {
      return false;
    }

    // Can't capture your own piece
    const targetPiece = board[to];
    if (targetPiece && this.getPieceColor(targetPiece) === currentPlayer) {
      return false;
    }

    // Basic piece movement validation
    return this.isValidPieceMove(board, from, to, piece);
  }

  private static isValidPieceMove(board: Record<string, string>, from: string, to: string, piece: string): boolean {
    const fromCoords = this.getSquareCoordinates(from);
    const toCoords = this.getSquareCoordinates(to);
    const pieceType = this.getPieceType(piece);
    const isWhite = this.isWhitePiece(piece);

    switch (pieceType) {
      case 'pawn':
        return this.isValidPawnMove(board, fromCoords, toCoords, isWhite);
      case 'rook':
        return this.isValidRookMove(board, fromCoords, toCoords);
      case 'bishop':
        return this.isValidBishopMove(board, fromCoords, toCoords);
      case 'queen':
        return this.isValidQueenMove(board, fromCoords, toCoords);
      case 'king':
        return this.isValidKingMove(fromCoords, toCoords);
      case 'knight':
        return this.isValidKnightMove(fromCoords, toCoords);
      default:
        return false;
    }
  }

  private static isValidPawnMove(board: Record<string, string>, from: { file: number; rank: number }, to: { file: number; rank: number }, isWhite: boolean): boolean {
    const direction = isWhite ? 1 : -1;
    const startRank = isWhite ? 1 : 6;
    const fileDiff = Math.abs(to.file - from.file);
    const rankDiff = to.rank - from.rank;

    // Moving forward
    if (fileDiff === 0) {
      if (rankDiff === direction) {
        // One square forward
        const targetSquare = String.fromCharCode('a'.charCodeAt(0) + to.file) + (to.rank + 1);
        return !board[targetSquare]; // Must be empty
      } else if (rankDiff === 2 * direction && from.rank === startRank) {
        // Two squares forward from starting position
        const oneSquareForward = String.fromCharCode('a'.charCodeAt(0) + to.file) + (from.rank + direction + 1);
        const twoSquaresForward = String.fromCharCode('a'.charCodeAt(0) + to.file) + (to.rank + 1);
        return !board[oneSquareForward] && !board[twoSquaresForward];
      }
    }
    // Diagonal capture
    else if (fileDiff === 1 && rankDiff === direction) {
      const targetSquare = String.fromCharCode('a'.charCodeAt(0) + to.file) + (to.rank + 1);
      const targetPiece = board[targetSquare];
      return !!targetPiece && this.getPieceColor(targetPiece) !== (isWhite ? 'white' : 'black');
    }

    return false;
  }

  private static isValidRookMove(board: Record<string, string>, from: { file: number; rank: number }, to: { file: number; rank: number }): boolean {
    // Rook moves horizontally or vertically
    if (from.file !== to.file && from.rank !== to.rank) {
      return false;
    }

    // Check if path is clear
    return this.isPathClear(board, from, to);
  }

  private static isValidBishopMove(board: Record<string, string>, from: { file: number; rank: number }, to: { file: number; rank: number }): boolean {
    // Bishop moves diagonally
    const fileDiff = Math.abs(to.file - from.file);
    const rankDiff = Math.abs(to.rank - from.rank);

    if (fileDiff !== rankDiff) {
      return false;
    }

    // Check if path is clear
    return this.isPathClear(board, from, to);
  }

  private static isValidQueenMove(board: Record<string, string>, from: { file: number; rank: number }, to: { file: number; rank: number }): boolean {
    // Queen combines rook and bishop moves
    return this.isValidRookMove(board, from, to) || this.isValidBishopMove(board, from, to);
  }

  private static isValidKingMove(from: { file: number; rank: number }, to: { file: number; rank: number }): boolean {
    // King moves one square in any direction
    const fileDiff = Math.abs(to.file - from.file);
    const rankDiff = Math.abs(to.rank - from.rank);
    return fileDiff <= 1 && rankDiff <= 1 && (fileDiff > 0 || rankDiff > 0);
  }

  private static isValidKnightMove(from: { file: number; rank: number }, to: { file: number; rank: number }): boolean {
    // Knight moves in L-shape
    const fileDiff = Math.abs(to.file - from.file);
    const rankDiff = Math.abs(to.rank - from.rank);
    return (fileDiff === 2 && rankDiff === 1) || (fileDiff === 1 && rankDiff === 2);
  }

  private static isPathClear(board: Record<string, string>, from: { file: number; rank: number }, to: { file: number; rank: number }): boolean {
    const fileStep = to.file > from.file ? 1 : to.file < from.file ? -1 : 0;
    const rankStep = to.rank > from.rank ? 1 : to.rank < from.rank ? -1 : 0;

    let currentFile = from.file + fileStep;
    let currentRank = from.rank + rankStep;

    while (currentFile !== to.file || currentRank !== to.rank) {
      const square = String.fromCharCode('a'.charCodeAt(0) + currentFile) + (currentRank + 1);
      if (board[square]) {
        return false; // Path is blocked
      }
      currentFile += fileStep;
      currentRank += rankStep;
    }

    return true;
  }

  static getValidMoves(board: Record<string, string>, square: string, currentPlayer: 'white' | 'black'): string[] {
    const validMoves: string[] = [];

    for (let file = 0; file < 8; file++) {
      for (let rank = 0; rank < 8; rank++) {
        const targetSquare = String.fromCharCode('a'.charCodeAt(0) + file) + (rank + 1);
        if (this.isValidMove(board, square, targetSquare, currentPlayer)) {
          validMoves.push(targetSquare);
        }
      }
    }

    return validMoves;
  }
}
