"""
Main FastAPI application for LLMRouter

Features:
- JWT Authentication
- Multi-model routing (Gemini, Mistral, Granite)
- STRICT RAG enforcement
- Resilient streaming (handles model failures + fallback)
"""

import os
import shutil
import tempfile
import json
import sys

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Allow running from parent directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import ChatRequest
from llm_manager import LLMManager
from rag import RAGPipeline
from auth import router as auth_router, get_current_user


# -------------------------------
# APP SETUP
# -------------------------------
app = FastAPI(title="LLMRouter API")

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# INIT COMPONENTS
# -------------------------------
llm_manager = LLMManager()

rag_pipeline = None
rag_init_error = ""


def get_rag():
    """Lazy load RAG to avoid crash if Qdrant isn't ready"""
    global rag_pipeline, rag_init_error

    if rag_pipeline is None and rag_init_error == "":
        try:
            rag_pipeline = RAGPipeline()
        except Exception as e:
            rag_init_error = str(e)
            print(f"[RAG ERROR] Initialization failed: {e}")

    return rag_pipeline


# ============================================================
# 🔐 CHAT ENDPOINT
# ============================================================
@app.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Handles chat requests with:
    - Model routing
    - STRICT RAG grounding
    - Resilient streaming (error handling + fallback)
    """

    try:
        # -------------------------------
        # MODEL SELECTION
        # -------------------------------
        if request.model == "auto":
            model, used_model_name = llm_manager.route_query(request.query)
        else:
            model, used_model_name = llm_manager.get_model(request.model)

        # -------------------------------
        # RAG RETRIEVAL
        # -------------------------------
        rag = get_rag()
        context = ""

        if rag:
            context = rag.retrieve_context(request.query)

        if context:
            print(f"[DEBUG] Context length: {len(context)}")

        # -------------------------------
        # STRICT RAG PROMPT
        # -------------------------------
        messages = []

        if context and context.strip():
            system_prompt = f"""
You are a context-aware AI assistant.

Use the provided context to answer the question.

If the context contains relevant information, answer clearly.

If the context is partially relevant, combine it with your general knowledge.

If no useful context is found, say:
"I cannot find the answer in the provided documents."

Context:
{context}
"""

        messages.append(SystemMessage(content=system_prompt))

        # -------------------------------
        # CHAT HISTORY
        # -------------------------------
        if hasattr(request, "history") and request.history:
            for msg in request.history:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "ai":
                    messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=request.query))

        # -------------------------------
        # STREAM RESPONSE (SAFE + FALLBACK)
        # -------------------------------
        async def event_generator():
            try:
                # send meta info first
                yield f"data: {json.dumps({'type': 'meta', 'model_used': used_model_name})}\n\n"

                # primary model stream
                for chunk in model.stream(messages):
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content})}\n\n"

            except Exception as e:
                print(f"[MODEL ERROR] {e}")

                # 🔥 fallback to Gemini if primary fails
                try:
                    fallback_model, fallback_name = llm_manager.get_model("gemini")

                    yield f"data: {json.dumps({'type': 'meta', 'model_used': fallback_name + ' (fallback)'})}\n\n"

                    for chunk in fallback_model.stream(messages):
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content})}\n\n"

                except Exception as fallback_error:
                    # if even fallback fails → send error
                    yield f"data: {json.dumps({'type': 'error', 'content': str(fallback_error)})}\n\n"

            finally:
                yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 📄 FILE UPLOAD (RAG INGESTION)
# ============================================================
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """
    Upload document → chunk → embed → store in Qdrant
    """

    rag = get_rag()

    if not rag:
        raise HTTPException(
            status_code=500,
            detail=f"RAG system is not properly initialized. Error: {rag_init_error}",
        )

    try:
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1],
        )

        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file.close()

            chunks = rag.process_file(temp_file.name, file.filename)

            return {
                "message": "Document successfully processed and added to Qdrant.",
                "chunks": chunks,
            }

        finally:
            os.remove(temp_file.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 🚀 RUN SERVER
# ============================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)