from langchain_groq import ChatGroq
from app.core.config import get_groq_api_key

def get_llm():
    """Free Groq-hosted LLM — fast inference, no cost."""
    return ChatGroq(
        groq_api_key=get_groq_api_key(),
        model="openai/gpt-oss-120b",
        temperature=0
    )