from langchain_community.document_loaders import PyPDFLoader
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter  
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS  
import torch
print(torch.cuda.is_available())

loader = PyPDFLoader("C:\\Users\\Aadiy\\OneDrive\\Desktop\\GenAI\\RAG\\Before_the_Coffee_Gets_Cold_Toshikazu_Kawaguchi.pdf")
documents = loader.load()
print(f"Loaded {len(documents)} documents.")

def preprocessing(document):
    # Remove newlines and extra spaces
    text = re.sub(r'\s+', ' ', document.page_content)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'Page \d+', '', text) # Remove page numbers
    return text.strip()

for doc in documents:
    doc.page_content = preprocessing(doc)
print("Preprocessing completed.")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = text_splitter.split_documents(documents)
print(f"Total chunks created: {len(chunks)}")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"})

print("Embeddings model loaded.")
embeddings_list = embeddings.embed_documents([chunk.page_content for chunk in chunks])

db = FAISS.from_documents(chunks, embeddings)
print("FAISS vector store created.")

# Retriever
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

query = "What is the main concept of the cafe in the story?"

# Generation
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLM
llm = ChatOllama(
    model="granite3.2:8b",
    temperature=0.7
)

# Prompt
prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the context below.

Context:
{context}

Question:
{question}
""")

# Format documents
def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

# RAG Chain (LCEL)
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": lambda x: x
    }
    | prompt
    | llm
    | StrOutputParser()
)

# Run
response = rag_chain.invoke(query)

print("\n🧠 Generated Response:\n")
print(response)