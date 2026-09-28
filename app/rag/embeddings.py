from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    """Free, local embedding model — no API key needed."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")