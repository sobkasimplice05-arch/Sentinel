#!/bin/bash

echo "🔥 SENTINEL SINGULARITY - 72 HOUR AUTONOMOUS EVOLUTION"
echo "Start: $(date)"
echo ""

cd /workspaces/Sentinel

# Ensure Ollama 1.5B
echo "📦 Pulling Ollama 1.5B model..."
ollama pull qwen2.5:1.5b

echo "🔄 Starting Ollama service..."
nohup ollama serve > ollama_singularity.log 2>&1 &
sleep 2

# Activate venv
source venv/bin/activate

# Run Singularity
echo "🚀 Launching Singularity Kernel..."
python << 'PYTHON'
import asyncio
from src.core.singularity_kernel import SingularityKernel
from src.core.self_audit import SelfAudit

async def main():
    kernel = SingularityKernel()
    audit = SelfAudit()
    
    kernel_task = asyncio.create_task(kernel.run_72_hour_loop())
    await kernel_task
    
    report = audit.generate_audit_report(kernel)
    
    print("\n" + "="*50)
    print("🏁 SINGULARITY 72-HOUR TEST COMPLETE")
    print("="*50)
    print(f"Cycles: {kernel.cycle_count}")
    print(f"Mutations: {kernel.mutations_applied}")
    print("="*50)

asyncio.run(main())
PYTHON

echo "✅ 72h evolution ended at $(date)"
