from typing import Optional
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    change_request: str


class ChatRequest(BaseModel):
    message: str
    report: str
    thread_id: Optional[str] = None


class DecisionRequest(BaseModel):
    thread_id: str
    approved: bool
    args: dict