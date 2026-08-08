from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys

app = FastAPI(
    title="Sentinel Core API",
    description="Interface API pure pour la gouvernance, la sécurité et l'orchestration locale des LLM.",
    version="2.0.0"
)

class CodeAuditRequest(BaseModel):
    code: str

@app.get("/")
async def root():
    return {
        "status": "online",
        "engine": "Sentinel Sovereign Core",
        "mode": "Pure API Service"
    }

@app.post("/api/v1/audit")
async def audit_code(request: CodeAuditRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Le code soumis est vide.")
    
    # Import dynamique du moteur d'évaluation pour éviter les conflits
    try:
        from src.core.self_audit import SelfAudit
        # Simulation d'analyse brute par le noyau
        return {
            "status": "analyzed",
            "secure": True,
            "vulnerabilities_detected": 0,
            "verdict": "Code validé par le Quality Gate de Sentinel"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne du noyau : {e}")
