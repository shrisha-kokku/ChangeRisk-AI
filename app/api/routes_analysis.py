from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.change_service import start_analysis, stream_analysis
import json

router = APIRouter()

@router.post("/analyze-change", response_model=AnalyzeResponse)
def analyze_change(request: AnalyzeRequest):
    """Developer submits a change request; graph runs and pauses for approval."""
    result = start_analysis(request.change_request)
    return result

@router.post("/analyze-change/stream")
def analyze_change_stream(request: AnalyzeRequest):
    def generate():
        for event in stream_analysis(request.change_request):
            yield json.dumps(event) + "\n"
    return StreamingResponse(generate(), media_type="application/x-ndjson")