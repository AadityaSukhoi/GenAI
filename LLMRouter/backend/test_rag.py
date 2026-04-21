import sys
import traceback
sys.path.append('.')
from rag import RAGPipeline

try:
    rag = RAGPipeline()
    print("RAG initialized successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
