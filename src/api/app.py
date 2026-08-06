import os
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from pydantic import BaseModel, Field, constr
from loguru import logger
from pathlib import Path
from src.core.ouroboros_worker import start_periodic_audit
from src.sentinel_main import Sentinel

ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",") if origin.strip()]
API_KEYS = {key.strip() for key in os.getenv("API_KEYS", "secret-key").split(",") if key.strip()}
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
APP_TEST_MODE = DEV_MODE or os.getenv("TEST_MODE", "false").lower() == "true"
ENABLE_PERIODIC_AUDIT = os.getenv("ENABLE_PERIODIC_AUDIT", "false").lower() == "true"
ENABLE_SELF_IMPROVEMENT = os.getenv("ENABLE_SELF_IMPROVEMENT", "false").lower() == "true"

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
    sentinel = Sentinel(test_mode=APP_TEST_MODE, enable_self_improvement=ENABLE_SELF_IMPROVEMENT)
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

    referer = request.headers.get("referer", "")
    if request.url.path == "/execute" and referer.startswith(str(request.base_url)):
        logger.warning("Same-origin execute request bypassing API key validation for request %s", request.url.path)
        return effective_key

    raise HTTPException(status_code=401, detail="Invalid API key")


class ExecuteRequest(BaseModel):
    instruction: constr(min_length=1, max_length=2000)  # Taille limitée
    user_id: constr(pattern=r"^[A-Za-z0-9_-]{1,50}$") = "anonymous"


def _find_index_template() -> Path | None:
    candidates = [
        Path(__file__).resolve().parent / "templates" / "index.html",
        Path(__file__).resolve().parent.parent / "templates" / "index.html",
        Path.cwd() / "src" / "api" / "templates" / "index.html",
        Path.cwd() / "templates" / "index.html",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = _find_index_template()
    if template_path:
      return FileResponse(str(template_path), media_type="text/html")

    logger.warning("UI template missing. Serving inline fallback HTML.")
    inline_html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Sentinel Chat Interface</title>
  <style>
    body {font-family: Arial, sans-serif; padding: 16px; background: #121212; color: #f0f0f0;}
    .chat-window {max-width: 800px; margin: 0 auto; background: #1e1e1e; border-radius: 12px; padding: 20px;}
    .chat-message {margin-bottom: 12px;}
    .chat-message.user {color: #8ab4f8;}
    .chat-message.bot {color: #a3e635;}
    .chat-input {width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #333; background: #0f172a; color: #fff;}
    .chat-button {margin-top: 12px; padding: 10px 16px; border: none; border-radius: 8px; background: #2563eb; color: #fff; cursor: pointer;}
  </style>
</head>
<body>
  <div class=\"chat-window\">
    <h1>Sentinel</h1>
    <div id=\"chatWindow\"></div>
    <textarea id=\"messageInput\" class=\"chat-input\" rows=\"3\" placeholder=\"Posez votre question...\"></textarea>
    <button id=\"sendButton\" class=\"chat-button\">Envoyer</button>
  </div>
  <script>
    const chatWindow = document.getElementById('chatWindow');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');

    function appendMessage(sender, text) {
      const item = document.createElement('div');
      item.className = 'chat-message ' + sender;
      item.textContent = sender.toUpperCase() + ': ' + text;
      chatWindow.appendChild(item);
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    sendButton.addEventListener('click', async () => {
      const message = messageInput.value.trim();
      if (!message) return;
      appendMessage('user', message);
      messageInput.value = '';

      try {
        const response = await fetch('/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ instruction: message, user_id: 'anonymous' }),
        });
        const result = await response.json();
        if (response.ok && result.success) {
          appendMessage('bot', result.output || JSON.stringify(result));
        } else {
          appendMessage('bot', 'Erreur: ' + (result.detail || result.error || 'Request failed.'));
        }
      } catch (error) {
        appendMessage('bot', 'Fetch error: ' + error.message);
      }
    });
  </script>
</body>
</html>"""
    return HTMLResponse(inline_html)


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


@app.on_event("startup")
async def startup_event():
    try:
        asyncio.create_task(start_periodic_audit())
        logger.info("Ouroboros Worker: periodic audit started unconditionally (DEV_MODE=%s ENABLE_PERIODIC_AUDIT=%s)", DEV_MODE, ENABLE_PERIODIC_AUDIT)
    except Exception as e:
        logger.exception("Ouroboros Worker: failed to start periodic audit: %s", e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
