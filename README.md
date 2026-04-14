# Attune — AI Music Theory Tutor

A conversational AI music theory tutor with a usage-based API. Built with FastAPI, Next.js, Claude, and ChromaDB.

## Project Structure

```
attune/
├── backend/               # FastAPI Python backend
│   ├── main.py            # App entry point
│   ├── config.py          # Settings & environment variables
│   ├── database.py        # SQLAlchemy async setup
│   ├── models.py          # DB models: User, Session, Message
│   ├── routers/
│   │   └── tutor.py       # /tutor/* API endpoints
│   ├── services/
│   │   ├── embeddings.py  # OpenAI embedding wrapper
│   │   ├── rag.py         # ChromaDB vector store & retrieval
│   │   └── tutor_agent.py # Claude tutor + RAG orchestration
│   └── knowledge/
│       ├── ingest.py      # Knowledge base ingestion script
│       └── content/       # Markdown files → knowledge base
└── frontend/              # Next.js 14 frontend
    ├── app/
    │   ├── page.tsx       # Landing / skill level selection
    │   └── chat/page.tsx  # Main chat interface
    ├── components/        # (Week 3: add shared components here)
    └── lib/api.ts         # API client & streaming helper
```

## Getting Started

### 1. Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and OPENAI_API_KEY

pip install -r requirements.txt

# Ingest the knowledge base (run once, or after adding content)
python knowledge/ingest.py

# Start the server
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tutor/session/start` | Start a session, set skill level |
| POST | `/tutor/chat` | Send a message, stream response (SSE) |
| GET | `/tutor/session/{id}/summary` | Get session summary + topics covered |
| GET | `/health` | Health check |

## Adding Knowledge

Add `.md` files to `backend/knowledge/content/`. Each section (`##` header) becomes a searchable chunk. Re-run `python knowledge/ingest.py` after adding content.

Format:
```markdown
# Section Title
topic: topic_slug
difficulty: beginner|intermediate|advanced|all

## Sub-Topic Header
Your content here...
```

## Week-by-Week Build Plan

- **Week 1** ✅ Foundation: backend scaffold, RAG pipeline, basic chat endpoint, minimal frontend
- **Week 2** → Tutor intelligence: skill assessment quiz, curriculum graph, session memory, Socratic prompting
- **Week 3** → Frontend polish: notation rendering, topic explorer, progress tracking, mobile
- **Week 4** → Business layer: API keys, usage metering, Stripe billing, deploy
