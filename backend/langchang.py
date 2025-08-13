from langchain_ollama import ChatOllama
from opik.integrations.langchain import OpikTracer
import os

# Set Opik project name
os.environ["OPIK_PROJECT_NAME"] = "ollama-langchain-integration"

# Create the Opik tracer
opik_tracer = OpikTracer(tags=["langchain", "ollama", "chat"])

# Create the Ollama model and configure it to use the Opik tracer
llm = ChatOllama(
    model="llama3.2",  # Using available model
    temperature=0,
    base_url="http://localhost:11434",  # Explicit Ollama URL
).with_config({"callbacks": [opik_tracer]})

# Test function to consistently run conversations
def chat_with_tracking(user_message, system_prompt="You are a helpful assistant."):
    """
    Send a message to Ollama and track it with Opik
    """
    messages = [
        ("system", system_prompt),
        ("human", user_message),
    ]

    print(f"🚀 Sending message: {user_message}")
    ai_msg = llm.invoke(messages)
    print(f"🤖 Response: {ai_msg.content}")
    print("✅ Interaction tracked in Opik")
    return ai_msg

# Example conversations that will all be tracked
if __name__ == "__main__":
    # Test 1: Translation
    chat_with_tracking(
        "I love programming.",
        "You are a helpful assistant that translates English to French."
    )

    print("\n" + "="*50 + "\n")

    # Test 2: General chat
    chat_with_tracking(
        "Explain what machine learning is in simple terms."
    )

    print("\n" + "="*50 + "\n")

    # Test 3: Code help
    chat_with_tracking(
        "Write a Python function to calculate fibonacci numbers.",
        "You are a helpful coding assistant."
    )