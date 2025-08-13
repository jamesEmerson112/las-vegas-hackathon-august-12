#!/usr/bin/env python3
"""
Interactive Weaviate Query Tool
Run this to search your book database interactively.
"""

import os
import weaviate
from weaviate.classes.init import Auth

# Connect to Weaviate
WEAVIATE_CLUSTER_URL = os.getenv('WEAVIATE_CLUSTER_URL') or 'https://4oreows2qroxgn0tjgj2uq.c0.us-west3.gcp.weaviate.cloud'
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY') or 'aVcyNUdKT2d3WHMxcHFzYl9CL3haUXVkajhzSWtzRmFFamRWa0dOSjZEVGR1SVBWNTYzT21iSkVVeWJVPV92MjAw'

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_CLUSTER_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
)

book_collection = weaviate_client.collections.get("BookRecs")

def search_books(query, limit=5):
    """Search books using BM25 search"""
    print(f"\n🔍 Searching for: '{query}'")
    try:
        results = book_collection.query.bm25(query=query, limit=limit)
        if results.objects:
            print(f"📚 Found {len(results.objects)} books:")
            for i, book in enumerate(results.objects, 1):
                props = book.properties
                print(f"\n  {i}. {props['title']} ({props['year']})")
                print(f"     Author: {props['author']}")
                print(f"     Genre: {props['genre']}")
                print(f"     Description: {props['description'][:100]}...")
        else:
            print("❌ No books found")
    except Exception as e:
        print(f"❌ Search failed: {e}")

def get_books_by_genre(genre):
    """Get all books of a specific genre"""
    print(f"\n📖 Books in '{genre}' genre:")
    try:
        results = book_collection.query.fetch_objects(limit=20)
        found = False
        for book in results.objects:
            if genre.lower() in book.properties['genre'].lower():
                props = book.properties
                print(f"  - {props['title']} by {props['author']} ({props['year']})")
                found = True
        if not found:
            print(f"❌ No books found in '{genre}' genre")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_all_books():
    """Show all books in the database"""
    print(f"\n📚 All Books in Database:")
    try:
        results = book_collection.query.fetch_objects(limit=50)
        for i, book in enumerate(results.objects, 1):
            props = book.properties
            print(f"  {i}. {props['title']} by {props['author']} ({props['year']}) - {props['genre']}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🎯 Interactive Weaviate Book Database Explorer")
    print("=" * 50)

    while True:
        print(f"\nWhat would you like to do?")
        print("1. Search books")
        print("2. Show books by genre")
        print("3. Show all books")
        print("4. Quit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            query = input("Enter search query: ").strip()
            if query:
                search_books(query)
        elif choice == "2":
            genre = input("Enter genre (e.g., Fantasy, Science Fiction): ").strip()
            if genre:
                get_books_by_genre(genre)
        elif choice == "3":
            show_all_books()
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice")

    weaviate_client.close()
    print("\n✅ Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Goodbye!")
        weaviate_client.close()
