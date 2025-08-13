#!/usr/bin/env python3
"""
Explore Weaviate Database Contents
This script helps you see what's actually stored in your Weaviate database.
"""

import os
import weaviate
from weaviate.classes.init import Auth

# Connect to Weaviate
WEAVIATE_CLUSTER_URL = os.getenv('WEAVIATE_CLUSTER_URL') or 'https://4oreows2qroxgn0tjgj2uq.c0.us-west3.gcp.weaviate.cloud'
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY') or 'aVcyNUdKT2d3WHMxcHFzYl9CL3haUXVkajhzSWtzRmFFamRWa0dOSjZEVGR1SVBWNTYzT21iSkVVeWJVPV92MjAw'

print("🔌 Connecting to Weaviate...")
weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_CLUSTER_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
)

print(f"✅ Connected: {weaviate_client.is_connected()}")

try:
    # List all collections
    print("\n📋 Available Collections:")
    collections = weaviate_client.collections.list_all()
    for collection_name in collections:
        print(f"  - {collection_name}")

    if "BookRecs" in collections:
        book_collection = weaviate_client.collections.get("BookRecs")

        # Get collection info
        print(f"\n📊 BookRecs Collection Info:")
        collection_config = book_collection.config.get()
        print(f"  - Name: {collection_config.name}")
        print(f"  - Vector Index Type: {collection_config.vector_index_type}")

        # Show properties/schema
        print(f"\n📝 Schema Properties:")
        for prop in collection_config.properties:
            print(f"  - {prop.name}: {prop.data_type}")

        # Count objects
        total_count = book_collection.aggregate.over_all(total_count=True)
        print(f"\n📈 Total Objects: {total_count.total_count}")

        # Get all books with their data
        print(f"\n📚 All Books in Database:")
        response = book_collection.query.fetch_objects(limit=50)

        for i, book in enumerate(response.objects, 1):
            props = book.properties
            print(f"\n  📖 Book #{i}:")
            print(f"     Title: {props.get('title', 'N/A')}")
            print(f"     Author: {props.get('author', 'N/A')}")
            print(f"     Genre: {props.get('genre', 'N/A')}")
            print(f"     Year: {props.get('year', 'N/A')}")
            print(f"     Description: {props.get('description', 'N/A')[:100]}...")

        # Test different search methods
        print(f"\n🔍 Testing Search Methods:")

        # BM25 Search
        print(f"\n  🔤 BM25 Search for 'science fiction':")
        try:
            bm25_results = book_collection.query.bm25(query="science fiction", limit=3)
            for book in bm25_results.objects:
                print(f"    - {book.properties['title']} by {book.properties['author']}")
        except Exception as e:
            print(f"    ❌ BM25 failed: {e}")

        # Keyword search
        print(f"\n  🔎 Keyword Search for titles containing 'Lord':")
        try:
            keyword_results = book_collection.query.where(
                weaviate.classes.query.Filter.by_property("title").contains_any(["Lord", "Hobbit"])
            ).fetch_objects(limit=5)
            for book in keyword_results.objects:
                print(f"    - {book.properties['title']} by {book.properties['author']}")
        except Exception as e:
            print(f"    ❌ Keyword search failed: {e}")

        # Try to see if we can do vector search
        print(f"\n  🧠 Vector Search Test:")
        try:
            vector_results = book_collection.query.near_text(
                query="space adventure",
                limit=3
            )
            print("    ✅ Vector search works!")
            for book in vector_results.objects:
                print(f"    - {book.properties['title']} by {book.properties['author']}")
        except Exception as e:
            print(f"    ❌ Vector search failed: {e}")

    else:
        print("❌ BookRecs collection not found!")

except Exception as e:
    print(f"❌ Error exploring database: {e}")

finally:
    # Clean up
    weaviate_client.close()
    print(f"\n✅ Connection closed")
