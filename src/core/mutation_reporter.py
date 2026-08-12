"""
📊 MUTATION REPORTER - Generate unique reports per cycle
"""
import json
from datetime import datetime
from loguru import logger

class MutationReporter:
    def __init__(self):
        self.reports = []
    
    def generate_report(self, cycle_num, mutation_data):
        """Génère un rapport UNIQUE pour chaque mutation"""
        
        report = {
            "cycle": cycle_num,
            "timestamp": datetime.now().isoformat(),
            "mutation": {
                "type": mutation_data.get("type", "unknown"),
                "size": len(mutation_data.get("code", "")),
                "changes": mutation_data.get("changes_count", 0),
                "functions_added": mutation_data.get("functions_added", []),
                "functions_modified": mutation_data.get("functions_modified", []),
                "performance_improvement": mutation_data.get("performance_pct", 0)
            },
            "validation": {
                "syntax_valid": mutation_data.get("syntax_valid", False),
                "tests_passed": mutation_data.get("tests_passed", 0),
                "tests_failed": mutation_data.get("tests_failed", 0)
            },
            "impact": {
                "model_used": mutation_data.get("model_used", "unknown"),
                "execution_time": mutation_data.get("execution_time", 0),
                "success": mutation_data.get("success", False)
            }
        }
        
        return report
    
    def format_for_discord(self, report):
        """Formate le rapport pour Discord avec VRAIES données"""
        
        emoji = "✅" if report["impact"]["success"] else "❌"
        
        message = f"""
{emoji} **SENTINEL MUTATION #{report['cycle']}**

**Type:** {report['mutation']['type']}
**Size:** {report['mutation']['size']} bytes
**Changes:** {report['mutation']['changes']} modifications
**New Functions:** {', '.join(report['mutation']['functions_added']) or 'None'}
**Modified Functions:** {', '.join(report['mutation']['functions_modified']) or 'None'}
**Performance Gain:** +{report['mutation']['performance_improvement']}%

**Validation:**
- Syntax: {'✅' if report['validation']['syntax_valid'] else '❌'}
- Tests Passed: {report['validation']['tests_passed']}/59
- Tests Failed: {report['validation']['tests_failed']}

**Model Used:** {report['impact']['model_used']}
**Execution Time:** {report['impact']['execution_time']}s
**Status:** {'🔥 SUCCESS' if report['impact']['success'] else '⚠️ FAILED'}

Timestamp: {report['timestamp']}
"""
        return message

