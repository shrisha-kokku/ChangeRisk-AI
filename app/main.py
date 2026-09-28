from fastapi import FastAPI
from app.api.routes_analysis import router as analysis_router
from app.api.routes_action import router as action_router

app = FastAPI(title="ChangeRisk AI")
app.include_router(analysis_router)
app.include_router(action_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}