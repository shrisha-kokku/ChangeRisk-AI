import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.ingest import ingest_documents

if __name__ == "__main__":
    count = ingest_documents("data")
    print(f"Ingested {count} chunks")