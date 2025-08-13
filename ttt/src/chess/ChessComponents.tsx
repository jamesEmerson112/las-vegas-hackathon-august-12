import React from 'react';
import { ChessMove } from './ChessLogic';

interface ChessSquareProps {
  square: string;
  piece: string | null;
  isSelected: boolean;
  isHighlighted: boolean;
  isValidMove: boolean;
  onClick: () => void;
}

export const ChessSquare: React.FC<ChessSquareProps> = ({
  square,
  piece,
  isSelected,
  isHighlighted,
  isValidMove,
  onClick
}) => {
  const file = square.charCodeAt(0) - 'a'.charCodeAt(0);
  const rank = parseInt(square[1]) - 1;

  // Fix the chess board color pattern: a1 should be dark
  const isLightSquare = (file + rank) % 2 === 1;

  const baseClasses = `
    w-16 h-16 flex items-center justify-center text-2xl cursor-pointer
    transition-all duration-150 hover:opacity-80 select-none relative
  `;

  // Traditional chess colors: light squares are cream/beige, dark squares are brown
  const colorClasses = isLightSquare
    ? 'bg-amber-100 text-gray-900'
    : 'bg-amber-800 text-white';

  const stateClasses = isSelected
    ? 'ring-4 ring-blue-500 ring-inset'
    : isHighlighted
    ? 'ring-4 ring-yellow-400 ring-inset'
    : '';

  return (
    <div
      className={`${baseClasses} ${colorClasses} ${stateClasses}`}
      onClick={onClick}
    >
      {piece && (
        <span className="text-3xl font-bold drop-shadow-sm">
          {piece}
        </span>
      )}
      {/* Show possible move indicator */}
      {isValidMove && !piece && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 bg-green-500 rounded-full opacity-60" />
        </div>
      )}
      {isValidMove && piece && (
        <div className="absolute inset-0 bg-red-500 opacity-20 rounded" />
      )}
    </div>
  );
};

interface ChessBoardProps {
  board: Record<string, string>;
  selectedSquare: string | null;
  onSquareClick: (square: string) => void;
  lastMove: ChessMove | null;
  validMoves: string[];
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  board,
  selectedSquare,
  onSquareClick,
  lastMove,
  validMoves
}) => {
  const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const ranks = [8, 7, 6, 5, 4, 3, 2, 1];

  const isHighlighted = (square: string): boolean => {
    return lastMove ? (square === lastMove.from || square === lastMove.to) : false;
  };

  const isValidMove = (square: string): boolean => {
    return validMoves.includes(square);
  };

  return (
    <div className="relative bg-amber-900 p-6 rounded-lg shadow-xl border-2 border-amber-800">
      {/* Rank labels (left side) */}
      <div className="absolute left-1 top-6 flex flex-col h-full justify-center">
        {ranks.map(rank => (
          <div key={rank} className="h-16 flex items-center justify-center text-amber-100 font-bold text-lg">
            {rank}
          </div>
        ))}
      </div>

      {/* File labels (bottom) */}
      <div className="absolute bottom-1 left-6 flex w-full justify-center">
        {files.map(file => (
          <div key={file} className="w-16 flex items-center justify-center text-amber-100 font-bold text-lg">
            {file}
          </div>
        ))}
      </div>

      {/* Chess board */}
      <div className="grid grid-cols-8 gap-0 border-4 border-amber-800 shadow-inner">
        {ranks.map(rank =>
          files.map(file => {
            const square = `${file}${rank}`;
            const piece = board[square] || null;
            return (
              <ChessSquare
                key={square}
                square={square}
                piece={piece}
                isSelected={selectedSquare === square}
                isHighlighted={isHighlighted(square)}
                isValidMove={isValidMove(square)}
                onClick={() => onSquareClick(square)}
              />
            );
          })
        )}
      </div>
    </div>
  );
};
