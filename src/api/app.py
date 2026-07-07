"""🌐 REST API - SENTINEL via FastAPI
Expose SENTINEL en API HTTP
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from src.sentinel_main import Sentinel
import time

# Initialize
app = FastAPI(
    title="🛡️ SENTINEL API",
    description="One AI to rule them all - Transparent, Secure, Honest AI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Sentinel
try:
    sentinel = Sentinel()
except Exception as e:
    logger.error(f"Failed to initialize Sentinel: {e}")
    sentinel = None

# Models
class ExecuteRequest(BaseModel):
    instruction: str
    user_id: str = "anonymous"

class ExecuteResponse(BaseModel):
    success: bool
    response: str = None
    quality_score: float = None
    model_used: str = None
    execution_id: str = None
    effectiveness: float = None
    execution_time: float = None
    error: str = None

# Routes
@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "operational",
        "sentinel": "ready" if sentinel else "not initialized"
    }

@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute a task through SENTINEL"""
    
    if not sentinel:
        raise HTTPException(status_code=500, detail="Sentinel not initialized")
    
    logger.info(f"API Request: {request.instruction[:60]}...")
    
    try:
        result = sentinel.execute(request.instruction, request.user_id)
        
        return ExecuteResponse(
            success=result.get("success", False),
            response=result.get("response"),
            quality_score=result.get("quality_score"),
            model_used=result.get("model_used"),
            execution_id=result.get("execution_id"),
            effectiveness=result.get("effectiveness"),
            execution_time=result.get("execution_time"),
            error=result.get("error")
        )
    
    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def status():
    """Get SENTINEL status"""
    return {
        "system": "SENTINEL",
        "version": "1.0.0",
        "status": "operational",
        "components": {
            "grammar_corrector_input": "ready",
            "parser": "ready",
            "classifier": "ready",
            "router": "ready",
            "orchestrator": "ready",
            "quality_gate": "ready",
            "accuracy_coach": "ready",
            "logger": "ready",
            "grammar_corrector_output": "ready",
        }
    }

@app.get("/docs")
async def docs():
    """API Documentation"""
    return {
        "title": "🛡️ SENTINEL API",
        "description": "One AI to rule them all",
        "endpoints": {
            "POST /execute": "Execute a task",
            "GET /health": "Health check",
            "GET /status": "System status",
            "GET /docs": "This documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
