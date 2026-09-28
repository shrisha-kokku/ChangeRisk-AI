from app.rag.vectorstore import get_vectorstore

def retrieve_context(query: str, k: int = 4) -> list[str]:
    """Given the change request, returns the most relevant chunks."""
    store = get_vectorstore()
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]