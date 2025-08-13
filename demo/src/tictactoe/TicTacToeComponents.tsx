import React from 'react';
import { GameState, GameStats, Player, TicTacToeLogic } from './TicTacToeLogic';

// Individual cell component
interface CellProps {
  value: Player | null;
  onClick: () => void;
  isWinning: boolean;
  disabled: boolean;
}

export const Cell: React.FC<CellProps> = ({ value, onClick, isWinning, disabled }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        w-20 h-20 text-3xl font-bold border-2 border-gray-300
        transition-all duration-200 hover:bg-gray-50
        ${isWinning ? 'bg-green-100 border-green-400' : 'bg-white'}
        ${disabled ? 'cursor-not-allowed opacity-75' : 'cursor-pointer hover:border-gray-400'}
        ${value === 'X' ? 'text-blue-600' : value === 'O' ? 'text-red-600' : 'text-gray-400'}
      `}
    >
      {value || ''}
    </button>
  );
};

// Game board component
interface GameBoardProps {
  gameState: GameState;
  onCellClick: (position: number) => void;
}

export const GameBoard: React.FC<GameBoardProps> = ({ gameState, onCellClick }) => {
  const winningPattern = TicTacToeLogic.getWinningPattern(gameState.board);

  return (
    <div className="inline-block bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <div className="grid grid-cols-3 gap-2">
        {gameState.board.map((cell, index) => (
          <Cell
            key={index}
            value={cell}
            onClick={() => onCellClick(index)}
            isWinning={winningPattern.includes(index)}
            disabled={gameState.isGameOver || cell !== null}
          />
        ))}
      </div>
    </div>
  );
};

// Game status component
interface GameStatusProps {
  gameState: GameState;
}

export const GameStatus: React.FC<GameStatusProps> = ({ gameState }) => {
  const message = TicTacToeLogic.getGameResultMessage(gameState);
  const isGameOver = gameState.isGameOver;

  return (
    <div className={`
      p-4 rounded-lg text-center font-medium
      ${isGameOver
        ? gameState.winner
          ? 'bg-green-50 border border-green-200 text-green-800'
          : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
        : 'bg-blue-50 border border-blue-200 text-blue-800'
      }
    `}>
      <p className="text-lg">{message}</p>
      {!isGameOver && (
        <p className="text-sm mt-1 opacity-75">
          {gameState.currentPlayer === 'X' ? 'Blue player' : 'Red player'} to move
        </p>
      )}
    </div>
  );
};

// Game statistics component
interface GameStatsProps {
  stats: GameStats;
}

export const GameStatsDisplay: React.FC<GameStatsProps> = ({ stats }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Game Statistics</h3>
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-blue-600 font-medium">X Wins:</span>
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-bold">
            {stats.xWins}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-red-600 font-medium">O Wins:</span>
          <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-bold">
            {stats.oWins}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-yellow-600 font-medium">Draws:</span>
          <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-bold">
            {stats.draws}
          </span>
        </div>
        <div className="border-t pt-3 flex justify-between items-center">
          <span className="text-gray-600 font-medium">Total Games:</span>
          <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-bold">
            {stats.totalGames}
          </span>
        </div>
      </div>
    </div>
  );
};

// Complete tic-tac-toe game component
interface TicTacToeGameProps {
  gameState: GameState;
  stats: GameStats;
  onCellClick: (position: number) => void;
  onNewGame: () => void;
  onResetStats: () => void;
}

export const TicTacToeGame: React.FC<TicTacToeGameProps> = ({
  gameState,
  stats,
  onCellClick,
  onNewGame,
  onResetStats,
}) => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Game Controls */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">
              Game Controls
            </h2>

            <div className="space-y-3">
              <button
                onClick={onNewGame}
                className="w-full bg-gray-900 hover:bg-gray-800 text-white
                         font-semibold py-3 px-4 rounded-lg transition-colors
                         flex items-center justify-center gap-2"
              >
                🎮 New Game
              </button>

              <button
                onClick={onResetStats}
                className="w-full bg-red-600 hover:bg-red-700 text-white
                         font-semibold py-2 px-4 rounded-lg transition-colors
                         flex items-center justify-center gap-2 text-sm"
              >
                🔄 Reset Stats
              </button>
            </div>
          </div>

          <GameStatsDisplay stats={stats} />
        </div>

        {/* Game Board */}
        <div className="lg:col-span-2 space-y-6">
          <GameStatus gameState={gameState} />

          <div className="flex justify-center">
            <GameBoard gameState={gameState} onCellClick={onCellClick} />
          </div>

          {/* Move counter */}
          <div className="text-center text-sm text-gray-600">
            Move: {gameState.moveCount} / 9
          </div>
        </div>
      </div>
    </div>
  );
};
