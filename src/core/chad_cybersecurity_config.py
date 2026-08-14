"""
🇹🇩 CHAD CYBERSECURITY CONFIG
Pour la souveraineté numérique tchadienne
"""

TARGETS = {
    "government_servers": [
        # Serveurs de l'administration tchadienne
        "192.168.x.x",  # À configurer
        "10.0.x.x"      # À configurer
    ],
    "critical_infrastructure": [
        # Banques, électricité, eau, etc.
        # À configurer par l'État tchadien
    ]
}

THREAT_LEVELS = {
    "critical": {"color": "red", "auto_patch": True, "notify": "immediate"},
    "high": {"color": "orange", "auto_patch": True, "notify": "1hour"},
    "medium": {"color": "yellow", "auto_patch": False, "notify": "1day"},
    "low": {"color": "green", "auto_patch": False, "notify": "weekly"}
}

EVOLUTION_TARGETS = [
    "intrusion_detection",
    "vulnerability_scanning",
    "patch_generation",
    "anomaly_detection",
    "incident_response",
    "threat_intelligence"
]

