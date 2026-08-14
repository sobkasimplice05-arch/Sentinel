"""
🌐 SIMULATED INTERNET - Fake but realistic internet access
"""
import json
import asyncio
import random
from datetime import datetime
from loguru import logger

class SimulatedInternet:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.threat_db = self._load_threat_database()
        logger.info("🌐 Simulated Internet initialized")
    
    def _load_knowledge_base(self):
        return {
            "cve_database": {
                "CVE-2024-001": {"severity": "critical", "description": "Buffer overflow"},
                "CVE-2024-002": {"severity": "high", "description": "SQL injection"},
            },
            "threat_intel": {
                "known_ips": ["192.168.1.100", "10.0.0.50"],
                "malware_hashes": ["d41d8cd98f00b204e9800998ecf8427e"],
            }
        }
    
    def _load_threat_database(self):
        return {
            "active_threats": [
                {"id": "threat-001", "type": "brute_force", "severity": "high"},
                {"id": "threat-002", "type": "sql_injection", "severity": "critical"},
            ]
        }
    
    async def search_vulnerability(self, query):
        logger.info(f"🔍 Searching: {query}")
        await asyncio.sleep(random.uniform(0.5, 1))
        return [
            {"cve": "CVE-2024-001", "score": 9.8},
            {"cve": "CVE-2024-002", "score": 8.5},
        ]
    
    async def fetch_threat_intelligence(self):
        logger.info("📡 Fetching threat intelligence")
        await asyncio.sleep(random.uniform(1, 2))
        return self.threat_db["active_threats"]
    
    async def generate_fake_logs(self, server_type="web"):
        logger.info(f"📋 Generating logs for {server_type}")
        logs = """
[2024-08-14 10:23:45] Failed password for admin from 192.168.1.100
[2024-08-14 10:24:12] Failed password for admin from 192.168.1.100
[2024-08-14 10:25:01] SQL Error: Unexpected token
[2024-08-14 10:26:33] Port scan detected from 10.0.0.50
"""
        return logs

