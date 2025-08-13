#!/usr/bin/env python3
"""
Quick setup and test script for Ollama + Weaviate + Opik
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages"""
    packages = [
        "opik",
        "openai",
        "weaviate-client"
    ]

    print("🔧 Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def pull_model():
    """Pull llama3.2 model if not available"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "llama3.2" in result.stdout:
            print("✅ llama3.2 model is available")
        else:
            print("📥 Pulling llama3.2 model...")
            subprocess.check_call(["ollama", "pull", "llama3.2"])
            print("✅ llama3.2 model pulled")
    except subprocess.CalledProcessError:
        print("❌ Failed to pull model. Make sure Ollama is installed and running")

def test_weaviate_connection():
    """Test Weaviate connection"""
    try:
        import weaviate
        from weaviate.classes.init import Auth

        WEAVIATE_CLUSTER_URL = 'https://4oreows2qroxgn0tjgj2uq.c0.us-west3.gcp.weaviate.cloud'
        WEAVIATE_API_KEY = 'aVcyNUdKT2d3WHMxcHFzYl9CL3haUXVkajhzSWtzRmFFamRWa0dOSjZEVGR1SVBWNTYzT21iSkVVeWJVPV92MjAw'

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_CLUSTER_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
        )

        if client.is_connected():
            print("✅ Weaviate connection successful")

            # Try to get collections
            collections = list(client.collections.list_all().keys())
            print(f"📚 Available collections: {collections}")

            client.close()
            return True
        else:
            print("❌ Weaviate connection failed")
            return False

    except Exception as e:
        print(f"❌ Weaviate test failed: {e}")
        return False

def setup_opik():
    """Setup Opik configuration"""
    try:
        import opik
        opik.configure(use_local=False)
        print("✅ Opik configured (you may need to authenticate)")
        return True
    except Exception as e:
        print(f"❌ Opik setup failed: {e}")
        return False

def main():
    print("🚀 Setting up Ollama + Weaviate + Opik environment...\n")

    # Install packages
    install_packages()
    print()

    # Check components
    ollama_ok = check_ollama()
    if ollama_ok:
        pull_model()
    print()

    weaviate_ok = test_weaviate_connection()
    print()

    opik_ok = setup_opik()
    print()

    # Summary
    print("📋 Setup Summary:")
    print(f"   Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"   Weaviate: {'✅' if weaviate_ok else '❌'}")
    print(f"   Opik: {'✅' if opik_ok else '❌'}")

    if all([ollama_ok, weaviate_ok, opik_ok]):
        print("\n🎉 All systems ready! You can now run the RAG script.")
        print("\n💡 To run the example:")
        print("   python hack_night_vegas_august_12_comet___weaviate.py")
    else:
        print("\n⚠️  Some components need attention. Check the errors above.")

if __name__ == "__main__":
    main()
