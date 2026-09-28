from fastapi import FastAPI
from app.api.routes_analysis import router as analysis_router
from app.api.routes_approval import router as approval_router

app = FastAPI(title="ChangeRisk AI")

app.include_router(analysis_router)
app.include_router(approval_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}