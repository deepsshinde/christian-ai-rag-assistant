import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Load local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = chroma_client.get_collection("bible")
except:
    collection = chroma_client.create_collection(
        name="bible",
        metadata={"description": "Bible verses for RAG"}
    )


def retrieve_scripture(query: str, k: int = 5) -> List[str]:
    """
    Retrieve relevant scripture using semantic search.
    """
    try:
        # Generate embedding for query
        embedding = model.encode(query).tolist()
        
        # Query vector database
        results = collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        
        if results and results["documents"]:
            return results["documents"][0]
        else:
            return []
            
    except Exception as e:
        print(f"RAG error: {e}")
        return []


def add_scripture_to_db(verses: List[Dict[str, str]]):
    """
    Add Bible verses to vector database.
    verses: [{"id": "John 3:16", "text": "For God so loved..."}]
    """
    try:
        ids = [v["id"] for v in verses]
        texts = [v["text"] for v in verses]
        embeddings = [model.encode(text).tolist() for text in texts]
        
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings
        )
        
        print(f"Added {len(verses)} verses to database")
        
    except Exception as e:
        print(f"Error adding to DB: {e}")