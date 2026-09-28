import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, DecisionRequest
from app.services.action_service import stream_chat, stream_decision

router = APIRouter()


def _as_stream(events):
    def generate():
        for event in events:
            yield json.dumps(event) + "\n"
    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.post("/chat")
def chat(request: ChatRequest):
    return _as_stream(stream_chat(request.message, request.report, request.thread_id))


@router.post("/decision")
def decision(request: DecisionRequest):
    return _as_stream(stream_decision(request.thread_id, request.approved, request.args))