#!/usr/bin/env python3
"""
AI Text Humanizer with Weaviate Storage and Opik Tracking
This tool humanizes formal/robotic text and stores everything for future reference.
"""

import os
import opik
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
from openai import OpenAI
from datetime import datetime
import uuid

# Configure Opik
opik.configure(use_local=False)
os.environ["OPIK_PROJECT_NAME"] = "ai-humanizer-project"

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

def setup_humanizer_collection():
    """Setup the TextHumanizer collection in Weaviate"""
    print("🔧 Setting up TextHumanizer collection...")

    try:
        collections = weaviate_client.collections.list_all()

        if "TextHumanizer" not in collections:
            print("📝 Creating TextHumanizer collection...")

            weaviate_client.collections.create(
                name="TextHumanizer",
                properties=[
                    Property(name="original_text", data_type=DataType.TEXT),
                    Property(name="humanized_text", data_type=DataType.TEXT),
                    Property(name="text_type", data_type=DataType.TEXT),  # email, blog, technical, etc.
                    Property(name="user_id", data_type=DataType.TEXT),
                    Property(name="timestamp", data_type=DataType.TEXT),
                    Property(name="humanization_score", data_type=DataType.NUMBER),  # 1-10 how human it sounds
                    Property(name="tags", data_type=DataType.TEXT_ARRAY),
                ],
            )

            # Add some sample data
            sample_data = [
                {
                    "original_text": "Please be advised that your request has been received and is currently under review by our team. We will provide you with an update regarding the status of your inquiry within 3-5 business days.",
                    "humanized_text": "Thanks for reaching out! We got your message and we're looking into it. We'll get back to you in the next few days with an update.",
                    "text_type": "customer_service",
                    "user_id": "sample_user",
                    "timestamp": datetime.now().isoformat(),
                    "humanization_score": 8.5,
                    "tags": ["formal_to_casual", "customer_service", "email"]
                },
                {
                    "original_text": "The implementation of the aforementioned solution requires comprehensive analysis of the existing infrastructure and subsequent optimization of the current workflow processes.",
                    "humanized_text": "To make this solution work, we need to take a good look at what we have now and figure out how to make our processes better.",
                    "text_type": "technical",
                    "user_id": "sample_user",
                    "timestamp": datetime.now().isoformat(),
                    "humanization_score": 7.8,
                    "tags": ["technical_jargon", "business", "simplification"]
                },
                {
                    "original_text": "Pursuant to our previous correspondence, kindly note that the scheduled maintenance window has been rescheduled to accommodate operational requirements.",
                    "humanized_text": "Hey! Just wanted to let you know we had to move the maintenance time to work better with our schedule.",
                    "text_type": "notification",
                    "user_id": "sample_user",
                    "timestamp": datetime.now().isoformat(),
                    "humanization_score": 8.2,
                    "tags": ["formal_to_casual", "notification", "scheduling"]
                }
            ]

            humanizer_collection = weaviate_client.collections.get("TextHumanizer")
            print("📊 Adding sample humanization data...")

            with humanizer_collection.batch.dynamic() as batch:
                for data in sample_data:
                    batch.add_object(properties=data)

            print("✅ TextHumanizer collection created and populated!")
        else:
            print("✅ TextHumanizer collection already exists!")

        return weaviate_client.collections.get("TextHumanizer")

    except Exception as e:
        print(f"❌ Error setting up collection: {e}")
        return None

@opik.track
def find_similar_humanizations(text, collection, limit=3):
    """Find similar humanization examples from the database"""
    try:
        # Use BM25 search to find similar text patterns
        results = collection.query.bm25(query=text, limit=limit)

        examples = []
        for result in results.objects:
            props = result.properties
            examples.append({
                "original": props["original_text"],
                "humanized": props["humanized_text"],
                "type": props["text_type"],
                "score": props.get("humanization_score", 0)
            })
        return examples
    except Exception as e:
        print(f"Error finding examples: {e}")
        return []

@opik.track
def call_humanizer_llm(text, examples):
    """Call the LLM to humanize the text"""

    examples_text = ""
    if examples:
        examples_text = "\n\nHere are some examples of good humanization:\n"
        for i, ex in enumerate(examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Original: {ex['original'][:100]}...\n"
            examples_text += f"Humanized: {ex['humanized'][:100]}...\n"

    prompt = f"""
You are an expert at making formal, robotic, or overly technical text sound more human and natural.

Your task: Make this text sound more human, warm, and conversational while keeping the same meaning.

Guidelines:
- Use simpler, everyday words instead of jargon
- Make it sound like a real person is talking
- Keep it friendly and approachable
- Remove unnecessary formality
- Make it concise but not abrupt
- Keep the core message intact

{examples_text}

Now humanize this text:
"{text}"

Return ONLY the humanized version, nothing else.
"""

    try:
        response = ollama_client.chat.completions.create(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

@opik.track
def calculate_humanization_score(original, humanized):
    """Calculate how 'human' the text sounds (1-10)"""

    prompt = f"""
Rate how human and natural this text sounds on a scale of 1-10, where:
- 1 = Very robotic, formal, corporate-speak
- 10 = Very human, natural, conversational

Consider:
- Use of simple language vs jargon
- Conversational tone vs formal tone
- Natural flow vs stilted phrasing
- Warmth and personality vs cold professionalism

Original text: "{original}"
Humanized text: "{humanized}"

Return ONLY a number between 1 and 10 (can include decimals like 7.5).
"""

    try:
        response = ollama_client.chat.completions.create(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        score_text = response.choices[0].message.content.strip()
        # Extract number from response
        score = float(''.join(c for c in score_text if c.isdigit() or c == '.'))
        return min(10.0, max(1.0, score))  # Clamp between 1 and 10
    except Exception as e:
        return 5.0  # Default score if calculation fails

@opik.track
def store_humanization_result(collection, original_text, humanized_text, text_type, score, tags):
    """Store the humanization result in Weaviate"""

    data = {
        "original_text": original_text,
        "humanized_text": humanized_text,
        "text_type": text_type,
        "user_id": "current_user",  # You could make this dynamic
        "timestamp": datetime.now().isoformat(),
        "humanization_score": score,
        "tags": tags
    }

    try:
        collection.data.insert(properties=data)
        print("💾 Humanization result saved to database!")
        return True
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return False

@opik.track(name="humanize-text-pipeline")
def humanize_text(text, text_type="general", tags=None):
    """Main function to humanize text with full pipeline"""

    if tags is None:
        tags = ["humanization"]

    print(f"🤖 Starting humanization process...")
    print(f"📝 Original text: {text[:100]}...")

    # Find similar examples
    examples = find_similar_humanizations(text, humanizer_collection)
    print(f"🔍 Found {len(examples)} similar examples")

    # Humanize the text
    humanized = call_humanizer_llm(text, examples)
    print(f"✨ Humanized text: {humanized[:100]}...")

    # Calculate score
    score = calculate_humanization_score(text, humanized)
    print(f"📊 Humanization score: {score}/10")

    # Store result
    store_humanization_result(
        humanizer_collection, text, humanized, text_type, score, tags
    )

    return {
        "original": text,
        "humanized": humanized,
        "score": score,
        "examples_used": len(examples)
    }

def main():
    """Interactive humanizer"""
    global humanizer_collection

    print("🤖➡️👤 AI Text Humanizer")
    print("=" * 50)
    print("Transform robotic text into human-friendly content!")
    print("All results are stored in Weaviate and tracked with Opik.\n")

    # Setup collection
    humanizer_collection = setup_humanizer_collection()
    if not humanizer_collection:
        print("❌ Failed to setup collection. Exiting.")
        return

    while True:
        print("\nWhat would you like to do?")
        print("1. Humanize new text")
        print("2. View previous humanizations")
        print("3. Add sample robotic text to database")
        print("4. Quit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            text = input("\n📝 Enter the text to humanize:\n> ").strip()
            if text:
                text_type = input("Text type (email/technical/marketing/general): ").strip() or "general"
                tags_input = input("Tags (comma-separated, optional): ").strip()
                tags = [t.strip() for t in tags_input.split(",")] if tags_input else ["humanization"]

                print(f"\n🚀 Processing...")
                result = humanize_text(text, text_type, tags)

                print(f"\n" + "="*60)
                print(f"📋 RESULTS:")
                print(f"🤖 Original: {result['original']}")
                print(f"👤 Humanized: {result['humanized']}")
                print(f"📊 Score: {result['score']}/10")
                print(f"💡 Examples used: {result['examples_used']}")
                print(f"="*60)

        elif choice == "2":
            print(f"\n📚 Recent Humanizations:")
            try:
                results = humanizer_collection.query.fetch_objects(limit=5)
                for i, obj in enumerate(results.objects, 1):
                    props = obj.properties
                    print(f"\n{i}. [{props['text_type']}] Score: {props['humanization_score']}/10")
                    print(f"   Original: {props['original_text'][:80]}...")
                    print(f"   Humanized: {props['humanized_text'][:80]}...")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            print(f"\n🤖 Add some robotic text examples!")
            robotic_examples = [
                "We regret to inform you that your application has been unsuccessful at this time.",
                "Please find attached the documentation as per your request submitted on the aforementioned date.",
                "The system will undergo scheduled maintenance during which services may be temporarily unavailable.",
                "Your inquiry has been forwarded to the appropriate department for further processing.",
                "We acknowledge receipt of your communication and will respond accordingly.",
            ]

            print("Here are some robotic examples you can try:")
            for i, example in enumerate(robotic_examples, 1):
                print(f"{i}. {example}")

        elif choice == "4":
            break
        else:
            print("❌ Invalid choice")

    # Cleanup
    weaviate_client.close()
    print(f"\n✅ Thanks for using the AI Humanizer!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n✅ Goodbye!")
        weaviate_client.close()
