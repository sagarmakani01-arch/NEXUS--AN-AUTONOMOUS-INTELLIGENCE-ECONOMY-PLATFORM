import json
import random
from datetime import datetime

from app.meta.persistence import meta_persistence
from app.domain.models.meta import KnowledgeEntry, SimulationReport


class KnowledgeBase:
    """Maintains long-term findings, patterns, best practices, and insights."""

    async def add_entry(
        self,
        title: str,
        content: str,
        entry_type: str,
        source: str = None,
        tags: list = None,
        confidence: float = 0.5,
    ) -> dict:
        entry = KnowledgeEntry(
            title=title,
            content=content,
            entry_type=entry_type,
            source=source,
            tags=json.dumps(tags or []),
            confidence=confidence,
        )
        saved = await meta_persistence.save_knowledge(entry)
        return {
            "id": saved.id,
            "title": saved.title,
            "type": saved.entry_type,
            "confidence": saved.confidence,
        }

    async def get_entries(self, entry_type: str = None) -> list[dict]:
        entries = await meta_persistence.get_knowledge(entry_type)
        return [
            {
                "id": e.id,
                "title": e.title,
                "content": e.content,
                "type": e.entry_type,
                "source": e.source,
                "tags": e.tags,
                "confidence": e.confidence,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ]

    async def generate_report(
        self,
        title: str,
        report_type: str = "analysis",
        content: str = None,
        data: dict = None,
        simulation_ids: list = None,
    ) -> dict:
        report = SimulationReport(
            title=title,
            report_type=report_type,
            content=content or f"Auto-generated {report_type} report",
            data=json.dumps(data or {}),
            simulation_ids=json.dumps(simulation_ids or []),
        )
        saved = await meta_persistence.save_report(report)
        return {
            "id": saved.id,
            "title": saved.title,
            "type": saved.report_type,
        }

    async def get_reports(self, report_type: str = None) -> list[dict]:
        reports = await meta_persistence.get_reports(report_type)
        return [
            {
                "id": r.id,
                "title": r.title,
                "type": r.report_type,
                "content": r.content,
                "simulation_ids": r.simulation_ids,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in reports
        ]

    async def record_insight(self, insight_text: str, source: str = None) -> dict:
        return await self.add_entry(
            title=f"Insight: {insight_text[:80]}",
            content=insight_text,
            entry_type="insight",
            source=source,
            tags=["insight", "automated"],
            confidence=0.6,
        )

    async def get_stats(self) -> dict:
        entries = await self.get_entries()
        reports = await self.get_reports()
        types = {}
        for e in entries:
            t = e["type"]
            types[t] = types.get(t, 0) + 1
        return {
            "total_entries": len(entries),
            "total_reports": len(reports),
            "entry_types": types,
        }


knowledge_base = KnowledgeBase()
