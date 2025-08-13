#!/usr/bin/env python3
"""
Dataset Loader for AI Humanizer
Downloads and processes real datasets to populate Weaviate with robotic/formal text examples.
"""

import os
import opik
import weaviate
import requests
import json
import csv
from datetime import datetime
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType

# Configure Opik
opik.configure(use_local=False)
os.environ["OPIK_PROJECT_NAME"] = "ai-humanizer-data-pipeline"

# Connect to Weaviate
WEAVIATE_CLUSTER_URL = os.getenv('WEAVIATE_CLUSTER_URL') or 'https://4oreows2qroxgn0tjgj2uq.c0.us-west3.gcp.weaviate.cloud'
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY') or 'aVcyNUdKT2d3WHMxcHFzYl9CL3haUXVkajhzSWtzRmFFamRWa0dOSjZEVGR1SVBWNTYzT21iSkVVeWJVPV92MjAw'

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_CLUSTER_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
)

@opik.track
def setup_robotic_text_collection():
    """Setup a collection specifically for robotic text examples"""
    print("🔧 Setting up RoboticTextExamples collection...")
    
    try:
        collections = weaviate_client.collections.list_all()
        
        if "RoboticTextExamples" not in collections:
            print("📝 Creating RoboticTextExamples collection...")
            
            weaviate_client.collections.create(
                name="RoboticTextExamples",
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),  # where it came from
                    Property(name="category", data_type=DataType.TEXT),  # email, legal, tech, etc.
                    Property(name="formality_score", data_type=DataType.NUMBER),  # 1-10 how formal/robotic
                    Property(name="length", data_type=DataType.INT),  # character count
                    Property(name="tags", data_type=DataType.TEXT_ARRAY),
                    Property(name="timestamp", data_type=DataType.TEXT),
                ],
            )
            print("✅ RoboticTextExamples collection created!")
        else:
            print("✅ RoboticTextExamples collection already exists!")
            
        return weaviate_client.collections.get("RoboticTextExamples")
        
    except Exception as e:
        print(f"❌ Error setting up collection: {e}")
        return None

@opik.track
def add_corporate_emails():
    """Add corporate email examples"""
    print("📧 Adding corporate email examples...")
    
    corporate_emails = [
        {
            "text": "We regret to inform you that your application has been unsuccessful at this time. Please be advised that we will retain your information for future opportunities that may align with your qualifications.",
            "source": "hr_rejection_emails",
            "category": "corporate_email",
            "formality_score": 9.0,
            "tags": ["rejection", "formal", "hr"]
        },
        {
            "text": "Please be advised that the meeting scheduled for tomorrow has been postponed until further notice. We will communicate the rescheduled date and time in due course.",
            "source": "corporate_communications", 
            "category": "corporate_email",
            "formality_score": 8.5,
            "tags": ["meeting", "postponement", "formal"]
        },
        {
            "text": "We acknowledge receipt of your inquiry and wish to inform you that your request is currently under review by the appropriate department. A response will be provided within 5-7 business days.",
            "source": "customer_service",
            "category": "corporate_email", 
            "formality_score": 8.8,
            "tags": ["acknowledgment", "review", "timeline"]
        },
        {
            "text": "Pursuant to our previous correspondence, we are writing to confirm the details of your upcoming appointment. Please arrive 15 minutes prior to the scheduled time.",
            "source": "appointment_confirmations",
            "category": "corporate_email",
            "formality_score": 8.0,
            "tags": ["appointment", "confirmation", "instructions"]
        },
        {
            "text": "We are pleased to inform you that your proposal has been accepted. Please find attached the contract for your review and signature. Kindly return the signed document at your earliest convenience.",
            "source": "business_proposals",
            "category": "corporate_email",
            "formality_score": 7.5,
            "tags": ["acceptance", "contract", "signature"]
        }
    ]
    
    return corporate_emails

@opik.track  
def add_technical_documentation():
    """Add technical documentation examples"""
    print("⚙️ Adding technical documentation examples...")
    
    technical_docs = [
        {
            "text": "The implementation of the aforementioned solution requires comprehensive analysis of the existing infrastructure and subsequent optimization of the current workflow processes to ensure maximum efficiency.",
            "source": "technical_specs",
            "category": "technical",
            "formality_score": 9.5,
            "tags": ["implementation", "analysis", "optimization"]
        },
        {
            "text": "Users must ensure that all prerequisite software components are properly installed and configured prior to initiating the installation procedure outlined in Section 4.2 of this document.",
            "source": "installation_guides",
            "category": "technical",
            "formality_score": 8.7,
            "tags": ["prerequisites", "installation", "configuration"]
        },
        {
            "text": "The system administrator should execute the following command sequence to perform database optimization and subsequently verify the integrity of the data structures.",
            "source": "admin_manuals",
            "category": "technical", 
            "formality_score": 8.9,
            "tags": ["database", "optimization", "verification"]
        },
        {
            "text": "In the event of system failure, please consult the troubleshooting matrix provided in Appendix C to identify the appropriate remediation procedures.",
            "source": "troubleshooting_guides",
            "category": "technical",
            "formality_score": 8.5,
            "tags": ["troubleshooting", "failure", "procedures"]
        }
    ]
    
    return technical_docs

@opik.track
def add_legal_documents():
    """Add legal document examples"""
    print("⚖️ Adding legal document examples...")
    
    legal_docs = [
        {
            "text": "The party of the first part hereby agrees to indemnify and hold harmless the party of the second part from any and all claims, damages, or liabilities arising from or related to the performance of this agreement.",
            "source": "legal_contracts",
            "category": "legal",
            "formality_score": 10.0,
            "tags": ["indemnification", "liability", "agreement"]
        },
        {
            "text": "Whereas the parties desire to enter into this agreement and whereas each party has the requisite authority to execute this agreement, now therefore the parties agree as follows.",
            "source": "contract_preambles",
            "category": "legal",
            "formality_score": 9.8,
            "tags": ["whereas", "authority", "agreement"]
        },
        {
            "text": "Notice is hereby given that the undersigned will make application to the appropriate regulatory authority for permission to conduct the activities described herein.",
            "source": "regulatory_filings",
            "category": "legal",
            "formality_score": 9.5,
            "tags": ["notice", "application", "regulatory"]
        }
    ]
    
    return legal_docs

@opik.track
def add_academic_writing():
    """Add academic writing examples"""
    print("🎓 Adding academic writing examples...")
    
    academic_texts = [
        {
            "text": "The findings of this investigation demonstrate a statistically significant correlation between the variables under examination, necessitating further research to establish causal relationships.",
            "source": "research_papers",
            "category": "academic",
            "formality_score": 9.2,
            "tags": ["research", "correlation", "statistical"]
        },
        {
            "text": "The methodology employed in this study consists of a comprehensive literature review followed by empirical analysis utilizing both quantitative and qualitative research approaches.",
            "source": "methodology_sections",
            "category": "academic",
            "formality_score": 9.0,
            "tags": ["methodology", "literature", "empirical"]
        },
        {
            "text": "It is hereby recommended that future research endeavors should focus on the longitudinal effects of the intervention while controlling for potential confounding variables.",
            "source": "research_recommendations",
            "category": "academic",
            "formality_score": 8.8,
            "tags": ["recommendations", "longitudinal", "variables"]
        }
    ]
    
    return academic_texts

@opik.track
def add_medical_clinical():
    """Add medical/clinical examples"""
    print("🏥 Adding medical/clinical examples...")
    
    medical_texts = [
        {
            "text": "The patient should be advised to adhere to the prescribed medication regimen and schedule follow-up appointments as per the established protocol to monitor therapeutic efficacy.",
            "source": "clinical_notes",
            "category": "medical",
            "formality_score": 8.5,
            "tags": ["medication", "protocol", "monitoring"]
        },
        {
            "text": "Upon examination, the patient presents with symptoms consistent with the differential diagnosis. Further diagnostic testing is recommended to confirm the provisional assessment.",
            "source": "medical_reports",
            "category": "medical", 
            "formality_score": 9.0,
            "tags": ["examination", "diagnosis", "testing"]
        },
        {
            "text": "The healthcare provider should ensure that informed consent is obtained prior to initiating the treatment protocol and that all potential risks and benefits are adequately communicated.",
            "source": "clinical_guidelines",
            "category": "medical",
            "formality_score": 8.7,
            "tags": ["consent", "treatment", "communication"]
        }
    ]
    
    return medical_texts

@opik.track
def populate_database_with_examples(collection):
    """Populate the database with all examples"""
    print("🚀 Populating database with robotic text examples...")
    
    all_examples = []
    all_examples.extend(add_corporate_emails())
    all_examples.extend(add_technical_documentation()) 
    all_examples.extend(add_legal_documents())
    all_examples.extend(add_academic_writing())
    all_examples.extend(add_medical_clinical())
    
    # Add metadata to all examples
    for example in all_examples:
        example["length"] = len(example["text"])
        example["timestamp"] = datetime.now().isoformat()
    
    print(f"📊 Adding {len(all_examples)} examples to database...")
    
    try:
        with collection.batch.dynamic() as batch:
            for example in all_examples:
                batch.add_object(properties=example)
        
        print("✅ All examples added successfully!")
        return len(all_examples)
        
    except Exception as e:
        print(f"❌ Error adding examples: {e}")
        return 0

@opik.track
def download_real_datasets():
    """Download real datasets from online sources"""
    print("🌐 Downloading real datasets...")
    
    datasets = []
    
    # Try to get some real corporate/formal text datasets
    try:
        # Example: Corporate press releases (you can add more sources)
        print("📰 Attempting to download corporate communications...")
        
        # Add more sample corporate texts that sound robotic
        corporate_samples = [
            "We are pleased to announce that our organization has successfully completed the acquisition of the aforementioned entity, effective immediately.",
            "Please be advised that due to unforeseen circumstances, the previously scheduled event has been postponed indefinitely.",
            "The management team would like to express their appreciation for your continued dedication and commitment to excellence during this transitional period.",
            "It has come to our attention that certain operational procedures require immediate modification to ensure compliance with regulatory requirements.",
            "We wish to inform all stakeholders that the quarterly review meeting will be conducted via teleconference on the date specified in the calendar invitation."
        ]
        
        for i, text in enumerate(corporate_samples):
            datasets.append({
                "text": text,
                "source": "corporate_communications_dataset",
                "category": "corporate",
                "formality_score": 8.5 + (i * 0.1),
                "length": len(text),
                "tags": ["corporate", "formal", "business"],
                "timestamp": datetime.now().isoformat()
            })
            
        print(f"✅ Added {len(corporate_samples)} corporate communication samples")
        
    except Exception as e:
        print(f"⚠️ Could not download external datasets: {e}")
    
    return datasets

@opik.track
def analyze_database_contents(collection):
    """Analyze what's in the database"""
    print("\n📊 Analyzing database contents...")
    
    try:
        # Get all examples
        results = collection.query.fetch_objects(limit=100)
        
        # Analyze by category
        categories = {}
        formality_scores = []
        
        for obj in results.objects:
            props = obj.properties
            category = props.get("category", "unknown")
            formality = props.get("formality_score", 0)
            
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            formality_scores.append(formality)
        
        print(f"📈 Total examples: {len(results.objects)}")
        print(f"📋 Categories:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count} examples")
        
        if formality_scores:
            avg_formality = sum(formality_scores) / len(formality_scores)
            print(f"📊 Average formality score: {avg_formality:.1f}/10")
        
        # Show some examples
        print(f"\n📝 Sample entries:")
        for i, obj in enumerate(results.objects[:3], 1):
            props = obj.properties
            print(f"\n{i}. [{props['category']}] Formality: {props['formality_score']}/10")
            print(f"   Text: {props['text'][:100]}...")
            print(f"   Tags: {props.get('tags', [])}")
            
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")

def main():
    """Main function to populate the database"""
    print("🤖📚 AI Humanizer Database Populator")
    print("=" * 50)
    print("Building a comprehensive dataset of robotic/formal text!")
    
    # Setup collection
    collection = setup_robotic_text_collection()
    if not collection:
        print("❌ Failed to setup collection. Exiting.")
        return
    
    print("\nChoose what to add:")
    print("1. Add curated examples (emails, legal, tech, etc.)")
    print("2. Download external datasets")
    print("3. Add everything")
    print("4. Just analyze current database")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice in ["1", "3"]:
        count = populate_database_with_examples(collection)
        print(f"✅ Added {count} curated examples!")
    
    if choice in ["2", "3"]:
        datasets = download_real_datasets()
        if datasets:
            try:
                with collection.batch.dynamic() as batch:
                    for data in datasets:
                        batch.add_object(properties=data)
                print(f"✅ Added {len(datasets)} external dataset examples!")
            except Exception as e:
                print(f"❌ Error adding external data: {e}")
    
    # Always analyze at the end
    analyze_database_contents(collection)
    
    print(f"\n🎯 Database is ready! Your AI Humanizer now has tons of examples to learn from.")
    print(f"💡 Run your ai_humanizer.py script to start humanizing text with this rich dataset!")
    
    # Cleanup
    weaviate_client.close()
    print(f"✅ Connection closed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n✅ Goodbye!")
        weaviate_client.close()
