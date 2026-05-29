from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from backend.rag import retrieve_scripture
from backend.moderation import moderate_input, moderate_image_prompt
from backend.memory import add_memory, get_memory, clear_memory
from backend.denomination import detect_denomination
from backend.llm import generate_grounded_response
from backend.image_gen import generate_christian_image

app = FastAPI(title="Christian AI Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ImageRequest(BaseModel):
    prompt: str


@app.post("/chat")
def chat(req: ChatRequest):
    """
    Main chat endpoint with full grounding and safety.
    """
    
    user_input = req.message
    
    # 1. Input moderation
    moderation = moderate_input(user_input)
    if not moderation["safe"]:
        return {
            "response": moderation["message"],
            "citations": [],
            "denomination": "Unknown",
            "safe": False
        }
    
    # 2. Retrieve relevant scripture
    scripture_context = retrieve_scripture(user_input, k=5)
    
    if not scripture_context:
        return {
            "response": "I couldn't find relevant scripture for your question. Could you rephrase it?",
            "citations": [],
            "denomination": "general",
            "safe": True
        }
    
    # 3. Detect denomination
    denomination = detect_denomination(user_input)
    
    # 4. Get conversation history
    history = get_memory()
    
    # 5. Generate grounded response
    result = generate_grounded_response(
        user_query=user_input,
        scripture_context=scripture_context,
        conversation_history=history,
        denomination=denomination
    )
    
    # 6. Save to memory
    add_memory("user", user_input)
    add_memory("assistant", result["response"])
    
    # 7. Return response
    return {
        "response": result["response"],
        "citations": result["citations"],
        "scripture_context": result["scripture_used"],
        "denomination": denomination,
        "safe": True
    }


@app.post("/generate-image")
def generate_image(req: ImageRequest):
    """Generate Christian-themed image."""
    
    result = generate_christian_image(req.prompt)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Return whatever format your image_gen uses
    return result  # Contains image_url OR image_base64


@app.post("/clear-memory")
def clear_conversation():
    """Clear conversation memory."""
    clear_memory()
    return {"message": "Memory cleared"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)