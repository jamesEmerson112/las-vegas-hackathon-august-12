#!/usr/bin/env python3
"""
🎭 QUICK DEMO SCRIPT
Run this for a live demo of the AI Humanizer system!
"""

import os
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_step(step_num, title):
    print(f"\n🔸 Step {step_num}: {title}")
    print("-" * 40)

def demo_examples():
    """Show some great examples for the demo"""

    examples = [
        {
            "category": "💼 Corporate Email",
            "robotic": "We regret to inform you that your application has been unsuccessful at this time. Please be advised that we will retain your information for future opportunities that may align with your qualifications.",
            "human": "Thanks for applying! Unfortunately, we won't be moving forward with your application right now, but we'll keep your info on file for future openings."
        },
        {
            "category": "⚙️ Technical Documentation",
            "robotic": "The implementation of the aforementioned solution requires comprehensive analysis of the existing infrastructure and subsequent optimization of the current workflow processes to ensure maximum efficiency.",
            "human": "To get this working, we need to take a look at what we have now and figure out how to make our processes better."
        },
        {
            "category": "⚖️ Legal/Formal",
            "robotic": "Pursuant to our previous correspondence, kindly note that the scheduled maintenance window has been rescheduled to accommodate operational requirements and minimize impact on end-user accessibility.",
            "human": "Just a quick update - we had to move the maintenance time to work better with our schedule and minimize downtime for users."
        },
        {
            "category": "🏥 Medical/Clinical",
            "robotic": "The patient should be advised to adhere to the prescribed medication regimen and schedule follow-up appointments as per the established protocol to monitor therapeutic efficacy and potential adverse reactions.",
            "human": "Make sure to take your medication as prescribed and come back for check-ups so we can see how you're doing and watch for any side effects."
        },
        {
            "category": "🏛️ Government/Policy",
            "robotic": "All personnel are hereby directed to comply with the updated security protocols as outlined in Policy Document 2024-001, effective immediately upon distribution of this memorandum.",
            "human": "Everyone needs to follow the new security rules starting today. Check out Policy Document 2024-001 for the details."
        }
    ]

    print_header("DEMO EXAMPLES - Before & After")

    for i, example in enumerate(examples, 1):
        print(f"\n🎭 Example {i}: {example['category']}")
        print(f"\n🤖 ROBOTIC:")
        print(f'   "{example["robotic"]}"')
        print(f"\n👤 HUMANIZED:")
        print(f'   "{example["human"]}"')

        if i < len(examples):
            input("\n   Press Enter for next example...")

def demo_instructions():
    """Show demo instructions"""

    print_header("🎮 LIVE DEMO INSTRUCTIONS")

    print_step(1, "Show the Problem")
    print("   • Open a corporate email or formal document")
    print("   • Point out how robotic and unfriendly it sounds")
    print("   • 'Nobody actually talks like this!'")

    print_step(2, "Run the System Test")
    print("   • Run: python test_system.py")
    print("   • Show the complete pipeline working")
    print("   • Highlight the RAG approach finding similar examples")

    print_step(3, "Interactive Demo")
    print("   • Run: python ai_humanizer.py")
    print("   • Choose option 1: 'Humanize new text'")
    print("   • Paste one of the robotic examples")
    print("   • Show the dramatically improved result")

    print_step(4, "Show the Intelligence")
    print("   • Open Weaviate console")
    print("   • Show 23+ robotic examples in database")
    print("   • Explain how RAG improves results")

    print_step(5, "Show Observability")
    print("   • Open Opik dashboard")
    print("   • Show complete traces and monitoring")
    print("   • Highlight production-ready observability")

def demo_commands():
    """Show all the commands needed for demo"""

    print_header("📋 DEMO COMMAND CHECKLIST")

    commands = [
        ("🔧 Setup (one-time)", [
            "python download_datasets.py",
            "python dataset_loader.py  # Choose option 3",
        ]),
        ("🧪 System Test", [
            "python test_system.py",
        ]),
        ("🎮 Interactive Demo", [
            "python ai_humanizer.py",
            "# Choose option 1, paste robotic text",
        ]),
        ("🔍 Explore Data", [
            "python explore_weaviate.py",
            "python interactive_query.py",
        ])
    ]

    for category, cmds in commands:
        print(f"\n{category}:")
        for cmd in cmds:
            print(f"   {cmd}")

def demo_talking_points():
    """Show key talking points for the demo"""

    print_header("🎙️ KEY TALKING POINTS")

    points = [
        "🎯 Problem: Corporate/formal text sounds robotic and unfriendly",
        "🧠 Solution: AI-powered humanization with RAG for context",
        "🗄️ Intelligence: 23+ examples help improve results",
        "📊 Observability: Complete pipeline tracking with Opik",
        "🚀 Scalable: Ready for production with proper monitoring",
        "🔧 Technologies: Weaviate + Ollama + Opik = powerful combo",
        "💡 Use Cases: Customer service, technical docs, corporate comms",
        "📈 Impact: Better user experience, higher engagement"
    ]

    for point in points:
        print(f"\n   {point}")

def main():
    """Main demo script"""

    print_header("🎭 AI HUMANIZER DEMO GUIDE")
    print("Welcome to the complete demo guide!")
    print("This will help you run an amazing live demonstration.")

    while True:
        print(f"\n🎮 What would you like to see?")
        print("1. 📝 Demo Examples (Before & After)")
        print("2. 🎯 Demo Instructions")
        print("3. 📋 Command Checklist")
        print("4. 🎙️ Talking Points")
        print("5. 🚀 Run Live System Test")
        print("6. 🎮 Start Interactive Humanizer")
        print("7. ❌ Exit")

        choice = input("\nEnter choice (1-7): ").strip()

        if choice == "1":
            demo_examples()
        elif choice == "2":
            demo_instructions()
        elif choice == "3":
            demo_commands()
        elif choice == "4":
            demo_talking_points()
        elif choice == "5":
            print("\n🚀 Running system test...")
            os.system("python test_system.py")
        elif choice == "6":
            print("\n🎮 Starting interactive humanizer...")
            os.system("python ai_humanizer.py")
        elif choice == "7":
            break
        else:
            print("❌ Invalid choice")

    print(f"\n🎉 Thanks for using the AI Humanizer!")
    print(f"💡 Built with Weaviate, Opik, and Ollama")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n✅ Demo ended. Goodbye!")
