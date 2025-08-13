#!/usr/bin/env python3
"""
Test the Complete AI Humanizer System
This script tests the full pipeline: Weaviate storage + Opik tracking + AI humanization
"""

import os
import opik
import weaviate
from weaviate.classes.init import Auth
from openai import OpenAI
from datetime import datetime

# Configure Opik
opik.configure(use_local=False)
os.environ["OPIK_PROJECT_NAME"] = "ai-humanizer-test"

# Setup Ollama client
ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Connect to Weaviate
WEAVIATE_CLUSTER_URL = os.getenv('WEAVIATE_CLUSTER_URL') or 'https://4oreows2qroxgn0tjgj2uq.c0.us-west3.gcp.weaviate.cloud'
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY') or 'aVcyNUdKT2d3WHMxcHFzYl9CL3haUXVkajhzSWtzRmFFamRWa0dOSjZEVGR1SVBWNTYzT21iSkVVeWJVPV92MjAw'

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_CLUSTER_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
)

def test_weaviate_connection():
    """Test if Weaviate is connected and has our data"""
    print("🔌 Testing Weaviate connection...")

    try:
        is_connected = weaviate_client.is_connected()
        print(f"✅ Connected: {is_connected}")

        collections = weaviate_client.collections.list_all()
        print(f"📋 Available collections: {list(collections.keys())}")

        # Check our collections
        for collection_name in ["BookRecs", "RoboticTextExamples", "TextHumanizer"]:
            if collection_name in collections:
                collection = weaviate_client.collections.get(collection_name)
                results = collection.query.fetch_objects(limit=1)
                count = len(collection.query.fetch_objects(limit=100).objects)
                print(f"  ✅ {collection_name}: {count} objects")
            else:
                print(f"  ❌ {collection_name}: Not found")

        return True

    except Exception as e:
        print(f"❌ Weaviate test failed: {e}")
        return False

@opik.track
def test_robotic_text_search(query):
    """Test searching for similar robotic text examples"""
    print(f"🔍 Testing robotic text search for: '{query}'")

    try:
        robotic_collection = weaviate_client.collections.get("RoboticTextExamples")

        # Try BM25 search
        results = robotic_collection.query.bm25(query=query, limit=3)

        examples = []
        print(f"📚 Found {len(results.objects)} similar examples:")

        for i, result in enumerate(results.objects, 1):
            props = result.properties
            print(f"  {i}. [{props['category']}] Score: {props['formality_score']}/10")
            print(f"     Text: {props['text'][:100]}...")

            examples.append({
                "text": props["text"],
                "category": props["category"],
                "formality_score": props["formality_score"]
            })

        return examples

    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return []

@opik.track
def test_ai_humanization(robotic_text, examples):
    """Test the AI humanization process"""
    print(f"🤖➡️👤 Testing AI humanization...")

    examples_text = ""
    if examples:
        examples_text = "\n\nHere are similar examples from our database:\n"
        for i, ex in enumerate(examples[:2], 1):
            examples_text += f"\nExample {i} [{ex['category']}]:\n"
            examples_text += f"Original: {ex['text'][:80]}...\n"

    prompt = f"""
You are an expert at making formal, robotic text sound more human and natural.

Make this text sound more human, warm, and conversational:
"{robotic_text}"

Guidelines:
- Use simpler, everyday words
- Make it sound like a real person talking
- Keep it friendly and approachable
- Remove unnecessary formality
- Keep the core message intact
{examples_text}

Return ONLY the humanized version, nothing else.
"""

    try:
        response = ollama_client.chat.completions.create(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        humanized = response.choices[0].message.content.strip()
        print(f"✨ Humanized result: {humanized}")
        return humanized

    except Exception as e:
        print(f"❌ AI humanization failed: {e}")
        return f"Error: {e}"

@opik.track
def test_save_to_weaviate(original, humanized, category):
    """Test saving results back to Weaviate"""
    print(f"💾 Testing save to Weaviate...")

    try:
        humanizer_collection = weaviate_client.collections.get("TextHumanizer")

        data = {
            "original_text": original,
            "humanized_text": humanized,
            "text_type": category,
            "user_id": "test_user",
            "timestamp": datetime.now().isoformat(),
            "humanization_score": 8.0,  # Could calculate this
            "tags": ["test", "automated", category]
        }

        humanizer_collection.data.insert(properties=data)
        print("✅ Successfully saved to TextHumanizer collection!")
        return True

    except Exception as e:
        print(f"❌ Save test failed: {e}")
        return False

@opik.track(name="full-system-test")
def run_full_system_test():
    """Run the complete system test"""
    print("🚀 RUNNING FULL SYSTEM TEST")
    print("=" * 50)

    # Test cases
    test_cases = [
        {
            "text": "We regret to inform you that your application has been unsuccessful at this time.",
            "category": "corporate_email"
        },
        {
            "text": "The implementation of the aforementioned solution requires comprehensive analysis of existing infrastructure.",
            "category": "technical"
        },
        {
            "text": "Pursuant to our previous correspondence, please be advised that the meeting has been rescheduled.",
            "category": "formal_communication"
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['category']}")
        print("-" * 40)

        robotic_text = test_case["text"]
        category = test_case["category"]

        print(f"🤖 Original: {robotic_text}")

        # 1. Search for similar examples
        examples = test_robotic_text_search(robotic_text)

        # 2. Humanize the text
        humanized = test_ai_humanization(robotic_text, examples)

        # 3. Save the result
        saved = test_save_to_weaviate(robotic_text, humanized, category)

        result = {
            "original": robotic_text,
            "humanized": humanized,
            "examples_found": len(examples),
            "saved": saved
        }
        results.append(result)

        print(f"✅ Test case {i} completed!")

    return results

def main():
    """Main test function"""
    print("🧪 AI HUMANIZER SYSTEM TEST")
    print("=" * 50)
    print("Testing the complete pipeline: Weaviate + Opik + AI Humanization")

    # 1. Test Weaviate connection
    if not test_weaviate_connection():
        print("❌ Weaviate test failed. Cannot continue.")
        return

    print(f"\n" + "="*50)

    # 2. Run full system test
    results = run_full_system_test()

    # 3. Summary
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 50)

    successful_tests = sum(1 for r in results if r["saved"])

    print(f"✅ Successful tests: {successful_tests}/{len(results)}")
    print(f"📊 Total examples found: {sum(r['examples_found'] for r in results)}")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {'✅' if result['saved'] else '❌'} Test {i}")
        print(f"   Original: {result['original'][:50]}...")
        print(f"   Humanized: {result['humanized'][:50]}...")

    print(f"\n🎉 System test completed!")
    print(f"💡 Check your Opik dashboard for detailed traces!")
    print(f"🔍 Check your Weaviate console for stored data!")

    # Cleanup
    weaviate_client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n✅ Test interrupted. Goodbye!")
        weaviate_client.close()
