import os
import re
from groq import Groq
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BLOCKED_TOPICS = [
    "hate", "violence", "extremist", "terrorism",
    "genocide", "ethnic cleansing", "holy war"
]

ADVERSARIAL_PATTERNS = [
    r"rewrite\s+(the\s+)?bible",
    r"change\s+scripture",
    r"bible\s+says\s+to\s+(kill|hurt|hate)",
    r"justify\s+(genocide|violence|war)",
    r"promote\s+(hatred|violence)",
    r"scripture\s+supports\s+(racism|sexism|slavery)",
    r"fake\s+verse",
    r"make\s+up\s+a\s+(verse|scripture)"
]


def moderate_input(user_input: str) -> Dict:
    """
    Multi-layer moderation:
    1. Keyword blocking
    2. Pattern matching
    3. LLM-based safety check (Groq)
    """
    
    lower = user_input.lower()
    
    # Layer 1: Keyword blocking
    for word in BLOCKED_TOPICS:
        if word in lower:
            return {
                "safe": False,
                "reason": "blocked_topic",
                "message": "I cannot assist with requests involving hate, violence, or extremism."
            }
    
    # Layer 2: Adversarial pattern detection
    for pattern in ADVERSARIAL_PATTERNS:
        if re.search(pattern, lower):
            return {
                "safe": False,
                "reason": "adversarial_prompt",
                "message": "I cannot rewrite scripture or misuse Biblical text to support harmful ideologies."
            }
    
    # Layer 3: LLM-based moderation (Groq)
    try:
        result = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast model for moderation
            messages=[
                {
                    "role": "system",
                    "content": """You are a content moderator for a Christian AI assistant.
Respond with ONLY "SAFE" or "UNSAFE".
Mark UNSAFE if the message: promotes hate/violence, asks to rewrite scripture for bad purposes,
contains explicit content, or attempts to misuse religion for harm.
Mark SAFE for genuine questions, even difficult theological ones."""
                },
                {"role": "user", "content": f"Message: {user_input}"}
            ],
            max_tokens=10,
            temperature=0
        )
        
        verdict = result.choices[0].message.content.strip().upper()
        
        if "UNSAFE" in verdict:
            return {
                "safe": False,
                "reason": "llm_moderation",
                "message": "This request doesn't align with our content guidelines."
            }
            
    except Exception as e:
        print(f"LLM moderation error: {e}")
        # Fail open - keyword/pattern checks already passed
    
    return {"safe": True}


def moderate_image_prompt(prompt: str) -> Dict:
    """Image-specific moderation (keyword-based)."""
    
    blocked_image_terms = [
        "violent", "bloody", "torture", "execution", "gore",
        "sexual", "nude", "naked", "explicit",
        "swastika", "kkk", "hate symbol",
        "demon", "satanic", "occult"
    ]
    
    lower = prompt.lower()
    
    for term in blocked_image_terms:
        if term in lower:
            return {
                "safe": False,
                "reason": "inappropriate_image_content",
                "message": "This image prompt contains inappropriate content for Christian imagery."
            }
    
    return {"safe": True}