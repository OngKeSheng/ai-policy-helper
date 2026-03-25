# AI Policy & Product Helper

A **local-first RAG (Retrieval Augmented Generation)** system that ingests policy documents and answers customer questions with **citations**.

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 18+

### Setup & Run

1. **Clone and navigate:**
   ```bash
   cd ai-policy-helper-starter-pack
   ```

2. **Copy `.env.example` → `.env`** (already done, but verify):
   ```bash
   cp .env.example .env
   ```
   Current settings for local dev:
   ```env
   LLM_PROVIDER=stub          # Offline, deterministic, no API key needed
   VECTOR_STORE=memory        # In-memory store (for local dev)
   ```

3. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # Mac/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Frontend Setup (new terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Open browser:** http://localhost:3000

### Test Ingestion & Q&A

1. Click **"Ingest sample docs"** button
2. Go to **Chat** tab and ask:
   - *"Can a customer return a damaged blender after 20 days?"*
     - Expected: Citations from `Returns_and_Refunds.md` + `Warranty_Policy.md`
   - *"What's the shipping SLA to East Malaysia for bulky items?"*
     - Expected: Citations from `Delivery_and_Shipping.md`

### Run Tests

```bash
cd backend
pytest -v
```

Expected output:
```
test_api.py::test_health PASSED
test_api.py::test_ingest_and_ask PASSED
====== 2 passed in 2.44s ======
```

---

## Architecture

### High-Level Flow

```
User Query (UI)
     ↓
  [Frontend: Next.js]
     ↓
  [Backend: FastAPI] ── /api/ask endpoint
     ↓
  [RAG Engine]
     ├─ Embed query (LocalEmbedder: 384-dim)
     ├─ Retrieve top-k chunks (Vector Store)
     ├─ Generate answer (StubLLM or OpenRouterLLM)
     └─ Return citations + chunks
     ↓
  [Response with Citations]
     ↓
  [Frontend: Display answer + expandable chunks]
```

### Key Components

#### **Backend** (`backend/app/`)
- **`main.py`** — FastAPI routes (`/api/health`, `/api/metrics`, `/api/ingest`, `/api/ask`)
- **`rag.py`** — RAG orchestrator, embedder, vector stores (Qdrant/InMemory), LLM providers (Stub/OpenRouter)
- **`ingest.py`** — Document loader, Markdown section parser, chunker
- **`models.py`** — Pydantic schemas for request/response validation
- **`settings.py`** — Environment configuration loader

#### **Frontend** (`frontend/`)
- **`app/page.tsx`** — Main layout (renders AdminPanel + Chat)
- **`components/AdminPanel.tsx`** — Ingest & metrics display
- **`components/Chat.tsx`** — Chat UI with citation badges + expandable chunks
- **`lib/api.ts`** — API client for backend

#### **Vector Store**
- **Qdrant** (Docker) — Persistent vector DB for production
- **In-Memory** — Fast, local development mode (default for now)

#### **Embeddings**
- **LocalEmbedder** — Deterministic hash-based pseudo-embeddings (384-dim, normalized)
- Always fully offline, no API key needed

#### **LLM**
- **StubLLM** — Offline, deterministic, lists sources. Great for dev/testing.
- **OpenRouterLLM** — Real GPT-4o-mini via OpenRouter API (use for demo only)

---

## Data

Sample documents in `/data`:
- `Product_Catalog.md` — Product SKUs, prices, categories
- `Returns_and_Refunds.md` — Return windows (14 days appliances, 7 days electronics)
- `Warranty_Policy.md` — Coverage (12–24 months), exclusions (misuse, liquid damage)
- `Delivery_and_Shipping.md` — SLAs (West Malaysia 2–4 days, East Malaysia 5–10 days for bulky)
- `Compliance_Notes.md` — PDPA guidelines (data minimization, masking)
- `Internal_SOP_Agent_Guide.md` — Agent tone, escalation procedures

### Ingestion Process
1. Load all `.md` / `.txt` files from `/data`
2. Split by Markdown headings (sections)
3. Chunk text (700 words, 80-word overlap)
4. Embed each chunk (LocalEmbedder)
5. Store in vector DB with metadata (title, section, text)

---

## API Reference

### `GET /api/health`
Health check.
```bash
curl http://localhost:8000/api/health
# {"status": "ok"}
```

### `POST /api/ingest`
Ingest all documents from `/data` directory.
```bash
curl -X POST http://localhost:8000/api/ingest
# {"indexed_docs": 6, "indexed_chunks": 12}
```

### `POST /api/ask`
Ask a question with optional top-k parameter.
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can a customer return a damaged blender after 20 days?",
    "k": 4
  }'
# {
#   "query": "...",
#   "answer": "Based on the following sources: ...",
#   "citations": [
#     {"title": "Returns_and_Refunds.md", "section": "Conditions"},
#     ...
#   ],
#   "chunks": [...],
#   "metrics": {"retrieval_ms": 12.5, "generation_ms": 45.2}
# }
```

### `GET /api/metrics`
View ingestion and performance metrics.
```bash
curl http://localhost:8000/api/metrics
# {
#   "total_docs": 6,
#   "total_chunks": 12,
#   "avg_retrieval_latency_ms": 12.5,
#   "avg_generation_latency_ms": 45.2,
#   "embedding_model": "local-384",
#   "llm_model": "stub"
# }
```

---

## Configuration (`.env`)

```env
# Backend
EMBEDDING_MODEL=local-384              # 384-dim local deterministic embedder
LLM_PROVIDER=stub                      # stub | openrouter | ollama
# OPENROUTER_API_KEY=sk-or-v1-...     # Uncomment only for demo recording
VECTOR_STORE=memory                    # qdrant | memory (use memory for local dev)
COLLECTION_NAME=policy_helper
CHUNK_SIZE=700
CHUNK_OVERLAP=80
DATA_DIR=../data

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Switching LLMs

**Development (stub mode — recommended):**
```env
LLM_PROVIDER=stub
```
- Offline, no API key
- Deterministic (same query = same answer)
- Instant responses
- Perfect for testing citations, UI, and pipeline

**Demo Recording (real GPT answers):**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...       # Provided by interviewer
```
- Real GPT-4o-mini answers
- Use sparingly (shared key across candidates)
- Only uncomment for final demo recording

---

## Code Quality

### Chunking Strategy
- Simple word-based tokenizer
- 700-word chunks with 80-word overlap
- Preserves sections via Markdown heading detection
- No sophisticated reranking (can be added later)

### Retrieval
- Cosine similarity in embedding space
- Top-k=4 (configurable)
- Returns metadata (title, section) for each chunk

### Generation
- Stub LLM: Lists sources, concatenates chunk text
- OpenRouter LLM: Uses GPT-4o-mini with source citations in prompt
- Temperature=0.1 (low randomness, factual)

### Error Handling
- Graceful fallback: If Qdrant unavailable, use in-memory store
- If API key not provided, use stub mode
- Missing files: Log warnings, continue

---

## Trade-offs & Design Decisions

### 1. **In-Memory Vector Store (Local Dev)**
- ✅ No Docker/Qdrant dependency (simpler setup)
- ✅ Fast iteration during development
- ❌ Not persistent across restarts
- 🔄 Swap to Qdrant for Docker Compose deployment

### 2. **Stub LLM During Development**
- ✅ No API key needed
- ✅ Instant, deterministic responses
- ✅ Perfect for testing RAG pipeline & citations
- ❌ Answers are generic (list of sources)
- 🔄 Switch to OpenRouter for real answers in demo

### 3. **Local Embeddings (No API)**
- ✅ Fully offline, zero latency
- ✅ Deterministic (reproducible results)
- ❌ Not semantic (hash-based pseudo-embeddings)
- 📌 Good enough for small doc sets; can upgrade to sentence-transformers if needed

### 4. **Simple Chunking**
- ✅ Fast, no ML dependencies
- ✅ Preserves sections via heading structure
- ❌ No semantic awareness
- 🔄 Consider: MMR reranking, recursive chunking if performance degrades

### 5. **No Authentication/Rate Limiting**
- ✅ Simpler code for assessment
- ❌ Not suitable for production
- 🔄 Add JWT + rate limiting for real deployment

---

## What's Included

✅ **Functionality**
- Ingestion from Markdown files
- Chunk vectorization & retrieval
- Answer generation with citations
- Metrics & health endpoints
- Admin UI for ingestion
- Chat UI with expandable citations

✅ **Testing**
- 2 integration tests (health, ingest+ask)
- Pytest setup ready for expansion

✅ **Dev Experience**
- Auto-reload (FastAPI + Next.js)
- Python type hints
- Clean code structure
- Environment configuration

---

## Next Steps / Improvements

### Short-term (for production)
1. **Semantic embeddings** — Replace local embedder with `sentence-transformers` (all-MiniLM-L6-v2)
2. **Qdrant persistence** — Docker Compose for deployment
3. **Reranking** — MMR or semantic reranking for better retrieval
4. **Streaming** — Stream LLM responses for faster UX
5. **Authentication** — JWT tokens, rate limiting, API key management
6. **Testing** — More comprehensive tests (edge cases, error scenarios)

### Medium-term
1. **Feedback loop** — Track user satisfaction, log incorrect answers
2. **Fine-tuning** — Custom embeddings on company policy data
3. **Multi-turn** — Conversation history, context awareness
4. **Fact verification** — Cross-check LLM output against retrieved chunks
5. **Performance** — Caching, async processing, connection pooling

### Long-term
1. **Knowledge graph** — Structured extraction from documents
2. **Hybrid search** — BM25 (keyword) + semantic (embedding) fusion
3. **RAG evaluation** — Metrics (BLEU, ROUGE, answer relevance)
4. **Autonomous agents** — Tool-calling, multi-step reasoning

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process if needed
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Frontend won't compile
- Clear `.next` cache: `rm -rf frontend/.next`
- Restart: `npm run dev`
- Check `tsconfig.json` has `paths` alias defined

### Ingest returns 500 error
- Check `.env` has correct `DATA_DIR` (should be `../data` for local dev)
- Verify files exist: `ls data/`
- Check backend logs for Python exceptions

### Qdrant connection fails
- Make sure `docker-compose up` is running (if using Qdrant)
- Or switch to `VECTOR_STORE=memory` in `.env`

### API calls from frontend return CORS errors
- CORS is configured for `*` in `main.py` (fine for development)
- For production, restrict to specific domains

---

---

## License

Assessment submission. Built with FastAPI, Next.js, and Pydantic.
