import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { RotateCcw, Crown, Grid3X3, Crown as ChessIcon } from 'lucide-react';
import './App.css';
import { ChessLogic, ChessMove, GameState } from './chess/ChessLogic';
import { ChessBoard } from './chess/ChessComponents';
import { TicTacToeGame } from './tictactoe/TicTacToeComponents';
import { TicTacToeLogic, GameState as TicTacToeGameState, GameStats as TicTacToeGameStats } from './tictactoe/TicTacToeLogic';

const API_BASE = 'http://localhost:3002/api';

const App: React.FC = () => {
  // Navigation state
  const [activeGame, setActiveGame] = useState<'chess' | 'tictactoe'>('chess');

  // Chess game state
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [validMoves, setValidMoves] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [aiThinking, setAiThinking] = useState(false);
  const [status, setStatus] = useState('Click "New Game" to start');
  const [error, setError] = useState<string | null>(null);
  const [opikTrackingUrl, setOpikTrackingUrl] = useState<string | null>(null);

  // Tic-tac-toe game state
  const [ticTacToeGameState, setTicTacToeGameState] = useState<TicTacToeGameState>(
    TicTacToeLogic.createInitialState()
  );
  const [ticTacToeStats, setTicTacToeStats] = useState<TicTacToeGameStats>(
    TicTacToeLogic.createInitialStats()
  );
  const [ticTacToeGameId, setTicTacToeGameId] = useState<string | null>(null);
  const [ticTacToeAiThinking, setTicTacToeAiThinking] = useState(false);
  const [ticTacToeError, setTicTacToeError] = useState<string | null>(null);

  // Create new game
  const createNewGame = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setOpikTrackingUrl(null); // Reset Opik URL for new game
      setSelectedSquare(null);
      setValidMoves([]);
      const response = await axios.post(`${API_BASE}/game/new`);
      setGameState(response.data.gameState);
      setStatus('Your turn! You are playing as WHITE pieces.');
    } catch (err) {
      setError('Failed to create game. Make sure the backend server is running.');
      console.error('Game creation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle square click
  const handleSquareClick = async (square: string) => {
    if (!gameState || gameState.gameOver || aiThinking) return;

    if (gameState.currentPlayer !== 'white') {
      setStatus('Wait for AI to make a move...');
      return;
    }

    if (!selectedSquare) {
      // Select a square if it has a white piece
      const piece = gameState.board[square];
      if (piece && ChessLogic.isWhitePiece(piece)) {
        setSelectedSquare(square);
        const possibleMoves = ChessLogic.getValidMoves(gameState.board, square, 'white');
        setValidMoves(possibleMoves);
        setStatus(`Selected ${square}. Choose a destination square.`);
      } else {
        setStatus('Select one of your white pieces first.');
      }
    } else {
      // Make a move
      if (selectedSquare === square) {
        // Deselect
        setSelectedSquare(null);
        setValidMoves([]);
        setStatus('Selection cleared. Choose a piece to move.');
      } else {
        // Attempt move
        await makePlayerMove(selectedSquare, square);
      }
    }
  };

  // Make player move
  const makePlayerMove = async (from: string, to: string) => {
    if (!gameState) return;

    // Validate move client-side first
    if (!ChessLogic.isValidMove(gameState.board, from, to, 'white')) {
      setError('Invalid move! Please try a different move.');
      setSelectedSquare(null);
      setValidMoves([]);
      setStatus('Invalid move. Select a piece to move.');
      return;
    }

    try {
      setIsLoading(true);
      setStatus('Making your move...');

      const response = await axios.post(`${API_BASE}/game/${gameState.gameId}/move`, {
        from,
        to
      });

      if (response.data.success) {
        setGameState(response.data.gameState);
        setSelectedSquare(null);
        setValidMoves([]);
        setStatus('Move made! AI is thinking...');

        // Trigger AI move after a short delay
        setTimeout(() => {
          makeAIMove(response.data.gameState.gameId);
        }, 500);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Invalid move';
      setError(errorMsg);
      setSelectedSquare(null);
      setValidMoves([]);
      setStatus('Try a different move.');
    } finally {
      setIsLoading(false);
    }
  };

  // Make AI move
  const makeAIMove = async (gameId: string) => {
    try {
      setAiThinking(true);
      setStatus('🤖 AI is thinking... (tracked in Opik)');

      const response = await axios.post(`${API_BASE}/game/${gameId}/ai-move`);

      if (response.data.success) {
        setGameState(response.data.gameState);
        const aiMove = response.data.aiMove;
        setStatus(`AI moved: ${aiMove.from} → ${aiMove.to}. Your turn!`);

        // Update Opik tracking URL if provided
        if (response.data.opikTrackingUrl) {
          setOpikTrackingUrl(response.data.opikTrackingUrl);
        }
      } else {
        setError('AI failed to make a move');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'AI service error';
      setError(errorMsg);
      setStatus('AI encountered an error. Your turn!');
    } finally {
      setAiThinking(false);
    }
  };

  // Create new TicTacToe game
  const createNewTicTacToeGame = async () => {
    try {
      setTicTacToeError(null);
      const response = await axios.post(`${API_BASE}/tictactoe/new`);

      if (response.data.success) {
        const backendState = response.data.gameState;
        // Convert backend state to frontend state format
        const frontendState: TicTacToeGameState = {
          board: backendState.board,
          currentPlayer: backendState.currentPlayer,
          winner: backendState.winner,
          isDraw: backendState.isDraw,
          isGameOver: backendState.isGameOver,
          moveCount: backendState.moveCount
        };

        setTicTacToeGameState(frontendState);
        setTicTacToeGameId(response.data.gameId);
      }
    } catch (err) {
      setTicTacToeError('Failed to create game. Make sure the backend server is running.');
      console.error('TicTacToe game creation error:', err);
    }
  };

  // Handle TicTacToe move with backend integration
  const handleTicTacToeMove = async (position: number) => {
    if (!ticTacToeGameId || ticTacToeGameState.isGameOver || ticTacToeAiThinking) {
      return;
    }

    // Only allow moves when it's the human player's turn (X)
    if (ticTacToeGameState.currentPlayer !== 'X') {
      return;
    }

    try {
      setTicTacToeError(null);

      // Make player move
      const playerMoveResponse = await axios.post(`${API_BASE}/tictactoe/${ticTacToeGameId}/move`, {
        position
      });

      if (playerMoveResponse.data.success) {
        const backendState = playerMoveResponse.data.gameState;
        const frontendState: TicTacToeGameState = {
          board: backendState.board,
          currentPlayer: backendState.currentPlayer,
          winner: backendState.winner,
          isDraw: backendState.isDraw,
          isGameOver: backendState.isGameOver,
          moveCount: backendState.moveCount
        };

        setTicTacToeGameState(frontendState);

        // Update stats if game is over
        if (frontendState.isGameOver) {
          setTicTacToeStats(prevStats =>
            TicTacToeLogic.updateStats(prevStats, frontendState)
          );
        } else if (frontendState.currentPlayer === 'O') {
          // If game is not over and it's AI's turn, get AI move
          setTimeout(() => {
            makeTicTacToeAIMove();
          }, 500);
        }
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Failed to make move';
      setTicTacToeError(errorMsg);
      console.error('TicTacToe move error:', err);
    }
  };

  // Make AI move for TicTacToe
  const makeTicTacToeAIMove = async () => {
    if (!ticTacToeGameId) return;

    try {
      setTicTacToeAiThinking(true);
      setTicTacToeError(null);

      const aiMoveResponse = await axios.post(`${API_BASE}/tictactoe/${ticTacToeGameId}/ai-move`);

      if (aiMoveResponse.data.success) {
        const backendState = aiMoveResponse.data.gameState;
        const frontendState: TicTacToeGameState = {
          board: backendState.board,
          currentPlayer: backendState.currentPlayer,
          winner: backendState.winner,
          isDraw: backendState.isDraw,
          isGameOver: backendState.isGameOver,
          moveCount: backendState.moveCount
        };

        setTicTacToeGameState(frontendState);

        // Update stats if game is over
        if (frontendState.isGameOver) {
          setTicTacToeStats(prevStats =>
            TicTacToeLogic.updateStats(prevStats, frontendState)
          );
        }
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'AI service error';
      setTicTacToeError(errorMsg);
      console.error('TicTacToe AI move error:', err);
    } finally {
      setTicTacToeAiThinking(false);
    }
  };

  const handleNewTicTacToeGame = () => {
    createNewTicTacToeGame();
  };

  const handleResetTicTacToeStats = () => {
    setTicTacToeStats(TicTacToeLogic.createInitialStats());
  };

  // Clear error after a few seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Clear TicTacToe error after a few seconds
  useEffect(() => {
    if (ticTacToeError) {
      const timer = setTimeout(() => setTicTacToeError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [ticTacToeError]);

  const lastMove: ChessMove | null = gameState?.moveHistory[gameState.moveHistory.length - 1] || null;

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Game Hub
          </h1>
          <p className="text-gray-600">Choose your game and start playing!</p>
        </div>

        {/* Game Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-lg p-2 border border-gray-200">
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveGame('chess')}
                className={`
                  flex items-center gap-2 px-6 py-3 rounded-md font-semibold transition-all
                  ${activeGame === 'chess'
                    ? 'bg-gray-900 text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                <ChessIcon className="w-5 h-5" />
                Chess vs AI
              </button>
              <button
                onClick={() => setActiveGame('tictactoe')}
                className={`
                  flex items-center gap-2 px-6 py-3 rounded-md font-semibold transition-all
                  ${activeGame === 'tictactoe'
                    ? 'bg-gray-900 text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                <Grid3X3 className="w-5 h-5" />
                TicTacToe vs AI
              </button>
            </div>
          </div>
        </div>

        {/* Chess Game */}
        {activeGame === 'chess' && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Chess Game Controls */}
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                  <h2 className="text-lg font-semibold mb-4 text-gray-900">
                    Chess Controls
                  </h2>

                  <button
                    onClick={createNewGame}
                    disabled={isLoading}
                    className="w-full bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400
                              text-white font-semibold py-3 px-4 rounded-lg transition-colors
                              flex items-center justify-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    {gameState ? 'New Game' : 'Start Game'}
                  </button>

                  {/* Status */}
                  <div className="mt-4 p-3 bg-gray-100 rounded-lg border">
                    <p className="text-sm font-medium text-center text-gray-700">
                      {aiThinking ? (
                        <span className="flex items-center justify-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-600 border-t-transparent"></div>
                          AI Thinking...
                        </span>
                      ) : (
                        status
                      )}
                    </p>
                  </div>

                  {/* Error Display */}
                  {error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-red-700 text-sm text-center">{error}</p>
                    </div>
                  )}

                  {/* Opik Tracking URL */}
                  {opikTrackingUrl && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm font-medium text-blue-900 mb-2">🔍 Opik Tracking:</p>
                      <a
                        href={opikTrackingUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline text-xs break-all"
                      >
                        View AI decision process →
                      </a>
                    </div>
                  )}
                </div>

                {/* Game Info */}
                {gameState && (
                  <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">Game Info</h3>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current Turn:</span>
                        <span className={`font-medium ${gameState.currentPlayer === 'white' ? 'text-gray-900' : 'text-gray-600'}`}>
                          {gameState.currentPlayer === 'white' ? 'You (White)' : 'AI (Black)'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Moves:</span>
                        <span className="font-medium text-gray-900">{gameState.moveCount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Game ID:</span>
                        <span className="font-mono text-xs text-gray-500">{gameState.gameId}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Chess Board */}
              <div className="lg:col-span-2 flex justify-center">
                {gameState ? (
                  <ChessBoard
                    board={gameState.board}
                    selectedSquare={selectedSquare}
                    onSquareClick={handleSquareClick}
                    lastMove={lastMove}
                    validMoves={validMoves}
                  />
                ) : (
                  <div className="w-96 h-96 bg-white rounded-lg shadow-lg flex items-center justify-center border border-gray-200">
                    <div className="text-center text-gray-600">
                      <Crown className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                      <p className="text-lg font-medium">Start a new game to begin playing</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Move History */}
            {gameState && gameState.moveHistory.length > 0 && (
              <div className="mt-8 bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Move History</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-32 overflow-y-auto">
                  {gameState.moveHistory.map((move, index) => (
                    <div key={index} className="bg-gray-100 rounded px-2 py-1 border border-gray-200">
                      <div className="font-mono text-sm text-center text-gray-900">
                        {move.from}→{move.to}
                      </div>
                      <div className="text-xs text-center text-gray-600">
                        {move.player === 'white' ? '♔' : '♚'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Tic-Tac-Toe Game */}
        {activeGame === 'tictactoe' && (
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

              {/* Game Controls */}
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                  <h2 className="text-lg font-semibold mb-4 text-gray-900">
                    TicTacToe Controls
                  </h2>

                  <div className="space-y-3">
                    <button
                      onClick={handleNewTicTacToeGame}
                      className="w-full bg-gray-900 hover:bg-gray-800 text-white
                               font-semibold py-3 px-4 rounded-lg transition-colors
                               flex items-center justify-center gap-2"
                    >
                      🎮 New Game vs AI
                    </button>

                    <button
                      onClick={handleResetTicTacToeStats}
                      className="w-full bg-red-600 hover:bg-red-700 text-white
                               font-semibold py-2 px-4 rounded-lg transition-colors
                               flex items-center justify-center gap-2 text-sm"
                    >
                      🔄 Reset Stats
                    </button>
                  </div>

                  {/* AI Thinking Status */}
                  {ticTacToeAiThinking && (
                    <div className="mt-4 p-3 bg-blue-100 rounded-lg border border-blue-200">
                      <p className="text-sm font-medium text-center text-blue-700 flex items-center justify-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                        🤖 AI is thinking...
                      </p>
                    </div>
                  )}

                  {/* Error Display */}
                  {ticTacToeError && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-red-700 text-sm text-center">{ticTacToeError}</p>
                    </div>
                  )}

                  {/* Game Info */}
                  {ticTacToeGameId && (
                    <div className="mt-4 p-3 bg-gray-100 rounded-lg border">
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">You play:</span>
                          <span className="font-medium text-blue-600">X</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">AI plays:</span>
                          <span className="font-medium text-red-600">O</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Current turn:</span>
                          <span className={`font-medium ${ticTacToeGameState.currentPlayer === 'X' ? 'text-blue-600' : 'text-red-600'}`}>
                            {ticTacToeGameState.currentPlayer === 'X' ? 'Your turn' : 'AI turn'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Game ID:</span>
                          <span className="font-mono text-xs text-gray-500">{ticTacToeGameId}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Game Statistics */}
                <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4 text-gray-900">Game Statistics</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-blue-600 font-medium">X Wins (You):</span>
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-bold">
                        {ticTacToeStats.xWins}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-red-600 font-medium">O Wins (AI):</span>
                      <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-bold">
                        {ticTacToeStats.oWins}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-yellow-600 font-medium">Draws:</span>
                      <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-bold">
                        {ticTacToeStats.draws}
                      </span>
                    </div>
                    <div className="border-t pt-3 flex justify-between items-center">
                      <span className="text-gray-600 font-medium">Total Games:</span>
                      <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-bold">
                        {ticTacToeStats.totalGames}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Game Board */}
              <div className="lg:col-span-2 space-y-6">
                {/* Game Status */}
                <div className={`
                  p-4 rounded-lg text-center font-medium
                  ${ticTacToeGameState.isGameOver
                    ? ticTacToeGameState.winner
                      ? 'bg-green-50 border border-green-200 text-green-800'
                      : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                    : 'bg-blue-50 border border-blue-200 text-blue-800'
                  }
                `}>
                  <p className="text-lg">
                    {ticTacToeGameState.isGameOver
                      ? ticTacToeGameState.winner
                        ? `${ticTacToeGameState.winner === 'X' ? 'You' : 'AI'} win! 🎉`
                        : "It's a draw! 🤝"
                      : ticTacToeAiThinking
                        ? '🤖 AI is thinking...'
                        : ticTacToeGameState.currentPlayer === 'X'
                          ? 'Your turn - click a square!'
                          : 'AI is making a move...'
                    }
                  </p>
                </div>

                {/* Board */}
                <div className="flex justify-center">
                  {ticTacToeGameId ? (
                    <div className="inline-block bg-white p-6 rounded-lg shadow-lg border border-gray-200">
                      <div className="grid grid-cols-3 gap-2">
                        {ticTacToeGameState.board.map((cell, index) => (
                          <button
                            key={index}
                            onClick={() => handleTicTacToeMove(index)}
                            disabled={ticTacToeGameState.isGameOver || cell !== null || ticTacToeAiThinking || ticTacToeGameState.currentPlayer !== 'X'}
                            className={`
                              w-20 h-20 text-3xl font-bold border-2 border-gray-300
                              transition-all duration-200 hover:bg-gray-50
                              ${ticTacToeGameState.isGameOver || cell !== null || ticTacToeAiThinking || ticTacToeGameState.currentPlayer !== 'X' ? 'cursor-not-allowed opacity-75' : 'cursor-pointer hover:border-gray-400'}
                              ${cell === 'X' ? 'text-blue-600' : cell === 'O' ? 'text-red-600' : 'text-gray-400'}
                              bg-white
                            `}
                          >
                            {cell || ''}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="w-80 h-80 bg-white rounded-lg shadow-lg flex items-center justify-center border border-gray-200">
                      <div className="text-center text-gray-600">
                        <Grid3X3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                        <p className="text-lg font-medium mb-2">Ready to play?</p>
                        <p className="text-sm text-gray-500 mb-4">Click "New Game vs AI" to start!</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Move counter */}
                <div className="text-center text-sm text-gray-600">
                  Move: {ticTacToeGameState.moveCount} / 9
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default App;
