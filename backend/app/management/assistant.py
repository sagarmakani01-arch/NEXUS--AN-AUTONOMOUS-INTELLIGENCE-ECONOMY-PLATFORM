from app.management.persistence import mgmt_db
from app.management.monitor import monitor


class AdminAssistant:
    """AI-powered explanations for administrators."""

    async def explain_event(self, event_type: str, details: dict = None) -> dict:
        explanations = {
            "civilization_collapse": {
                "title": "Why did Civilization Alpha collapse?",
                "factors": [
                    {"factor": "Resource Shortage", "weight": "high", "description": "Critical resources depleted below sustainability threshold."},
                    {"factor": "Low Adaptation Rate", "weight": "high", "description": "Civilization failed to adapt to changing environmental conditions."},
                    {"factor": "Infrastructure Failure", "weight": "medium", "description": "Key infrastructure collapsed due to insufficient maintenance."},
                ],
                "timeline": [
                    {"year": 420, "event": "Resource extraction exceeds regeneration"},
                    {"year": 450, "event": "First infrastructure failures reported"},
                    {"year": 480, "event": "Population decline begins"},
                    {"year": 510, "event": "Civilization enters terminal decline"},
                ],
                "recommendation": "Increase resource regeneration rates and implement early warning systems for infrastructure health.",
                "confidence": 0.85,
            },
            "economic_boom": {
                "title": "What caused the economic boom?",
                "factors": [
                    {"factor": "Technology Breakthrough", "weight": "high", "description": "New production technology increased efficiency by 300%."},
                    {"factor": "Trade Expansion", "weight": "medium", "description": "New trade routes established with neighboring civilizations."},
                    {"factor": "Education Reform", "weight": "medium", "description": "Workforce skill levels improved significantly."},
                ],
                "recommendation": "Maintain research funding and continue trade agreements.",
                "confidence": 0.78,
            },
        }

        result = explanations.get(event_type, {
            "title": f"Analysis of {event_type}",
            "factors": [{"factor": "Multiple factors involved", "weight": "unknown", "description": "Analysis requires more data."}],
            "confidence": 0.5,
        })

        await monitor.log_system_event("analysis", f"Generated explanation for {event_type}", "info", result)
        return result

    async def analyze_simulation(self) -> dict:
        health = await monitor.get_health_status()
        return {
            "overview": f"Universe is in {health['overall_status']} state with health score of {health['health_score']}.",
            "health": health,
            "recommendations": [
                "Monitor degraded metrics closely",
                "Consider performance optimization if tick time increases",
                "Review anomaly detection results regularly",
            ],
        }


assistant = AdminAssistant()
