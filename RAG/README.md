# RAG Pipeline with LangChain + FAISS + Ollama

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline using LangChain, HuggingFace embeddings, FAISS vector store, and an Ollama-hosted LLM.

It processes a PDF book, chunks the content, embeds it, stores it in a vector database, and answers user queries based on retrieved context.

---

## Features

- Load and preprocess PDF documents
- Intelligent text chunking
- Semantic embeddings using HuggingFace
- Fast similarity search with FAISS
- Local LLM inference using Ollama
- End-to-end RAG pipeline with LangChain Expression Language (LCEL)

---

## Tech Stack

- **LangChain**
- **FAISS**
- **HuggingFace Transformers**
- **Ollama (granite3.2:8b)**
- **PyTorch (CUDA optional)**

---

## Project Workflow

### 1. Load PDF
- Uses `PyPDFLoader` to load the book:
`Before the Coffee Gets Cold - Toshikazu Kawaguchi`

---

### 2. Preprocessing
- Removes:
- Extra whitespace
- Newlines
- Page numbers

---

### 3. Text Splitting
- Uses `RecursiveCharacterTextSplitter`
- Config:
- Chunk size: `300`
- Overlap: `30`

---

### 4. Embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Device:
- GPU (`cuda`) if available
- Otherwise CPU

---

### 5. Vector Store
- FAISS is used to store embeddings
- Enables fast similarity search

---

### 6. Retriever
- Search type: `similarity`
- Top results (`k`): `3`

---

### 7. LLM (Ollama)
- Model: `granite3.2:8b`
- Temperature: `0.7`

---

### 8. RAG Chain
- Built using LangChain Expression Language (LCEL)
- Flow:
  `Query → Retriever → Context → Prompt → LLM → Output`

---

## Prompt Template

```text
Answer the question based only on the context below.

Context:
{context}

Question:
{question}

```

---

# How to Run

## 1. Install Dependencies

```
pip install -r requirements.txt
```

## 2. Start Ollama

Make sure Ollama is running and the model is pulled:

```
ollama pull granite3.2:8b
ollama run granite3.2:8b
```

## 3. Run Script

```
python docs.py
```

---

# Notes

- GPU acceleration is automatically enabled if CUDA is available:

```
torch.cuda.is_available()
```
- Embeddings are computed once and stored in FAISS
- Retrieval improves factual grounding of responses