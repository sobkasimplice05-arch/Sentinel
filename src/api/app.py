import os
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr
from loguru import logger
from pathlib import Path
from src.sentinel_main import Sentinel

ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",") if origin.strip()]
API_KEYS = {key.strip() for key in os.getenv("API_KEYS", "secret-key").split(",") if key.strip()}
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

DEFAULT_API_KEY = next(iter(API_KEYS), "secret-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI(title="🛡️ SENTINEL API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "X-API-Key", "Content-Type"],
)

try:
    sentinel = Sentinel()
except (RuntimeError, ImportError, OSError) as e:
    logger.error(f"Failed initialization: {e}")
    sentinel = None


def validate_api_key(request: Request, x_api_key: str | None = Depends(api_key_header)):
    effective_key = x_api_key or DEFAULT_API_KEY

    if x_api_key and x_api_key in API_KEYS:
        return x_api_key

    if DEV_MODE:
        logger.warning("DEV_MODE=True : bypassing API key validation for request %s", request.url.path)
        return effective_key

    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
        logger.warning("Swagger docs request bypassing API key validation for request %s", request.url.path)
        return effective_key

    raise HTTPException(status_code=401, detail="Invalid API key")


class ExecuteRequest(BaseModel):
    instruction: constr(min_length=1, max_length=2000)  # Taille limitée
    user_id: constr(pattern=r"^[A-Za-z0-9_-]{1,50}$") = "anonymous"


@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = Path(__file__).resolve().parent / "templates" / "index.html"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="UI template not found")
    return HTMLResponse(template_path.read_text(encoding="utf-8"))


@app.get("/health")
async def health_check():
    return {"status": "operational", "sentinel": "ready" if sentinel else "not"}


@app.post("/execute")
async def execute(request: ExecuteRequest, api_key: str = Depends(validate_api_key)):
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
