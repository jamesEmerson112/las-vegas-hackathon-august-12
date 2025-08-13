#!/usr/bin/env python3
"""
TicTacToe AI API Wrapper
========================
This script provides a JSON API interface to our TicTacToe AI agent.
It reads game state from stdin and returns AI moves as JSON.
"""

import sys
import json
import os
import re
from typing import Optional, Dict, Any

# Set Opik project name for TicTacToe games
os.environ["OPIK_PROJECT_NAME"] = "ollama-tictactoe-web-game"

class TicTacToeAIAPI:
    def __init__(self):
        self.ai_client = self._setup_ai()

    def _setup_ai(self):
        """Setup AI client with Opik tracking"""
        try:
            from langchain_ollama import ChatOllama
            from opik.integrations.langchain import OpikTracer

            opik_tracer = OpikTracer(tags=["tictactoe", "web-game", "api", "langchain"])

            llm = ChatOllama(
                model="llama3.2",
                temperature=0.1,  # Lower temperature for more consistent moves
                base_url="http://localhost:11434",
            ).with_config({"callbacks": [opik_tracer]})

            return llm
        except ImportError as e:
            # Fallback to OpenAI style if LangChain not available
            from openai import OpenAI
            from opik.integrations.openai import track_openai

            client = OpenAI(
                base_url="http://localhost:11434/v1/",
                api_key="ollama",
            )
            return track_openai(client)

    def get_board_state_text(self, game_state: Dict[str, Any]) -> str:
        """Convert game state to text representation for AI"""
        board = game_state.get('board', [None] * 9)
        current_player = game_state.get('currentPlayer', 'O')
        move_count = game_state.get('moveCount', 0)

        state = "Current TicTacToe board position:\n"
        state += f"{board[0] or '1'}|{board[1] or '2'}|{board[2] or '3'}\n"
        state += f"{board[3] or '4'}|{board[4] or '5'}|{board[5] or '6'}\n"
        state += f"{board[6] or '7'}|{board[7] or '8'}|{board[8] or '9'}\n\n"

        state += f"Current turn: {current_player}\n"
        state += f"Move count: {move_count}\n"

        # Show available positions
        available = []
        for i, cell in enumerate(board):
            if cell is None:
                available.append(str(i + 1))

        if available:
            state += f"Available positions: {', '.join(available)}\n"

        return state

    def get_ai_move(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI's next move"""
        try:
            # Try external AI first
            try:
                board_state = self.get_board_state_text(game_state)

                system_prompt = """You are a skilled TicTacToe-playing AI. You will be given the current 3x3 board position and need to make a move as O player.

CRITICAL RULES:
1. You are playing as O (the AI player)
2. The human player is X
3. Board positions are numbered 1-9:
   1|2|3
   4|5|6
   7|8|9
4. Respond with ONLY a single number (1-9) representing your chosen position
5. Choose only from available positions (empty spots shown as numbers)
6. Play strategically: try to win, block opponent wins, or choose good strategic positions

WINNING STRATEGY:
- Try to get 3 O's in a row (horizontal, vertical, or diagonal)
- Block the opponent from getting 3 X's in a row
- Take center (5) if available early in game
- Take corners if center not available

RESPONSE FORMAT:
Just the position number, nothing else. Example responses: "5" or "1" or "9"

Do not include any explanations, just the single digit."""

                user_message = f"""{board_state}

What position do you choose as O? Respond with only the position number (1-9)."""

                # Get AI response
                if hasattr(self.ai_client, 'invoke'):  # LangChain
                    messages = [
                        ("system", system_prompt),
                        ("human", user_message)
                    ]
                    response = self.ai_client.invoke(messages)
                    ai_response = response.content
                else:  # OpenAI style
                    response = self.ai_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        model="llama3.2"
                    )
                    ai_response = response.choices[0].message.content

                # Parse the move
                position = self._parse_move(ai_response.strip(), game_state)

                if position is not None:
                    return {
                        "success": True,
                        "move": position,
                        "thinking": ai_response.strip(),
                        "tracked_in_opik": True
                    }

            except Exception as e:
                print(f"External AI failed: {e}")

            # Fallback to strategic AI
            strategic_move = self._get_strategic_move(game_state)
            if strategic_move is not None:
                return {
                    "success": True,
                    "move": strategic_move,
                    "thinking": "Strategic AI move (Ollama unavailable)",
                    "tracked_in_opik": False
                }

            # Final fallback to random move
            board = game_state.get('board', [None] * 9)
            available = [i for i, cell in enumerate(board) if cell is None]
            if available:
                import random
                fallback_move = random.choice(available)
                return {
                    "success": True,
                    "move": fallback_move,
                    "thinking": "Random fallback move",
                    "tracked_in_opik": False
                }
            else:
                return {
                    "success": False,
                    "error": "No valid moves available",
                    "move": None
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "move": None
            }

    def _get_strategic_move(self, game_state: Dict[str, Any]) -> Optional[int]:
        """Strategic AI that doesn't require external AI services"""
        board = game_state.get('board', [None] * 9)

        # Win patterns (rows, columns, diagonals)
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]

        # 1. Try to win - look for 2 O's in a line
        for pattern in win_patterns:
            positions = [board[i] for i in pattern]
            if positions.count('O') == 2 and positions.count(None) == 1:
                for i, pos in enumerate(pattern):
                    if board[pos] is None:
                        return pos

        # 2. Block opponent win - look for 2 X's in a line
        for pattern in win_patterns:
            positions = [board[i] for i in pattern]
            if positions.count('X') == 2 and positions.count(None) == 1:
                for i, pos in enumerate(pattern):
                    if board[pos] is None:
                        return pos

        # 3. Take center if available
        if board[4] is None:
            return 4

        # 4. Take a corner
        corners = [0, 2, 6, 8]
        available_corners = [c for c in corners if board[c] is None]
        if available_corners:
            return available_corners[0]

        # 5. Take any available edge
        edges = [1, 3, 5, 7]
        available_edges = [e for e in edges if board[e] is None]
        if available_edges:
            return available_edges[0]

        return None

    def _parse_move(self, response: str, game_state: Dict[str, Any]) -> Optional[int]:
        """Parse AI response to extract move position (0-8 for internal use)"""
        try:
            board = game_state.get('board', [None] * 9)

            # Try to extract a number from the response
            numbers = re.findall(r'\b([1-9])\b', response)

            for num_str in numbers:
                position_1_to_9 = int(num_str)
                position_0_to_8 = position_1_to_9 - 1  # Convert to 0-based index

                # Check if position is valid and available
                if 0 <= position_0_to_8 <= 8 and board[position_0_to_8] is None:
                    return position_0_to_8

            return None

        except Exception:
            return None

def main():
    """Main entry point for the API"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read().strip()
        game_state = json.loads(input_data)

        # Initialize AI and get move
        ai = TicTacToeAIAPI()
        result = ai.get_ai_move(game_state)

        # Output result as JSON
        print(json.dumps(result))

    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "Invalid JSON input"
        }))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }))

if __name__ == "__main__":
    main()
