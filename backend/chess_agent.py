#!/usr/bin/env python3
"""
Chess AI Agent with Ollama & Opik Tracking
==========================================

A chess-playing AI agent using Ollama with complete game tracking in Opik.
Features:
- Interactive chess gameplay
- Visual board representation
- Move validation
- Game state tracking
- All AI decisions tracked in Opik
"""

import os
import re
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Set Opik project name for chess games
os.environ["OPIK_PROJECT_NAME"] = "ollama-chess-agent"

class PieceType(Enum):
    PAWN = "P"
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

@dataclass
class ChessMove:
    from_square: str
    to_square: str
    piece: str
    is_capture: bool = False
    is_check: bool = False
    is_checkmate: bool = False
    notation: str = ""

class ChessBoard:
    def __init__(self):
        self.board = self._init_board()
        self.current_player = Color.WHITE
        self.move_history = []
        self.game_over = False
        self.winner = None

    def _init_board(self):
        """Initialize chess board with starting position"""
        board = {}

        # White pieces
        board.update({
            'a1': '♖', 'b1': '♘', 'c1': '♗', 'd1': '♕', 'e1': '♔', 'f1': '♗', 'g1': '♘', 'h1': '♖',
            'a2': '♙', 'b2': '♙', 'c2': '♙', 'd2': '♙', 'e2': '♙', 'f2': '♙', 'g2': '♙', 'h2': '♙'
        })

        # Black pieces
        board.update({
            'a8': '♜', 'b8': '♞', 'c8': '♝', 'd8': '♛', 'e8': '♚', 'f8': '♝', 'g8': '♞', 'h8': '♜',
            'a7': '♟', 'b7': '♟', 'c7': '♟', 'd7': '♟', 'e7': '♟', 'f7': '♟', 'g7': '♟', 'h7': '♟'
        })

        return board

    def display_board(self):
        """Display the chess board in a nice format"""
        print("\n  ┌───┬───┬───┬───┬───┬───┬───┬───┐")
        for rank in range(8, 0, -1):
            print(f"{rank} │", end="")
            for file in 'abcdefgh':
                square = f"{file}{rank}"
                piece = self.board.get(square, ' ')
                print(f" {piece} │", end="")
            print(f" {rank}")
            if rank > 1:
                print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")
        print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
        print("    a   b   c   d   e   f   g   h")
        print()

    def is_valid_square(self, square: str) -> bool:
        """Check if square notation is valid"""
        return len(square) == 2 and square[0] in 'abcdefgh' and square[1] in '12345678'

    def make_move(self, from_sq: str, to_sq: str) -> bool:
        """Make a move if valid"""
        if not (self.is_valid_square(from_sq) and self.is_valid_square(to_sq)):
            return False

        if from_sq not in self.board:
            return False

        # Simple move validation (basic implementation)
        piece = self.board[from_sq]

        # Move the piece
        self.board[to_sq] = piece
        del self.board[from_sq]

        # Record move
        move = ChessMove(from_sq, to_sq, piece, notation=f"{from_sq}-{to_sq}")
        self.move_history.append(move)

        # Switch players
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

        return True

    def get_board_state(self) -> str:
        """Get current board state as text for AI"""
        state = "Current board position:\n"
        state += "  a b c d e f g h\n"

        for rank in range(8, 0, -1):
            state += f"{rank} "
            for file in 'abcdefgh':
                square = f"{file}{rank}"
                piece = self.board.get(square, '.')
                state += f"{piece} "
            state += f" {rank}\n"

        state += "  a b c d e f g h\n"
        state += f"\nCurrent turn: {self.current_player.value}\n"

        if self.move_history:
            last_move = self.move_history[-1]
            state += f"Last move: {last_move.notation}\n"

        return state

    def get_legal_moves_hint(self) -> str:
        """Get a hint about possible moves (simplified)"""
        pieces = []
        for square, piece in self.board.items():
            if self.current_player == Color.BLACK and piece in '♜♞♝♛♚♟':
                pieces.append(f"{piece} on {square}")
            elif self.current_player == Color.WHITE and piece in '♖♘♗♕♔♙':
                pieces.append(f"{piece} on {square}")

        return f"Your pieces: {', '.join(pieces[:8])}..."  # Limit output

class ChessAI:
    def __init__(self, use_langchain: bool = True):
        self.use_langchain = use_langchain
        self.ai_client = self._setup_ai()

    def _setup_ai(self):
        """Setup AI client with Opik tracking"""
        if self.use_langchain:
            from langchain_ollama import ChatOllama
            from opik.integrations.langchain import OpikTracer

            opik_tracer = OpikTracer(tags=["chess", "game", "ai-agent", "langchain"])

            llm = ChatOllama(
                model="llama3.2",
                temperature=0.3,  # Slightly creative but focused
                base_url="http://localhost:11434",
            ).with_config({"callbacks": [opik_tracer]})

            return llm
        else:
            from openai import OpenAI
            from opik.integrations.openai import track_openai

            client = OpenAI(
                base_url="http://localhost:11434/v1/",
                api_key="ollama",
            )
            return track_openai(client)

    def get_ai_move(self, board: ChessBoard) -> Optional[Tuple[str, str]]:
        """Get AI's next move"""
        board_state = board.get_board_state()
        legal_moves_hint = board.get_legal_moves_hint()

        system_prompt = """You are a chess-playing AI. You will be given the current board position and need to make a move.

IMPORTANT RULES:
1. You are playing as BLACK pieces (♜♞♝♛♚♟)
2. Respond with ONLY the move in format: from_square to_square (e.g., "e7 e5" or "g8 f6")
3. Use standard chess notation (a1-h8)
4. Make legal moves only
5. Try to play good chess - develop pieces, control center, protect king

Example response: "e7 e5" """

        user_message = f"""
{board_state}

{legal_moves_hint}

It's your turn (BLACK). What's your move?
Respond with only the move in format: from_square to_square
"""

        print("🤖 AI is thinking...")

        if self.use_langchain:
            messages = [
                ("system", system_prompt),
                ("human", user_message)
            ]
            response = self.ai_client.invoke(messages)
            ai_response = response.content
        else:
            response = self.ai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama3.2"
            )
            ai_response = response.choices[0].message.content

        print(f"🤖 AI says: {ai_response}")

        # Parse the move
        move = self._parse_move(ai_response)
        if move:
            print(f"✅ AI move parsed: {move[0]} -> {move[1]}")
        else:
            print("❌ Failed to parse AI move")

        return move

    def _parse_move(self, response: str) -> Optional[Tuple[str, str]]:
        """Parse AI response to extract move"""
        # Look for patterns like "e7 e5" or "e7-e5" or "e7 to e5"
        patterns = [
            r'([a-h][1-8])\s+([a-h][1-8])',  # "e7 e5"
            r'([a-h][1-8])-([a-h][1-8])',     # "e7-e5"
            r'([a-h][1-8])\s+to\s+([a-h][1-8])',  # "e7 to e5"
            r'Move:\s*([a-h][1-8])\s+([a-h][1-8])',  # "Move: e7 e5"
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return (match.group(1).lower(), match.group(2).lower())

        return None

def main():
    print("♔♕♖♗♘♙ Chess AI Agent with Ollama & Opik ♟♞♝♜♛♚")
    print("=" * 50)
    print("You play as WHITE (♔♕♖♗♘♙), AI plays as BLACK (♚♛♜♝♞♟)")
    print("Enter moves like: e2 e4")
    print("Type 'quit' to exit")
    print("=" * 50)

    # Choose AI integration
    print("\nChoose AI integration:")
    print("1. LangChain (recommended)")
    print("2. OpenAI-style")

    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Please enter 1 or 2")

    use_langchain = choice == "1"

    # Initialize game
    board = ChessBoard()
    ai = ChessAI(use_langchain=use_langchain)

    print(f"\n🎮 Game started! Using {'LangChain' if use_langchain else 'OpenAI-style'} integration")
    print("🔍 All moves will be tracked in Opik at: https://www.comet.com/opik/")

    game_number = 1

    while not board.game_over:
        board.display_board()

        if board.current_player == Color.WHITE:
            # Human turn
            print(f"🧑 Your turn (WHITE). Move #{len(board.move_history) + 1}")
            move_input = input("Enter your move (e.g., 'e2 e4') or 'quit': ").strip().lower()

            if move_input == 'quit':
                print("👋 Thanks for playing!")
                break

            # Parse human move
            parts = move_input.split()
            if len(parts) != 2:
                print("❌ Invalid format. Use: e2 e4")
                continue

            from_sq, to_sq = parts
            if board.make_move(from_sq, to_sq):
                print(f"✅ You moved: {from_sq} -> {to_sq}")
            else:
                print("❌ Invalid move. Try again.")
                continue

        else:
            # AI turn
            print(f"🤖 AI's turn (BLACK). Move #{len(board.move_history) + 1}")

            ai_move = ai.get_ai_move(board)
            if ai_move:
                from_sq, to_sq = ai_move
                if board.make_move(from_sq, to_sq):
                    print(f"🤖 AI moved: {from_sq} -> {to_sq}")
                    print("✅ Move tracked in Opik")
                else:
                    print("❌ AI made invalid move. Game continues...")
                    # For now, just switch back to human
                    board.current_player = Color.WHITE
            else:
                print("❌ AI couldn't make a move. Game continues...")
                board.current_player = Color.WHITE

        # Simple game end check (you can enhance this)
        if len(board.move_history) >= 50:  # Limit for demo
            print("\n🏁 Game ended after 50 moves!")
            board.game_over = True

    board.display_board()
    print(f"\n📊 Game summary:")
    print(f"Total moves: {len(board.move_history)}")
    print("🔍 All game data tracked in Opik!")

if __name__ == "__main__":
    main()
