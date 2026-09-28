import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import AnalyzeRequest
from app.services.change_service import stream_analysis

router = APIRouter()


@router.post("/analyze-change/stream")
def analyze_change_stream(request: AnalyzeRequest):
    def generate():
        for event in stream_analysis(request.change_request):
            yield json.dumps(event) + "\n"
    return StreamingResponse(generate(), media_type="application/x-ndjson")