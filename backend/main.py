from openai import OpenAI
from opik.integrations.openai import track_openai
import os

# Set Opik project name
os.environ["OPIK_PROJECT_NAME"] = "ollama-integration"

# Create an OpenAI client
client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama",  # Required but ignored by Ollama
)

# Log all traces made with the OpenAI client to Opik
client = track_openai(client)

def chat_with_ollama(message, model="llama3.2"):
    """
    Send a message to Ollama and get tracked response
    """
    print(f"🚀 Sending: {message}")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model=model,
    )

    response = chat_completion.choices[0].message.content
    print(f"🤖 Response: {response}")
    print("✅ Interaction tracked in Opik")
    return response

# Test different interactions - all will be tracked
if __name__ == "__main__":
    # Test 1: Simple test
    chat_with_ollama("Say this is a test")

    print("\n" + "="*50 + "\n")

    # Test 2: Ask a question
    chat_with_ollama("What is the capital of France?")

    print("\n" + "="*50 + "\n")

    # Test 3: Code question
    chat_with_ollama("Write a hello world program in Python")