# Multi-Model Chatbot

A clean, minimal chatbot application demonstrating a multi-model LLM architecture. It features manual model selection, automatic routing based on query complexity, and a complete RAG (Retrieval-Augmented Generation) pipeline.

## Features

- **Multi-Model Support**: Interact seamlessly with Gemini, Groq, and Granite (local via Ollama).
- **Auto Router**: Intelligently routes messages:
  - Complex/Reasoning queries go to Gemini.
  - Short/Factual queries go to Groq.
  - Fallback to Granite.
- **RAG Pipeline**: Upload a PDF or TXT to instantly inject context into conversations.
- **Dockerized Infrastructure**: Simplifies Qdrant (Vector DB) and Ollama setups.
- **Modern UI**: React web app with glassmorphism and beautiful design.

## Directory Structure
```
LLMRouter/
├── docker-compose.yml       # Qdrant and Ollama services
├── .env                     # Make sure to copy .env.example here
├── backend/
│   ├── requirements.txt
│   ├── main.py              # FastAPI app and endpoints
│   ├── models.py            # Pydantic schemas
│   ├── llm_manager.py       # LangChain setup and routing
│   └── rag.py               # Document embedder and retriever
└── frontend/
    ├── package.json
    ├── vite.config.js       # Vite React setup
    └── src/                 # CSS and App files component
```

## Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

## Quick Start Local Run

### 1. Set Environment Variables
Copy `.env.example` to `.env` and fill in your API keys in the root directory.
```bash
cp .env.example .env
```

### 2. Start Infrastructure
Run the Vector Database (Qdrant) and Ollama locally.
```bash
docker-compose up -d
```
Pull the granite memory for Ollama (Important: this sets up the final LLM):
```bash
docker exec -it <ollama-container-name> ollama pull granite3.2:8b
```

### 3. Start Backend
Open a terminal in the `backend` folder:
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Start Frontend
Open a new terminal in the `frontend` folder:
```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173` to test the AI Assistant!
