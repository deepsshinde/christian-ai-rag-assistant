import json
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection
try:
    collection = chroma_client.create_collection(
        name="bible",
        metadata={"description": "Bible verses"}
    )
except:
    chroma_client.delete_collection("bible")
    collection = chroma_client.create_collection(
        name="bible",
        metadata={"description": "Bible verses"}
    )


def ingest_bible_data(json_path: str = "data/bible.json"):
    """
    Load Bible JSON and ingest into ChromaDB.
    Expected format:
    {
        "verses": [
            {"reference": "John 3:16", "text": "For God so loved the world..."},
            ...
        ]
    }
    """
    
    print(f"Loading Bible data from {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    verses = data.get("verses", [])
    
    if not verses:
        print("No verses found in JSON!")
        return
    
    print(f"Found {len(verses)} verses. Generating embeddings...")
    
    # Process in batches
    batch_size = 100
    
    for i in range(0, len(verses), batch_size):
        batch = verses[i:i+batch_size]
        
        ids = [v["reference"] for v in batch]
        texts = [f"{v['reference']}: {v['text']}" for v in batch]
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=True).tolist()
        
        # Add to ChromaDB
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings
        )
        
        print(f"Ingested batch {i//batch_size + 1}/{(len(verses)-1)//batch_size + 1}")
    
    print(f"✅ Successfully ingested {len(verses)} verses!")


if __name__ == "__main__":
    # You'll need to provide a Bible JSON file
    # Sample format created below
    
    # Create sample data (you'd use a real Bible database)
    sample_verses = {
        "verses": [
            {"reference": "John 3:16", "text": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."},
            {"reference": "Psalm 23:1", "text": "The Lord is my shepherd, I lack nothing."},
            {"reference": "Romans 8:28", "text": "And we know that in all things God works for the good of those who love him, who have been called according to his purpose."},
            # Add more verses...
        ]
    }
    
    import os
    os.makedirs("data", exist_ok=True)
    
    with open("data/bible.json", "w", encoding="utf-8") as f:
        json.dump(sample_verses, f, indent=2)
    
    ingest_bible_data("data/bible.json")