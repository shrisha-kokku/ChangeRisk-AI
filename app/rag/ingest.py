from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vectorstore import get_vectorstore

def ingest_documents(source_dir: str = "data"):
    """Reads codebase/docs/security-policy files, chunks them, stores them as vectors."""
    loader = DirectoryLoader(
        source_dir,
        glob="**/*.*",
        loader_cls=TextLoader,          # NEW — forces plain text loading, no 'unstructured' needed
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    store = get_vectorstore()
    store.add_documents(chunks)
    return len(chunks)