from typing import List, Dict

# In-memory storage (use Redis for production)
conversation_memory: Dict[str, List[Dict]] = {}


def add_memory(role: str, content: str, session_id: str = "default"):
    """Add message to conversation memory."""
    
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    
    conversation_memory[session_id].append({
        "role": role,
        "content": content
    })
    
    # Keep only last 20 messages
    if len(conversation_memory[session_id]) > 20:
        conversation_memory[session_id] = conversation_memory[session_id][-20:]


def get_memory(session_id: str = "default") -> List[Dict]:
    """Get conversation history."""
    return conversation_memory.get(session_id, [])


def clear_memory(session_id: str = "default"):
    """Clear conversation history."""
    if session_id in conversation_memory:
        conversation_memory[session_id] = []