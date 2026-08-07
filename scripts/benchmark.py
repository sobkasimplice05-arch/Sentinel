"""📊 BENCHMARK - Performance testing"""
from src.sentinel_main import Sentinel
from loguru import logger
import time
import statistics

def benchmark():
    logger.info("\n" + "="*70)
    logger.info("📊 SENTINEL BENCHMARKING")
    logger.info("="*70 + "\n")
    
    sentinel = Sentinel()
    
    test_cases = [
        "Explain machine learning",
        "Write fibonacci function",
        "What is Python",
    ]
    
    times = []
    quality_scores = []
    
    for i, instruction in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/{len(test_cases)}] {instruction}")
        
        start = time.time()
        result = sentinel.execute(instruction)
        elapsed = time.time() - start
        
        times.append(elapsed)
        quality_scores.append(result.get('quality_score', 0.5))
        
        logger.info(f"   Time: {elapsed:.2f}s")
        logger.info(f"   Quality: {result.get('quality_score', 0):.0%}")
    
    logger.info("\n" + "="*70)
    logger.info("📊 BENCHMARK RESULTS")
    logger.info("="*70)
    logger.info(f"Total executions: {len(times)}")
    logger.info(f"Avg time: {statistics.mean(times):.2f}s")
    logger.info(f"Min time: {min(times):.2f}s")
    logger.info(f"Max time: {max(times):.2f}s")
    logger.info(f"Avg quality: {statistics.mean(quality_scores):.0%}")
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    benchmark()
