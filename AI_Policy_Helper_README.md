# AI Policy & Product Helper

A local-first RAG starter with **FastAPI** (backend), **Next.js** (frontend), and **Qdrant** (vector DB). Runs with one command using Docker Compose.


## Quick start

1) **Copy `.env.example` → `.env`** and edit as needed.

2) **Run everything**:
```bash
docker compose up --build
```
- Frontend: http://localhost:3000  
- Backend:  http://localhost:8000/docs  
- Qdrant:   http://localhost:6333 (UI)

3) **Ingest sample docs** (from the UI Admin tab) or:
```bash
curl -X POST http://localhost:8000/api/ingest
```

4) **Ask a question**:
```bash
curl -X POST http://localhost:8000/api/ask -H 'Content-Type: application/json' \
  -d '{"query":"What’s the shipping SLA to East Malaysia for bulky items?"}'
```

## Offline-friendly
- If you **don’t** set an API key, the backend uses a **deterministic stub LLM** and a **built-in embedding** to keep everything fully local.
- If you set `OPENROUTER_API_KEY` (or configure Ollama), the backend will use real models automatically.

## Project layout
```
ai-policy-helper/
├─ backend/
│  ├─ app/
│  │  ├─ main.py          # FastAPI app + endpoints
│  │  ├─ settings.py      # config/env
│  │  ├─ rag.py           # embeddings, vector store, retrieval, generation
│  │  ├─ models.py        # pydantic models
│  │  ├─ ingest.py        # doc loader & chunker
│  │  ├─ __init__.py
│  │  └─ tests/
│  │     ├─ conftest.py
│  │     └─ test_api.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ app/
│  │  ├─ page.tsx         # chat UI
│  │  ├─ layout.tsx
│  │  └─ globals.css
│  ├─ components/
│  │  ├─ Chat.tsx
│  │  └─ AdminPanel.tsx
│  ├─ lib/api.ts
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ next.config.js
│  └─ Dockerfile
├─ data/                  # sample policy docs
├─ docker-compose.yml
├─ Makefile
└─ .env.example
```

## Tests
Run unit tests inside the backend container:
```bash
docker compose run --rm backend pytest -q
```

## Notes
- Keep it simple. For take-home, focus on correctness, citations, and clean code.

---

## Candidate Instructions (Read Me First)

### Goal
Build a local-first **Policy & Product Helper** using RAG that:
- Ingests the sample docs under `/data`
- Answers questions with **citations** (title + section)
- Exposes metrics and health endpoints
- Provides a minimal **chat UI** and **admin panel**

You have **48 hours** once you start. AI coding tools are allowed.

### Deliverables
1. **GitHub repo link** with your changes.
2. **README** describing setup, architecture, trade-offs, and what you’d ship next.
3. **2–5 minute screen capture** demonstrating ingestion + Q&A + citations.
4. **Tests**: show how to run them and their results (e.g., `pytest -q`).

### Acceptance Checks (we will run)
1. `docker compose up --build` boots **Qdrant + backend + frontend**.
2. Use Admin tab to **ingest** docs without errors.
3. Ask: *“Can a customer return a damaged blender after 20 days?”* → cites **Returns_and_Refunds.md** and **Warranty_Policy.md**.
4. Ask: *“What’s the shipping SLA to East Malaysia for bulky items?”* → cites **Delivery_and_Shipping.md** (mentions bulky item surcharge).
5. Expand a citation chip and see the underlying chunk text.

### Rubric (100 pts)
- **Functionality & correctness (35)** — ingestion, RAG with citations, metrics, health.
- **Code quality & structure (20)** — small functions, separation of concerns, typing, linting.
- **Reproducibility & docs (15)** — clear README, env.example, diagrams.
- **UX & DX polish (10)** — responsive, accessible, solid loading/errors.
- **Testing (10)** — meaningful unit/integration tests that run locally.
- **Performance & observability (10)** — reasonable latency, useful metrics/logs.

### How to Run (Docker)
```bash
# copy env
cp .env.example .env

# run all services
docker compose up --build

# endpoints
# frontend: http://localhost:3000
# backend swagger: http://localhost:8000/docs
# qdrant ui: http://localhost:6333
```

### How to Run (No Docker, optional)
Backend:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
```
Frontend:
```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

### Switching LLMs
- Default is **stub** (deterministic, offline). Use stub mode during development — it requires no API key, runs instantly, and lets you iterate quickly on your RAG pipeline, citations, UI, and tests.
- When you are ready to record your **2–5 minute demo video**, switch to the real LLM by setting `LLM_PROVIDER=openrouter` and `OPENROUTER_API_KEY` in `.env`. An OpenRouter API key is provided, which defaults to GPT-4o-mini. OpenRouter is an all-in-one LLM API key that lets you access different LLMs with the same key.
- **Important**: The API key is shared across all candidates. Please only use it during your demo recording to ensure everyone has a smooth experience.
- To use Ollama: set `LLM_PROVIDER=stub` (keep stub) or extend `rag.py` to add an `OllamaLLM` class.
- Please document any changes you make.

### Vector Store
- Default is **Qdrant** via Docker. Fallback is in-memory if Qdrant isn’t available.
- To switch to in-memory explicitly: `VECTOR_STORE=memory` in `.env`.

### API Reference
- `POST /api/ingest` → `{ indexed_docs, indexed_chunks }`
- `POST /api/ask` body:
  ```json
  { "query": "What's the refund window for Category A?", "k": 4 }
  ```
  Response includes `answer`, `citations[]`, `chunks[]`, `metrics`.
- `GET /api/metrics` → counters + avg latencies
- `GET /api/health` → `{ "status": "ok" }`

### UI Walkthrough
1. Open **http://localhost:3000**.
2. In **Admin** card, click **Ingest sample docs** and then **Refresh metrics**.
3. In **Chat**, ask questions. Click the **source badges** to expand supporting chunks.

### What You Can Modify
- Anything. Improve chunking, reranking (MMR), prompt, UI polish, streaming, caching, guardrails (PDPA masking), feedback logging, small eval script, etc.
- Keep the one-command run and README accurate.

### Constraints & Notes
- Keep keys out of the frontend.
- Validate file types if you extend ingestion to uploads.
- Provide small architecture diagram if you can (ASCII is fine).

### Troubleshooting
- **Qdrant healthcheck failing**: ensure port `6333` is free; re-run compose.
- **CORS**: CORS is configured to `*` in `main.py` for local dev.
- **Embeddings/LLM**: With no keys, stub models run by default so the app always works.

### Submission
- Share GitHub repo link + your short demo video.
- Include any notes on trade-offs and next steps.
