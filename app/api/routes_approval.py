from fastapi import APIRouter
from app.models.schemas import ApprovalRequest, ApprovalResponse
from app.services.change_service import submit_approval

router = APIRouter()

@router.post("/approve", response_model=ApprovalResponse)
def approve_change(request: ApprovalRequest):
    """Developer approves/rejects; graph resumes and (if approved) files the GitHub issue."""
    result = submit_approval(request.thread_id, request.approved)
    return result