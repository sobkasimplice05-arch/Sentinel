"""Benchmark de transfert minimal pour vérifier les capacités apprises de Sentinel.

Le benchmark ne prétend pas mesurer une intelligence générale. Il vérifie que la
boucle active distingue une observation pauvre d'une observation riche et qu'elle
ne recompte pas deux fois la même observation.
"""
from __future__ import annotations

import json
import tempfile
from contextlib import chdir
from pathlib import Path
from typing import Any

from feedback_learning import AdaptiveFeedback
from learning_engine import LearningEngine


CASES = (
    "quality_discrimination",
    "feedback_deduplication",
)


def run_transfer_benchmark(output_path: str | Path = "transfer_benchmark_report.json") -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="sentinel-transfer-") as directory:
        with chdir(directory):
            engine = LearningEngine()
            weak = engine.evaluate_threats({"source": "short"}, {})
            rich = engine.evaluate_threats(
                {"source_a": "A" * 1200, "source_b": "B" * 1200},
                {},
            )
            quality_passed = (
                rich["intelligence_score"] > weak["intelligence_score"]
                and rich["quality_metrics"]["content_quality"] > weak["quality_metrics"]["content_quality"]
            )

            feedback = AdaptiveFeedback(
                db_filename=Path("feedback.db"),
                state_filename=Path("feedback_state.json"),
                report_filename=Path("feedback_report.json"),
            )
            first = feedback.run_cycle(
                {"source": "stable observation " + "x" * 100},
                rich,
                {"source": "benchmark", "decision": "NO_CHANGE_NEEDED", "confidence": 0},
            )
            second = feedback.run_cycle(
                {"source": "stable observation " + "x" * 100},
                rich,
                {"source": "benchmark", "decision": "NO_CHANGE_NEEDED", "confidence": 0},
            )
            dedup_passed = first["decision"] == "PROMOTED" and second["decision"] == "NO_CHANGE_NEEDED"

    cases = {
        "quality_discrimination": {"passed": quality_passed},
        "feedback_deduplication": {"passed": dedup_passed},
    }
    passed = sum(1 for item in cases.values() if item["passed"])
    report: dict[str, Any] = {
        "benchmark": "sentinel-transfer-v1",
        "cases": cases,
        "passed": passed,
        "total": len(CASES),
        "score": round(passed / len(CASES), 6),
        "transfer_verified": passed == len(CASES),
    }
    Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_transfer_benchmark(), ensure_ascii=False, indent=2))


__all__ = ["run_transfer_benchmark"]


