from pydantic import BaseModel
from typing import List, Dict

class AnalyzeRequest(BaseModel):
    change_request: str

class AnalyzeResponse(BaseModel):
    thread_id: str
    risk_report: str
    question: str
    execution_log: List[Dict[str, str]]

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool

class ApprovalResponse(BaseModel):
    status: str
    execution_log: List[Dict[str, str]]