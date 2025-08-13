#!/usr/bin/env python3
"""
Chess AI API Wrapper
====================
This script provides a JSON API interface to our chess AI agent.
It reads game state from stdin and returns AI moves as JSON.
"""

import sys
import json
import os
import re
import io
import contextlib
from typing import Optional, Tuple, Dict, Any

# Set Opik project name for chess games
os.environ["OPIK_PROJECT_NAME"] = "ollama-chess-web-game"

class ChessAIAPI:
    def __init__(self):
        self.ai_client = self._setup_ai()

    def _setup_ai(self):
        """Setup AI client with Opik tracking"""
        try:
            from langchain_ollama import ChatOllama
            from opik.integrations.langchain import OpikTracer

            opik_tracer = OpikTracer(tags=["chess", "web-game", "api", "langchain"])

            llm = ChatOllama(
                model="llama3.2",
                temperature=0.3,
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
        board = game_state.get('board', {})
        current_player = game_state.get('currentPlayer', 'black')
        move_history = game_state.get('moveHistory', [])

        state = "Current chess board position:\\n"
        state += "  a b c d e f g h\\n"

        for rank in range(8, 0, -1):
            state += f"{rank} "
            for file in 'abcdefgh':
                square = f"{file}{rank}"
                piece = board.get(square, '.')
                state += f"{piece} "
            state += f" {rank}\\n"

        state += "  a b c d e f g h\\n"
        state += f"\\nCurrent turn: {current_player}\\n"
        state += f"Move count: {len(move_history)}\\n"

        if move_history:
            last_move = move_history[-1]
            state += f"Last move: {last_move.get('from', '')} -> {last_move.get('to', '')}\\n"

        return state

    def get_ai_move(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI's next move"""
        try:
            board_state = self.get_board_state_text(game_state)

            system_prompt = """You are a skilled chess-playing AI. You will be given the current board position and need to make a move as BLACK pieces (♜♞♝♛♚♟).

CRITICAL RULES:
1. You are playing as BLACK pieces only: ♜♞♝♛♚♟
2. Respond with ONLY a valid move in the exact format: {"from": "e7", "to": "e5"}
3. Use lowercase chess notation (a1-h8)
4. Make only legal chess moves
5. Play strategically - develop pieces, control center, protect king

RESPONSE FORMAT EXAMPLE:
{"from": "e7", "to": "e5"}

Do not include any other text, explanations, or formatting. Just the JSON move object."""

            user_message = f"""
{board_state}

What is your move as BLACK? Respond with only the JSON move object in the format: {{"from": "square", "to": "square"}}
"""

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
            move = self._parse_move_json(ai_response)

            return {
                "success": True,
                "move": move,
                "thinking": ai_response.strip(),
                "tracked_in_opik": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "move": None
            }

    def _parse_move_json(self, response: str) -> Optional[Dict[str, str]]:
        """Parse AI response to extract move in JSON format"""
        try:
            # Try to parse the response directly as JSON first
            try:
                move_data = json.loads(response.strip())
                if 'from' in move_data and 'to' in move_data:
                    from_sq = move_data['from'].lower()
                    to_sq = move_data['to'].lower()

                    if self._is_valid_square(from_sq) and self._is_valid_square(to_sq):
                        return {"from": from_sq, "to": to_sq}
            except json.JSONDecodeError:
                pass

            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]*\}', response)
            if json_match:
                json_str = json_match.group()
                move_data = json.loads(json_str)

                if 'from' in move_data and 'to' in move_data:
                    from_sq = move_data['from'].lower()
                    to_sq = move_data['to'].lower()

                    if self._is_valid_square(from_sq) and self._is_valid_square(to_sq):
                        return {"from": from_sq, "to": to_sq}

            # Fallback: try to parse simple format
            patterns = [
                r'([a-h][1-8])\s*[to\-]\s*([a-h][1-8])',
                r'"from"\s*:\s*"([a-h][1-8])".*"to"\s*:\s*"([a-h][1-8])"',
            ]

            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    from_sq = match.group(1).lower()
                    to_sq = match.group(2).lower()
                    return {"from": from_sq, "to": to_sq}

            return None

        except Exception:
            return None

    def _is_valid_square(self, square: str) -> bool:
        """Check if square notation is valid"""
        return (len(square) == 2 and
                square[0] in 'abcdefgh' and
                square[1] in '12345678')

def main():
    """Main entry point for the API"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read().strip()
        game_state = json.loads(input_data)

        # Capture stderr to get Opik URL
        stderr_capture = io.StringIO()

        # Initialize AI and get move
        with contextlib.redirect_stderr(stderr_capture):
            ai = ChessAIAPI()
            result = ai.get_ai_move(game_state)

        # Extract Opik URL from stderr if present
        stderr_content = stderr_capture.getvalue()
        opik_url = None

        # Look for Opik URL pattern in stderr
        url_pattern = r'https://www\.comet\.com/opik/api/v1/session/redirect/projects/\?trace_id=[^\s]+'
        url_match = re.search(url_pattern, stderr_content)
        if url_match:
            opik_url = url_match.group()

        # Add Opik URL to result if found
        if opik_url:
            result["opik_tracking_url"] = opik_url

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
