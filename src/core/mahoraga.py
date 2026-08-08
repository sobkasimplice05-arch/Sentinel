"""MAHORAGA - Adaptation infinie | OUROBOROS - Auto-évolution"""
import json, os
from pathlib import Path
from loguru import logger

STATE_FILE = "sentinel_evolution_state.json"

class Mahoraga:
    def __init__(self):
        self.state = self._load()
        logger.info("⚔️ Mahoraga Protocol: Adaptation active")

    def _load(self):
        if Path(STATE_FILE).exists():
            try:
                return json.load(open(STATE_FILE))
            except Exception:
                pass
        return {"weights": {}, "thresholds": {"quality": 0.75}}

    def _save(self):
        try:
            json.dump(self.state, open(STATE_FILE, "w"), indent=2)
        except Exception as e:
            logger.warning(f"Mahoraga save failed: {e}")

    def adapt(self, model_used, quality_score, task_type="general"):
        """Sukuna's Domain: chaque exécution renforce ou punit"""
        try:
            w = self.state["weights"].setdefault(model_used, 1.0)
            self.state["weights"][model_used] = round(
                w * (1.08 if quality_score >= 0.9 else 0.94), 4
            )
            if quality_score < 0.6:
                self.state["thresholds"]["quality"] = max(
                    0.5, self.state["thresholds"]["quality"] - 0.01
                )
            elif quality_score >= 0.95:
                self.state["thresholds"]["quality"] = min(
                    0.95, self.state["thresholds"]["quality"] + 0.005
                )
            self._save()
        except Exception as e:
            logger.warning(f"Mahoraga adapt failed (non-blocking): {e}")

    def best_model(self, fallback="qwen2.5:0.5b"):
        if not self.state["weights"]:
            return fallback
        return max(self.state["weights"], key=self.state["weights"].get)

mahoraga = Mahoraga()
