import os
import requests
from typing import Dict
from dotenv import load_dotenv
from backend.moderation import moderate_image_prompt

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Free at huggingface.co
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


def generate_christian_image(prompt: str) -> Dict:
    """Generate Christian image using Hugging Face (free)."""
    
    # Moderate prompt
    moderation = moderate_image_prompt(prompt)
    if not moderation["safe"]:
        return {"success": False, "error": moderation["message"]}
    
    safe_prompt = f"Christian biblical artwork, Renaissance style: {prompt}. Peaceful, reverent, respectful religious imagery."
    
    try:
        response = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": safe_prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            # Save image and return path
            import base64
            image_bytes = response.content
            
            # Save to file
            os.makedirs("generated_images", exist_ok=True)
            filename = f"generated_images/image_{hash(prompt) % 10000}.png"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            
            # Return base64 for Streamlit
            b64 = base64.b64encode(image_bytes).decode()
            return {
                "success": True,
                "image_base64": b64,
                "image_path": filename
            }
        else:
            return {"success": False, "error": f"HF API error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": f"Image generation failed: {str(e)}"}