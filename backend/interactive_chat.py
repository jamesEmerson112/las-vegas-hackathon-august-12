#!/usr/bin/env python3
"""
Interactive Ollama Chat with Opik Tracking
==========================================

This script provides an interactive chat interface with Ollama that tracks
all conversations in Opik. You can choose between OpenAI-style or LangChain integration.
"""

import os
from typing import Literal

# Set Opik project name
os.environ["OPIK_PROJECT_NAME"] = "ollama-interactive-chat"

def chat_with_openai_style():
    """Chat using OpenAI-style integration"""
    from openai import OpenAI
    from opik.integrations.openai import track_openai

    client = OpenAI(
        base_url="http://localhost:11434/v1/",
        api_key="ollama",
    )
    client = track_openai(client)

    def send_message(message: str, model: str = "llama3.2") -> str:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message}],
            model=model,
        )
        return chat_completion.choices[0].message.content

    return send_message

def chat_with_langchain():
    """Chat using LangChain integration"""
    from langchain_ollama import ChatOllama
    from opik.integrations.langchain import OpikTracer

    opik_tracer = OpikTracer(tags=["interactive", "langchain", "ollama"])

    llm = ChatOllama(
        model="llama3.2",
        temperature=0.7,  # More creative responses
        base_url="http://localhost:11434",
    ).with_config({"callbacks": [opik_tracer]})

    def send_message(message: str, system_prompt: str = "You are a helpful assistant.") -> str:
        messages = [
            ("system", system_prompt),
            ("human", message),
        ]
        ai_msg = llm.invoke(messages)
        return ai_msg.content

    return send_message

def main():
    print("🤖 Interactive Ollama Chat with Opik Tracking")
    print("=" * 50)

    # Choose integration method
    print("Choose integration method:")
    print("1. OpenAI-style (faster)")
    print("2. LangChain (more features)")

    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Please enter 1 or 2")

    # Initialize the chosen chat method
    if choice == "1":
        print("\n🔧 Using OpenAI-style integration...")
        send_message = chat_with_openai_style()
        integration_type = "OpenAI"
    else:
        print("\n🔧 Using LangChain integration...")
        send_message = chat_with_langchain()
        integration_type = "LangChain"

    print(f"✅ {integration_type} integration ready!")
    print("\n💬 Start chatting! (type 'quit' to exit, 'clear' to see instructions again)")
    print("All conversations will be tracked in Opik at: https://www.comet.com/opik/")
    print("-" * 50)

    conversation_count = 0

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()

            if user_input.lower() == 'quit':
                print(f"\n👋 Goodbye! Had {conversation_count} conversations tracked in Opik.")
                break

            if user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print("💬 Continue chatting! (type 'quit' to exit)")
                print("-" * 50)
                continue

            if not user_input:
                continue

            print("🤖 Assistant: ", end="", flush=True)

            # Send message and get response
            response = send_message(user_input)
            print(response)

            conversation_count += 1
            print(f"\n✅ Conversation #{conversation_count} tracked in Opik")

        except KeyboardInterrupt:
            print(f"\n\n👋 Goodbye! Had {conversation_count} conversations tracked in Opik.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Make sure Ollama is running: `ollama serve`")

if __name__ == "__main__":
    main()
