"""
RAG Pipeline for LLMRouter

Improved:
- Better retrieval (score-based)
- Structured context
- Cleaner output for LLM
"""

import os
from typing import List
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

from langchain_ollama import OllamaEmbeddings

load_dotenv()


class RAGPipeline:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = "chat_docs"

        print(f"[RAG] Connecting to Qdrant at {self.qdrant_url}")

        # -------------------------------
        # EMBEDDINGS
        # -------------------------------
        self.embeddings = OllamaEmbeddings(
            model="granite3.2:8b",
            base_url="http://localhost:11434",
        )

        # -------------------------------
        # QDRANT CONNECTION
        # -------------------------------
        self.client = QdrantClient(url=self.qdrant_url)
        self.client.get_collections()
        print("[RAG] Qdrant connected")

        # -------------------------------
        # COLLECTION SETUP
        # -------------------------------
        if not self.client.collection_exists(self.collection_name):
            print("[RAG] Creating collection...")

            dummy_vector = self.embeddings.embed_query("test")

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=len(dummy_vector),
                    distance=Distance.COSINE,
                ),
            )

        # -------------------------------
        # VECTOR STORE
        # -------------------------------
        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    # ============================================================
    # DOCUMENT PROCESSING
    # ============================================================
    def process_file(self, file_path: str, filename: str) -> int:
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents = loader.load()

        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
            documents = loader.load()

        else:
            raise ValueError("Only PDF and TXT supported")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,   
            chunk_overlap=150,
        )

        chunks = splitter.split_documents(documents)

        if chunks:
            self.vectorstore.add_documents(chunks)

        return len(chunks)

    # ============================================================
    # RETRIEVAL (IMPROVED)
    # ============================================================
    def retrieve_context(self, query: str, top_k: int = 8) -> str:
        try:
            # 🔥 Get scores too
            results = self.vectorstore.similarity_search_with_score(
                query, k=top_k
            )

            filtered_docs = [
                (doc, score)
                for doc, score in results
                if score < 0.8  
            ]

            if not filtered_docs:
                return ""

            context_parts = []
            for i, (doc, score) in enumerate(filtered_docs):
                context_parts.append(
                    f"[Source {i+1} | relevance={round(score, 3)}]\n{doc.page_content}"
                )

            return "\n\n---\n\n".join(context_parts)

        except Exception as e:
            print(f"[RAG ERROR] {e}")
            return ""