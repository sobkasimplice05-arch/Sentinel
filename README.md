# 🛡️ SENTINEL
**One AI to rule them all** - Transparent, Secure, Honest AI Orchestrator

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](#)

---

## 🎯 Mission

Build an AI that refuses to flatter you, admits its limits, and routes you to a human when it matters.

Most AI assistants optimize for user satisfaction. Sentinel optimizes for **honesty**.

---

## ✨ Core Features

✅ **100% Auditable** - Every decision logged in JSON  
✅ **Multi-IA Orchestration** - Route to best model per task  
✅ **Grammar Correction** - Input & output cleaned automatically  
✅ **5-Layer Quality Gate** - Syntax, Logic, Security, Hallucination, Completeness  
✅ **Local-First** - Zero cloud, zero tracking, zero costs  
✅ **Zero API Costs** - $0 forever (Ollama + open-source)  

---

## 🚀 Quick Start

### Requirements
- Python 3.11+
- Windows 11 / Mac / Linux
- 4GB+ RAM
- Ollama installed

### Installation

```bash
# Clone
git clone https://github.com
cd Sentinel

# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or: source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run
python src/main.py
```

### API

```bash
# Start server
python -m uvicorn src.api.app:app --reload

# Access: http://localhost:8000/docs
```

### UI

```bash
# Start Streamlit
streamlit run streamlit_app.py

# Access: http://localhost:8501
```

---

## 📊 Architecture
User Input
↓
Grammar Corrector (Input)
↓
Instruction Parser → Task Classifier → Model Router
↓
LLM Execution (Local via Ollama)
↓
Quality Gate (5 checks)
↓
Grammar Corrector (Output)
↓
Accuracy Coach (Feedback)
↓
Transparency Logger
↓
User Gets Perfect Response

---

## 📋 Roadmap (15 Tasks)

- [x] Task 0: Repo Setup
- [ ] Task 0.5: Grammar Corrector
- [ ] Task 1-4: Core Engine
- [ ] Task 5-9: Quality Gate
- [ ] Task 10-12: Orchestration
- [ ] Task 13-15: Interfaces & Testing

See [TASKS.md](docs/TASKS.md) for details.

---

## 💾 Tech Stack

- **Backend:** FastAPI, Python 3.11+
- **LLM:** Ollama (local models)
- **Models:** Mistral 7B, Qwen 7B, Phi 2.7B
- **Frontend:** Streamlit, Claude Code
- **Quality:** Hugging Face Transformers, spaCy
- **Logging:** Loguru, JSON
- **Repo:** GitHub + Actions

**Cost:** $0

---

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development Tasks](docs/TASKS.md)
- [API Reference](docs/API.md)
- [Configuration](docs/CONFIG.md)
- [Session Logs](docs/SESSION_LOG.md)

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 👤 Created By

[SOBKA PATALE SIMPLICE](https://github.com)

---

## 🔗 Resources

- [Ollama Docs](https://ollama.ai/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Hugging Face](https://huggingface.co/)

---

**"An AI that says NO and owns it."** 🛡️
