# Christian AI Assistant

A production-grade AI assistant for answering Christianity-related questions with Biblical grounding, multi-denomination awareness, and comprehensive safety measures.

## Architecture

### Core Components

1. **RAG System** (ChromaDB + Sentence Transformers)
   - Embeds Bible verses using `all-MiniLM-L6-v2`
   - Retrieves top-K relevant scriptures via semantic search
   - Prevents hallucinated verse citations by grounding every response in retrieved context

2. **LLM Layer** (Groq — `llama-3.3-70b-versatile`)
   - Generates responses grounded in retrieved scripture only
   - Uses carefully engineered system prompts with explicit anti-hallucination rules
   - Validates all citations against the retrieved context before returning

3. **Safety & Moderation** (three-layer pipeline)
   - **Input moderation**: Keyword blocking → regex adversarial patterns → Groq LLM classifier
   - **Image moderation**: Keyword blocklist → Groq LLM classifier for subtle violations
   - Blocks adversarial prompts (e.g. "rewrite Bible to support X ideology")
   - Handles prompt-injection attempts and jailbreak patterns

4. **Denomination Awareness**
   - Keyword-based detector for Catholic / Protestant / Orthodox context
   - Adjusts LLM guidance per denomination (sacraments, sola scriptura, theosis, etc.)
   - Acknowledges theological differences respectfully when traditions conflict

5. **Image Generation** (Hugging Face — `stabilityai/stable-diffusion-xl-base-1.0`)
   - Free tier via HuggingFace Inference API
   - Auto-wraps prompts with "Christian biblical artwork, Renaissance style" framing
   - Two-layer moderation before generation (keyword + LLM)

### Key Design Decisions

#### Why Groq over OpenAI?
- Free-tier friendly with very fast inference (good for demos)
- `llama-3.3-70b-versatile` has strong instruction-following for grounding rules
- `llama-3.1-8b-instant` used for moderation calls — low-latency, low-cost

#### Why ChromaDB?
- Lightweight, persistent, zero-infrastructure vector store
- Easy local development and Docker deployment
- Sufficient performance for Bible-scale data (~31,000 verses)

#### Why HuggingFace SDXL over DALL-E 3?
- Free inference API — no billing setup needed for evaluation
- SDXL produces high-quality religious artwork
- Easy swap to DALL-E 3 by changing `image_gen.py` if needed

#### Hallucination Prevention Strategy
1. System prompt explicitly forbids inventing verses or historical claims
2. Only scripture retrieved from ChromaDB is injected into context
3. `citation_validator.py` cross-checks all citations against the retrieved context
4. `detect_fake_verses()` flags non-canonical book names and impossible chapter/verse numbers
5. If no relevant scripture is retrieved, the model is instructed to say so rather than invent

#### Edge Case Handling
- **Fake / non-existent verses**: Model told to say "I don't have that reference available"
- **Impossible chapter/verse**: Flagged by `detect_fake_verses()` heuristic
- **Theological disputes**: System prompt instructs multi-perspective, humble responses
- **Adversarial prompts**: Regex + LLM moderation → firm refusal with explanation
- **Subtle image policy violations**: LLM image moderator catches what keyword lists miss (e.g. "Jesus holding a sword over enemies")
- **Prompt injection**: LLM moderation layer trained to detect override attempts

## Project Structure

```
christian-ai-assistant/
├── app.py                    # FastAPI backend — main entry point
├── streamlit_ui.py           # Streamlit frontend (chat + image generation)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── backend/
│   ├── llm.py                # Groq LLM with grounded prompting
│   ├── rag.py                # ChromaDB retrieval
│   ├── moderation.py         # 3-layer input + 2-layer image moderation
│   ├── citation_validator.py # Citation cross-check + fake verse detection
│   ├── denomination.py       # Catholic / Protestant / Orthodox detection
│   └── memory.py             # In-memory conversation history (per session)
├── data/
│   ├── fetch_bible.py        # Downloads Bible JSON
│   └── ingest_bible.py       # Embeds and loads verses into ChromaDB
├── tests/
│   ├── test_cases.py         # Core functional test suite (pytest)
│   └── edge_cases.py         # Adversarial, hallucination, and boundary tests
└── chroma_db/                # Persisted vector database (pre-built)
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Fill in:
#   GROQ_API_KEY      — free at console.groq.com
#   HUGGINGFACE_API_KEY — free at huggingface.co

# 3. Ingest Bible data (only needed if chroma_db/ is missing)
python data/ingest_bible.py

# 4. Start backend
python app.py
# or: uvicorn app:app --reload

# 5. Start frontend (separate terminal)
streamlit run streamlit_ui.py
```

### Docker (one command)

```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

## Data Flow

```
User query
  → Input moderation (keyword → regex → LLM)
  → RAG retrieval (ChromaDB semantic search, top-5 verses)
  → Denomination detection
  → LLM generation (Groq, scripture-grounded context)
  → Citation validation (cross-check against retrieved verses)
  → Safe response returned to user
```

## Prompt Engineering Strategy

**System Prompt Design**
- Explicit grounding instruction: "only cite Bible verses provided in context"
- Prohibition on hallucination: "if unsure, say 'I don't have that reference'"
- Denomination guidance injected per request
- Pastoral tone instruction for sensitive questions

**Anti-Hallucination Constraints**
```python
# In llm.py system prompt:
"CRITICAL RULES:
- Only cite Bible verses that are provided in the context below
- If unsure about a verse, say 'I don't have that specific reference available'
- Never claim certainty on disputed theological matters
- Refuse requests to misuse scripture"
```

## Running Tests

```bash
# Core tests (requires running API on localhost:8000)
pytest tests/test_cases.py -v

# Edge cases, adversarial, hallucination tests
pytest tests/edge_cases.py -v

# All tests
pytest tests/ -v
```

## Evaluation Dataset Summary

`tests/edge_cases.py` covers five categories:

| Category | Count | What it tests |
|---|---|---|
| Hallucination | 7 | Fake books, impossible chapter/verse, historical false claims |
| Adversarial | 8 | Ideology injection, jailbreaks, hate wrapped in theology |
| Contradiction | 4 | Trinity paradox, predestination vs free will, OT/NT tension |
| Boundary | 8 | Empty input, Unicode, SQL injection, very long queries |
| Image | 7 | Obvious + subtle policy-violating image prompts |
