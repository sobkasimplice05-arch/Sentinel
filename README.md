🛡️ SENTINEL

[![License: MIT](https://shields.io)](https://opensource.org)
[![Python 3.11+](https://shields.io)](https://python.org)
[![Status: Active Development](https://shields.io)]()

**Sentinel** is an open-source, local-first LLM governance and orchestration layer designed to enforce absolute transparency, multi-layered security, and unbiased alignment. 

Unlike commercial AI assistants that optimize for user compliance (sycophancy), Sentinel optimizes for strict factuality and structural audibility.

---

## 🎯 Value Proposition

* **Zero Complacency (Anti-Sycophancy):** Detects and neutralizes AI brown-noser behaviors, ensuring objective, raw outputs.
* **Deterministic Auditing:** Logs 100% of pipeline decisions, execution metadata, and confidence scores into verifiable local JSON schemas.
* **Hardened Security Guardrails:** Intercepts jailbreaks, prompts injection, and hallucinations before execution and delivery.
* **Sovereign & Local-First:** Orchestrates open-weight models locally via Ollama with zero data leakage, zero latency overhead, and $0 API costs.

---

## ✨ Core Features

* **Multi-Model Routing:** Intelligently maps incoming prompts to specialized local weights (e.g., Mistral for low-latency syntax, Qwen for technical execution).
* **Pre/Post Execution Guardrails:** Features an advanced Input/Output pipeline using state-of-the-art tokenization and syntax parsers.
* **5-Layer Quality Gate:** Dynamic evaluation framework covering *Syntax, Logic, Guardrails, Hallucination, and Structural Completeness*.
* **Emergency Override Protocol:** Triggers isolated fallback mechanisms or human-in-the-loop escalation paths when structural confidence drops below threshold boundaries.

---

## 🚀 Quick Start

### Prerequisites
* Python 3.11+
* Ollama Runtime (Running locally)
* Minimum Hardware: 8GB RAM / Modern Multi-core CPU or Dedicated GPU

### Installation
```bash
# Clone the repository
git clone https://github.com
cd Sentinel

# Initialize virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\Activate.ps1

# Install production and development dependencies
pip install -r requirements.txt
```

### Execution

#### 1. Headless API Server (FastAPI)
```bash
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --reload
```
*Interactive Swagger Documentation available at:* `http://localhost:8000/docs`

#### 2. Local Web Interface (Streamlit)
```bash
streamlit run streamlit_app.py
```
*User Interface available at:* `http://localhost:8501`

---

## 📊 Pipeline Architecture
User Prompt│▼ (Ingestion Layer)Input Guardrails (Syntax Validation & Token Sanitization)│▼ (Control Plane)Instruction Parser ──► Task Classifier ──► Predictive Model Router│▼ (Execution Engine)Local LLM (via Ollama)│▼ (Evaluation Plane)5-Layer Quality Gate│▼ (Post-Processing)Output Realignment & Calibration│▼ (Storage Engine)JSON Transparency Logger│┌──────────────────────────────────────────────┘▼Sanitized Operational Response
---

## 💾 Tech Stack

* **Core Engine:** Python 3.11+, FastAPI (Asynchronous Web Server)
* **LLM Orchestration:** Ollama API Interface
* **Supported Weights:** Mistral-7B, Qwen-7B, Phi-3
* **Validation & NLP:** Hugging Face Transformers, spaCy, Pydantic (Data Validation)
* **Observability:** Loguru & Structured JSON Stream Logging
* **Frontend Sandbox:** Streamlit

---

## 📋 Project Status & Roadmap
For detailed granular tickets and implementation progress, please review [TASKS.md](./TASKS.md).

- [x] Phase 0: Repository Scaffold & Environment Matrix Setup
- [x] Phase 1: Input/Output Syntax realigners
- [ ] Phase 2: Multi-Layer Quality Gate Integration (Active Development)
- [ ] Phase 3: Model Routing Optimization 

---

## 🤝 Contributing
We welcome contributions from deep learning engineers, security researchers, and open-source advocates. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 👤 Maintainer
* **Sobka Patale Simplice** - *Lead Architect & Visionary*

---
> *"An AI designed to say NO when it matters, and back it up with data."* 🛡️
