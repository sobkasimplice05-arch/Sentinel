#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.core.self_audit import SelfAudit


def main():
    parser = argparse.ArgumentParser(description="Run the Sentinel self-audit wrapper from project root")
    parser.add_argument(
        "--path",
        default="src/core/self_audit.py",
        help="File or directory to audit (default: src/core/self_audit.py)",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Rewrite improved code back to files when available",
    )
    args = parser.parse_args()

    os.environ.setdefault("TEST_MODE", "true")
    orchestrator = LLMOrchestrator(test_mode=True)
    auditor = SelfAudit(orchestrator)

    target = Path(args.path)
    if target.is_dir():
        source_paths = list(target.rglob("*.py"))
    else:
        source_paths = [target]

    results = []
    for source_path in source_paths:
        result = auditor.audit_path(str(source_path), rewrite=args.rewrite)
        results.append(result)
        print(f"Audit result for {source_path}: success={result['success']} rewrite={result.get('auto_rewritten', False)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
