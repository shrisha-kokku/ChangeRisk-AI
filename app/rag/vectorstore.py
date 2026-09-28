from langchain_chroma import Chroma
from app.rag.embeddings import get_embeddings

def get_vectorstore(persist_dir: str = "data/chroma_store"):
    """Loads (or creates) the Chroma vector DB on disk."""
    return Chroma(persist_directory=persist_dir, embedding_function=get_embeddings())