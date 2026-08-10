#!/bin/bash

echo "🔥 SENTINEL SINGULARITY - 72 HOUR AUTONOMOUS EVOLUTION"
echo "=================================================="
echo "Start time: $(date)"
echo "Expected end: $(date -d '+72 hours')"
echo ""

cd /workspaces/Sentinel

# Ensure Ollama is running (failback)
echo "🔄 Ensuring Ollama 1.5B is available..."
ollama pull qwen2.5:1.5b
nohup ollama serve > ollama_singularity.log 2>&1 &

# Activate venv
source venv/bin/activate

# Run Singularity Kernel
echo "🚀 Launching Singularity Kernel..."
python << 'PYTHON'
import asyncio
from src.core.singularity_kernel import SingularityKernel
from src.core.self_audit import SelfAudit

async def main():
    kernel = SingularityKernel()
    audit = SelfAudit()
    
    # Run both in parallel
    kernel_task = asyncio.create_task(kernel.run_72_hour_loop())
    audit_task = asyncio.create_task(audit.monitor_singularity(kernel))
    
    await kernel_task
    
    # Generate final report
    report = audit.generate_audit_report(kernel)
    
    print("\n" + "="*50)
    print("🏁 SINGULARITY 72-HOUR TEST COMPLETE")
    print("="*50)
    print(f"Cycles completed: {kernel.cycle_count}")
    print(f"Mutations applied: {kernel.mutations_applied}")
    print(f"Status: {'SUCCESS' if kernel.cycle_count >= 72 else 'INTERRUPTED'}")
    print("="*50)

asyncio.run(main())
PYTHON

echo "✅ Singularity 72h evolution complete"
