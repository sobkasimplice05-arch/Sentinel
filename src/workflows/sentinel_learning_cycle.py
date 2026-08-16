import asyncio
import json
from src.core.sentinel_real_learner import SentinelRealLearner

async def main():
    try:
        learner = SentinelRealLearner()
        discoveries = await learner.autonomous_real_learning()
        with open('sentinel_web_discoveries.json', 'w') as f:
            json.dump(discoveries, f, indent=2)
        print('\n💾 Discoveries saved!')
        return 0
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
