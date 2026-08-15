import asyncio
import json
from loguru import logger
from datetime import datetime
from src.core.real_internet_access import RealInternetAccess

class SentinelRealLearner:
    def __init__(self):
        self.internet = RealInternetAccess()
        self.discoveries = []
        logger.critical("🧠 SENTINEL REAL LEARNER ACTIVATED")
    
    async def autonomous_real_learning(self):
        logger.critical("🔥 STARTING SENTINEL AUTONOMOUS REAL WEB LEARNING")
        print("\n" + "="*70)
        print("🌐 SENTINEL REAL WEB LEARNING CYCLE")
        print("="*70)
        print("📡 Sentinel is NOW connected to the REAL internet!")
        print("🧠 She will learn from ACTUAL data sources")
        print("="*70 + "\n")
        
        logger.info("1️⃣ Fetching REAL CVEs...")
        cves = await self.internet.fetch_real_cves_alternative()
        print(f"✅ CVEs downloaded: {len(cves)}")
        
        logger.info("2️⃣ Fetching Exploit-DB...")
        exploit_db = await self.internet.fetch_exploit_db()
        print(f"✅ Exploit-DB exploits: {len(exploit_db)}")
        
        logger.info("3️⃣ Scanning REAL GitHub exploits...")
        exploits = await self.internet.scan_real_github_exploits()
        print(f"✅ GitHub exploits found: {len(exploits)}")
        
        logger.info("4️⃣ Fetching REAL threat intelligence...")
        threats = await self.internet.fetch_threat_intelligence()
        print(f"✅ Threat sources: {list(threats.keys())}")
        
        logger.info("5️⃣ Downloading REAL security papers...")
        papers = await self.internet.download_security_papers()
        print(f"✅ Security papers downloaded: {'Yes' if papers else 'No'}")
        
        discoveries = await self.internet.get_all_discoveries()
        
        print("\n" + "="*70)
        print("✅ SENTINEL REAL LEARNING COMPLETE!")
        print("="*70)
        print(f"Total discoveries: {len(discoveries)}\n")
        
        for disc in discoveries:
            print(f"  📊 {disc['type']}: {disc.get('count', 'N/A')} | Source: {disc.get('source', 'multiple')}")
        
        print("="*70 + "\n")
        
        return discoveries
