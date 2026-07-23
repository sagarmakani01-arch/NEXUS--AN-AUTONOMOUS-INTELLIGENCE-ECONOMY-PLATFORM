import json
import logging
import random
from datetime import datetime, timezone

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.publications")


class PublicationEngine:
    def __init__(self):
        self.stats = {
            "publications_created": 0,
            "publications_published": 0,
            "total_citations": 0,
        }

    async def create_publication(self, title: str, authors: list[str],
                                 institution: str | None = None,
                                 abstract: str | None = None,
                                 knowledge_domain: str | None = None,
                                 keywords: list[str] | None = None,
                                 project_id: str | None = None) -> dict:
        impact = random.uniform(0.1, 0.8)
        quality = random.uniform(0.3, 0.9)
        novelty = random.uniform(0.2, 0.9)
        pub_id = await db.create_publication(
            title=title, abstract=abstract,
            authors=json.dumps(authors), institution=institution,
            knowledge_domain=knowledge_domain,
            keywords=json.dumps(keywords or []),
            impact_score=round(impact, 3),
            quality_score=round(quality, 3),
            novelty_score=round(novelty, 3),
            project_id=project_id,
        )
        self.stats["publications_created"] += 1
        return {
            "publication_id": pub_id, "title": title,
            "impact_score": round(impact, 3),
            "quality_score": round(quality, 3),
        }

    async def submit_for_review(self, pub_id: str) -> dict:
        pub = await db.get_publication(pub_id)
        if not pub:
            return {"success": False, "error": "Publication not found"}
        await db.update_publication(pub_id, status="submitted", peer_review_status="under_review")
        return {"success": True, "status": "submitted"}

    async def publish(self, pub_id: str) -> dict:
        pub = await db.get_publication(pub_id)
        if not pub:
            return {"success": False, "error": "Publication not found"}
        now = datetime.now(timezone.utc).isoformat()
        await db.update_publication(
            pub_id, status="published", peer_review_status="accepted",
            publication_date=now,
        )
        self.stats["publications_published"] += 1
        self.stats["total_citations"] += pub.get("citations", 0)

        if pub.get("institution"):
            orgs = await db.list_organizations()
            for org in orgs:
                if org["name"] == pub["institution"]:
                    await db.update_organization(
                        org["id"],
                        published_papers=org.get("published_papers", 0) + 1,
                    )
                    break

        await dispatch(Event(EventType.PUBLICATION_RELEASED, {
            "publication_id": pub_id, "title": pub["title"],
            "institution": pub["institution"],
            "impact_score": pub["impact_score"],
        }))
        return {"success": True, "status": "published"}

    async def add_citation(self, pub_id: str) -> dict:
        pub = await db.get_publication(pub_id)
        if not pub:
            return {"success": False}
        new_citations = pub.get("citations", 0) + 1
        new_impact = min(100, pub["impact_score"] + 0.01)
        await db.update_publication(pub_id, citations=new_citations, impact_score=round(new_impact, 3))
        return {"success": True, "citations": new_citations}

    async def get_publication(self, pub_id: str) -> dict | None:
        return await db.get_publication(pub_id)

    async def list_publications(self, institution: str | None = None,
                                knowledge_domain: str | None = None,
                                status: str | None = None) -> list[dict]:
        return await db.list_publications(institution=institution,
                                         knowledge_domain=knowledge_domain,
                                         status=status)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


publication_engine = PublicationEngine()
