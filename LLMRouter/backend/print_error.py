import traceback
try:
    from rag import RAGPipeline
    r = RAGPipeline()
except Exception as e:
    print(str(e))
