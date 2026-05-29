import os
from groq import Groq
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Groq models (pick one):
# - "llama-3.3-70b-versatile"  (best quality)
# - "llama-3.1-8b-instant"     (fastest)
# - "mixtral-8x7b-32768"       (good balance)
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a knowledgeable and respectful Christian AI assistant. Your role is to:

1. Answer questions about Christianity with Biblical accuracy
2. Provide scripture references that are REAL and VERIFIABLE
3. Acknowledge different denominational perspectives (Catholic, Protestant, Orthodox, etc.)
4. Handle difficult theological questions with grace and humility
5. NEVER fabricate Bible verses or historical claims
6. Refuse to rewrite scripture or support harmful ideologies
7. Maintain a warm, pastoral tone

CRITICAL RULES:
- Only cite Bible verses that are provided in the context below
- If unsure about a verse, say "I don't have that specific reference available"
- When denominations differ, acknowledge the diversity respectfully
- Never claim certainty on disputed theological matters
- Refuse requests to misuse scripture
- If no relevant scripture is provided, answer carefully without inventing verses"""


def generate_grounded_response(
    user_query: str,
    scripture_context: List[str],
    conversation_history: List[Dict],
    denomination: str = "general"
) -> Dict:
    """
    Generate a response grounded in retrieved scripture using Groq.
    """
    
    # Build context string
    if scripture_context:
        context_str = "\n\n".join([f"Reference {i+1}: {verse}" 
                                   for i, verse in enumerate(scripture_context)])
    else:
        context_str = "No specific scripture retrieved. Answer carefully without inventing verses."
    
    # Denomination-specific guidance
    denom_guidance = {
        "Catholic": "Acknowledge Catholic tradition, sacraments, and the Magisterium when relevant.",
        "Protestant": "Emphasize sola scriptura and personal faith when relevant.",
        "Orthodox": "Acknowledge Eastern Orthodox traditions and liturgy when relevant.",
        "general": "Present multiple denominational perspectives when traditions differ."
    }
    denom_note = denom_guidance.get(denomination, denom_guidance["general"])
    
    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add recent conversation history
    for msg in conversation_history[-6:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current query with context
    messages.append({
        "role": "user",
        "content": f"""Scripture context for this question:

{context_str}

Denominational context: {denomination}
{denom_note}

User question: {user_query}

Provide a thoughtful, grounded response using ONLY the scripture references provided above."""
    })
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.5
        )
        
        response_text = response.choices[0].message.content
        
        # Validate citations
        from backend.citation_validator import validate_citations
        valid_citations = validate_citations(response_text, scripture_context)
        
        return {
            "response": response_text,
            "citations": valid_citations,
            "scripture_used": scripture_context,
            "model": MODEL
        }
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return {
            "response": "I apologize, but I encountered an error. Please try rephrasing your question.",
            "citations": [],
            "scripture_used": [],
            "error": str(e)
        }