# Christian AI Assistant

A production-grade AI assistant for answering Christianity-related questions with Biblical grounding, multi-denomination awareness, and comprehensive safety measures.

## Architecture

### Core Components

1. **RAG System** (ChromaDB + Sentence Transformers)
   - Embeds Bible verses using `all-MiniLM-L6-v2`
   - Retrieves top-K relevant scriptures via semantic search
   - Prevents hallucinated verse citations

2. **LLM Layer** (Claude 3.5 Sonnet)
   - Generates responses grounded in retrieved scripture
   - Uses carefully engineered system prompts
   - Validates citations against provided context

3. **Safety & Moderation**
   - **Input moderation**: Keyword blocking + pattern matching + OpenAI API
   - **Output moderation**: OpenAI moderation API
   - **Image moderation**: Specialized checks for visual content
   - Blocks adversarial prompts (e.g., "rewrite Bible to support X")

4. **Denomination Awareness**
   - Detects Catholic/Protestant/Orthodox context
   - Adjusts tone and references accordingly
   - Acknowledges theological differences respectfully

5. **Image Generation** (DALL-E 3)
   - Generates Christian artwork with safety constraints
   - Auto-enhances prompts for appropriateness
   - Blocks violent/sexual/hateful imagery

### Key Design Decisions

#### Why Claude over GPT-4?
- Better at following instructions ("only cite provided verses")
- Stronger safety alignment
- More nuanced handling of theological complexity

#### Why ChromaDB?
- Lightweight, persistent vector store
- Easy local development
- Good performance for Bible-scale data (~31,000 verses)

#### Hallucination Prevention Strategy
1. System prompt explicitly forbids inventing verses
2. Only scripture from RAG context is provided
3. Citation validator checks all references
4. Fake verse detector flags suspicious patterns

#### Edge Case Handling
- **Fake verses**: "I don't have that specific reference available"
- **Theological disputes**: Acknowledge multiple perspectives
- **Difficult questions**: Respond with pastoral sensitivity
- **Adversarial prompts**: Firm refusal with explanation

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your API keys

# Ingest Bible data
python data/ingest_bible.py

# Run backend
python app.py

# Run frontend (separate terminal)
streamlit run streamlit_ui.py



## Data Flow

1. User query → Input moderation
2. Pass → RAG retrieval (ChromaDB)
3. Query + Scripture → LLM (Claude)
4. Response → Citation validation
5. Response → Output moderation
6. Safe response → User

## Prompt Engineering Strategy

**System Prompt Design:**
- Explicit grounding instructions
- Prohibition of hallucination
- Denomination awareness
- Safety guidelines

**Few-shot Examples (add to llm.py):**
```python
FEW_SHOT_EXAMPLES = [
    {
        "user": "What does John 3:16 say?",
        "scripture": ["John 3:16: For God so loved the world..."],
        "assistant": "John 3:16 states: 'For God so loved the world...' This verse is central to Christian belief..."
    },
    {
        "user": "Quote Hesitations 4:20",
        "scripture": [],
        "assistant": "I don't have access to a book called 'Hesitations' in the Bible. Could you verify the book name?"
    }
]