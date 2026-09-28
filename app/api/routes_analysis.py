from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.change_service import start_analysis

router = APIRouter()

@router.post("/analyze-change", response_model=AnalyzeResponse)
def analyze_change(request: AnalyzeRequest):
    """Developer submits a change request; graph runs and pauses for approval."""
    result = start_analysis(request.change_request)
    return result