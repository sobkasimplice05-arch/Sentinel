from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from src.sentinel_main import Sentinel

app = FastAPI(title="🛡️ SENTINEL API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

try:
    sentinel = Sentinel()
except Exception as e:
    logger.error(f"Failed: {e}")
    sentinel = None

class ExecuteRequest(BaseModel):
    instruction: str
    user_id: str = "anonymous"

@app.get("/health")
async def health_check():
    return {"status": "operational", "sentinel": "ready" if sentinel else "not"}

@app.post("/execute")
async def execute(request: ExecuteRequest):
    if not sentinel:
        raise HTTPException(status_code=500, detail="Not initialized")
    result = sentinel.execute(request.instruction, request.user_id)
    return result

@app.get("/status")
async def status():
    return {"system": "SENTINEL", "version": "1.0.0", "status": "operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
