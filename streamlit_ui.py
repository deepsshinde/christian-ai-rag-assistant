import streamlit as st
import requests

st.set_page_config(
    page_title="Christian AI Assistant",
    page_icon="✝️",
    layout="centered"
)

API_BASE = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("✝️ Christian AI Assistant")

# ====== Use RADIO instead of TABS ======
mode = st.radio(
    "Select Mode",
    ["💬 Chat", "🎨 Generate Image"],
    horizontal=True
)

st.divider()

# ====== CHAT MODE ======
if mode == "💬 Chat":
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("citations"):
                st.caption(f"📖 References: {', '.join(msg['citations'])}")
            if msg.get("denomination") and msg["denomination"] != "general":
                st.caption(f"🏛️ Perspective: {msg['denomination']}")
    
    # Chat input (NOW at top level, not in tabs - works!)
    user_input = st.chat_input("Ask a question about Christianity...")
    
    if user_input:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/chat",
                        json={"message": user_input}
                    )
                    data = response.json()
                    
                    st.write(data["response"])
                    
                    if data.get("citations"):
                        st.caption(f"📖 References: {', '.join(data['citations'])}")
                    if data.get("denomination") and data["denomination"] != "general":
                        st.caption(f"🏛️ Perspective: {data['denomination']}")
                    
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["response"],
                        "citations": data.get("citations", []),
                        "denomination": data.get("denomination", "general")
                    })
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# ====== IMAGE MODE ======
elif mode == "🎨 Generate Image":
    
    st.subheader("Generate Christian Imagery")
    
    image_prompt = st.text_area(
        "Describe the image",
        placeholder="e.g., The Good Shepherd tending his flock at sunset",
        height=100
    )
    
    if st.button("🎨 Generate Image", type="primary"):
        if image_prompt:
            with st.spinner("Generating image..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/generate-image",
                        json={"prompt": image_prompt}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Handle URL (Pollinations)
                        if "image_url" in data:
                            st.image(data["image_url"], caption="Generated Christian Artwork")
                        
                        # Handle base64 (Hugging Face)
                        elif "image_base64" in data:
                            import base64
                            img_bytes = base64.b64decode(data["image_base64"])
                            st.image(img_bytes, caption="Generated Christian Artwork")
                    else:
                        st.error(response.json().get("detail", "Generation failed"))
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt")

# ====== SIDEBAR ======
with st.sidebar:
    st.header("About")
    st.info("""
    Christian AI Assistant features:
    - Scripture-grounded responses (RAG)
    - Bible verse citations
    - Denomination awareness
    - Image generation
    - Safety moderation
    """)
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        try:
            requests.post(f"{API_BASE}/clear-memory")
        except:
            pass
        st.rerun()