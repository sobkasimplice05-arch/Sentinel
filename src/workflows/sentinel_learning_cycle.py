"""Lance un cycle d'apprentissage réel et persiste les découvertes."""
from __future__ import annotations

import asyncio
import json

from src.core.sentinel_real_learner import SentinelRealLearner


async def main() -> int:
    try:
        learner = SentinelRealLearner()
        discoveries = await learner.autonomous_real_learning()
        with open("sentinel_web_discoveries.json", "w", encoding="utf-8") as handle:
            json.dump(discoveries, handle, indent=2, ensure_ascii=False)
        print("\nDécouvertes sauvegardées.")
        return 0
    except Exception as error:
        print(f"\nErreur : {error}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))


__all__ = ["main"]
