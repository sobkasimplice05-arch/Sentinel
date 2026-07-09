# 🛡️ SENTINEL - One AI to rule them all

## What is SENTINEL?

Multi-IA orchestrator that:
- Routes to best AI for each task
- Validates responses through 5 quality gates
- Corrects grammar in input AND output
- Learns from every execution
- Logs everything for auditability
- Costs $0 (100% free)

## Components

- Grammar Corrector (Input & Output)
- Instruction Parser
- Task Classifier  
- Model Router (Local-First)
- LLM Orchestrator
- Quality Gate (5 checkers)
- Accuracy Coach
- Transparency Logger
- REST API
- Web UI

## Quick Start

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Run REST API
```bash
python -m uvicorn src.api.app:app --reload
# http://localhost:8000
```

### Run Web UI
```bash
streamlit run streamlit_app.py
```

## Cost: $0

100% free - no API costs

## Features

✅ Multi-model routing
✅ Quality assurance (5 layers)
✅ Learning system
✅ Complete auditability

## Testing

```bash
pytest tests/test_complete_system.py -v
```

## License

MIT License

---

"One AI to rule them all" - SENTINEL
