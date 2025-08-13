import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { RotateCcw, Crown } from 'lucide-react';
import './App.css';
import { ChessLogic, ChessMove, GameState } from './chess/ChessLogic';
import { ChessBoard } from './chess/ChessComponents';

const API_BASE = 'http://localhost:3001/api';

const App: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [validMoves, setValidMoves] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [aiThinking, setAiThinking] = useState(false);
  const [status, setStatus] = useState('Click "New Game" to start');
  const [error, setError] = useState<string | null>(null);
  const [opikTrackingUrl, setOpikTrackingUrl] = useState<string | null>(null);

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

  // Clear error after a few seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const lastMove: ChessMove | null = gameState?.moveHistory[gameState.moveHistory.length - 1] || null;

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Chess vs Ollama AI
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Game Controls */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h2 className="text-lg font-semibold mb-4 text-gray-900">
                Game Controls
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

      </div>
    </div>
  );
};

export default App;
