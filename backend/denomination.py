from typing import Dict
import re

DENOMINATION_KEYWORDS = {
    "Catholic": [
        "catholic", "pope", "vatican", "mass", "eucharist",
        "mary", "saints", "rosary", "confession", "catechism"
    ],
    "Protestant": [
        "protestant", "reformation", "luther", "calvin",
        "sola scriptura", "grace alone", "baptist", "methodist",
        "presbyterian", "pentecostal"
    ],
    "Orthodox": [
        "orthodox", "eastern orthodox", "patriarch",
        "divine liturgy", "icons", "theosis"
    ],
    "general": []
}


def detect_denomination(user_input: str) -> str:
    """
    Detect likely denomination from user query.
    Returns: Catholic, Protestant, Orthodox, or general
    """
    
    lower = user_input.lower()
    
    scores = {denom: 0 for denom in DENOMINATION_KEYWORDS}
    
    for denom, keywords in DENOMINATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower:
                scores[denom] += 1
    
    # Return denomination with highest score, or "general"
    max_denom = max(scores, key=scores.get)
    
    if scores[max_denom] > 0:
        return max_denom
    
    return "general"