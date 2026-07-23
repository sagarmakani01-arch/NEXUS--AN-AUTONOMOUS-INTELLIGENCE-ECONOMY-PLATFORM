import json

from app.temporal.persistence import temporal_persistence


class HistoricalAnalyticsEngine:
    """Generates analytical summaries of historical data."""

    async def most_influential_events(self, clock_id: str, timeline_id: str = None, limit: int = 10) -> dict:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=1000
        )
        sorted_events = sorted(events, key=lambda e: e.impact_score, reverse=True)[:limit]
        result = [
            {
                "id": e.id,
                "type": e.event_type,
                "title": e.title,
                "impact": e.impact_score,
                "year": e.year_occurred,
                "tick": e.tick_occurred,
            }
            for e in sorted_events
        ]
        await temporal_persistence.save_analytics(
            analytics_type="influential_events",
            title=f"Top {limit} Most Influential Events",
            data={"events": result},
            timeline_id=timeline_id,
        )
        return {"events": result, "count": len(result)}

    async def event_type_distribution(self, clock_id: str, timeline_id: str = None) -> dict:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=10000
        )
        distribution = {}
        for e in events:
            distribution[e.event_type] = distribution.get(e.event_type, 0) + 1

        sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        result = [{"type": t, "count": c} for t, c in sorted_dist]

        await temporal_persistence.save_analytics(
            analytics_type="event_distribution",
            title="Event Type Distribution",
            data={"distribution": result, "total_events": len(events)},
            timeline_id=timeline_id,
        )
        return {"distribution": result, "total_events": len(events)}

    async def timeline_summary(self, clock_id: str, timeline_id: str = None) -> dict:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=10000
        )
        if not events:
            return {"summary": "No events recorded"}

        first_event = events[0]
        last_event = events[-1]
        years_span = (last_event.year_occurred or 0) - (first_event.year_occurred or 0)

        unique_locations = set()
        unique_participants = set()
        for e in events:
            if e.location:
                unique_locations.add(e.location)
            if e.participants:
                try:
                    p_list = json.loads(e.participants) if isinstance(e.participants, str) else e.participants
                    if isinstance(p_list, list):
                        unique_participants.update(p_list)
                except (json.JSONDecodeError, TypeError):
                    pass

        avg_impact = sum(e.impact_score for e in events) / len(events)

        summary = {
            "total_events": len(events),
            "years_span": years_span,
            "events_per_year": len(events) / max(1, years_span),
            "first_event": {"title": first_event.title, "year": first_event.year_occurred},
            "last_event": {"title": last_event.title, "year": last_event.year_occurred},
            "unique_locations": len(unique_locations),
            "unique_participants": len(unique_participants),
            "average_impact_score": round(avg_impact, 2),
        }

        await temporal_persistence.save_analytics(
            analytics_type="timeline_summary",
            title="Timeline Summary",
            data=summary,
            timeline_id=timeline_id,
        )
        return summary

    async def era_analysis(self, clock_id: str, timeline_id: str = None) -> dict:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=10000
        )
        if not events:
            return {"eras": []}

        eras = []
        era_size = 50
        min_year = min(e.year_occurred for e in events if e.year_occurred)
        max_year = max(e.year_occurred for e in events if e.year_occurred)

        for era_start in range(min_year, max_year + 1, era_size):
            era_end = era_start + era_size
            era_events = [
                e for e in events
                if e.year_occurred and era_start <= e.year_occurred < era_end
            ]
            if era_events:
                type_counts = {}
                for e in era_events:
                    type_counts[e.event_type] = type_counts.get(e.event_type, 0) + 1
                eras.append({
                    "start_year": era_start,
                    "end_year": era_end,
                    "event_count": len(era_events),
                    "top_event_type": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None,
                    "avg_impact": sum(e.impact_score for e in era_events) / len(era_events),
                })

        await temporal_persistence.save_analytics(
            analytics_type="era_analysis",
            title="Era Analysis",
            data={"eras": eras},
            timeline_id=timeline_id,
        )
        return {"eras": eras, "total_eras": len(eras)}

    async def milestone_detection(self, clock_id: str, timeline_id: str = None, threshold: float = 0.7) -> dict:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=10000
        )
        milestones = [
            {
                "id": e.id,
                "type": e.event_type,
                "title": e.title,
                "impact": e.impact_score,
                "year": e.year_occurred,
                "tick": e.tick_occurred,
            }
            for e in events
            if e.impact_score >= threshold
        ]
        milestones.sort(key=lambda x: x["impact"], reverse=True)

        await temporal_persistence.save_analytics(
            analytics_type="milestones",
            title=f"Milestones (impact >= {threshold})",
            data={"milestones": milestones},
            timeline_id=timeline_id,
        )
        return {"milestones": milestones, "count": len(milestones)}


historical_analytics = HistoricalAnalyticsEngine()
