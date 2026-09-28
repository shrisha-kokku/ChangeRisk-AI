import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file into environment variables

def get_groq_api_key() -> str:
    return os.getenv("GROQ_API_KEY", "")

def get_langsmith_project() -> str:
    return os.getenv("LANGCHAIN_PROJECT", "changerisk-ai")