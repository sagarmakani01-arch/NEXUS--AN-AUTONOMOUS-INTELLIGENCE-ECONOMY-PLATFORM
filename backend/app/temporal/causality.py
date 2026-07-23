from typing import Optional

from app.temporal.persistence import temporal_persistence


class CausalityEngine:
    """Tracks cause-and-effect relationships between historical events."""

    def __init__(self):
        self._pending_edges: list[dict] = []

    async def record_cause(
        self,
        source_event_id: str,
        target_event_id: str,
        relationship_type: str,
        strength: float = 0.5,
        description: str = None,
    ) -> dict:
        edge = await temporal_persistence.create_causal_edge(
            source_event_id=source_event_id,
            target_event_id=target_event_id,
            relationship_type=relationship_type,
            strength=strength,
            description=description,
        )

        self._pending_edges.append({
            "source": source_event_id,
            "target": target_event_id,
            "type": relationship_type,
        })

        return {
            "id": edge.id,
            "source": source_event_id,
            "target": target_event_id,
            "relationship": relationship_type,
            "strength": strength,
        }

    async def get_effects(self, event_id: str) -> list[dict]:
        edges = await temporal_persistence.get_causal_edges(event_id)
        return [
            {
                "id": e.id,
                "source": e.source_event_id,
                "target": e.target_event_id,
                "relationship": e.relationship_type,
                "strength": e.strength,
                "description": e.description,
            }
            for e in edges
            if e.source_event_id == event_id
        ]

    async def get_causes(self, event_id: str) -> list[dict]:
        edges = await temporal_persistence.get_causal_edges(event_id)
        return [
            {
                "id": e.id,
                "source": e.source_event_id,
                "target": e.target_event_id,
                "relationship": e.relationship_type,
                "strength": e.strength,
                "description": e.description,
            }
            for e in edges
            if e.target_event_id == event_id
        ]

    async def get_causal_chain(self, event_id: str, depth: int = 5) -> dict:
        chain = await temporal_persistence.get_causal_chain(event_id, depth)

        nodes = set()
        edges = []
        for e in chain:
            nodes.add(e.source_event_id)
            nodes.add(e.target_event_id)
            edges.append({
                "source": e.source_event_id,
                "target": e.target_event_id,
                "relationship": e.relationship_type,
                "strength": e.strength,
            })

        return {
            "root": event_id,
            "nodes": list(nodes),
            "edges": edges,
            "depth": len(chain),
        }

    async def find_cascade(
        self,
        event_id: str,
        max_depth: int = 10,
        min_strength: float = 0.3,
    ) -> list[dict]:
        cascade = []
        visited = set()
        queue = [(event_id, 0)]

        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth >= max_depth:
                continue
            visited.add(current)

            effects = await self.get_effects(current)
            for effect in effects:
                if effect["strength"] >= min_strength:
                    cascade.append({
                        "from": current,
                        "to": effect["target"],
                        "type": effect["relationship"],
                        "strength": effect["strength"],
                        "depth": depth + 1,
                    })
                    queue.append((effect["target"], depth + 1))

        return cascade

    async def get_graph_stats(self, clock_id: str) -> dict:
        from app.temporal.persistence import temporal_persistence as tp

        events = await tp.get_events(clock_id, limit=10000)
        all_edges = []

        for event in events[:100]:
            edges = await temporal_persistence.get_causal_edges(event.id)
            all_edges.extend(edges)

        type_counts = {}
        for e in all_edges:
            type_counts[e.relationship_type] = type_counts.get(e.relationship_type, 0) + 1

        return {
            "total_events": len(events),
            "total_edges_sampled": len(all_edges),
            "relationship_types": type_counts,
            "avg_strength": (
                sum(e.strength for e in all_edges) / len(all_edges) if all_edges else 0
            ),
        }

    def get_pending_count(self) -> int:
        return len(self._pending_edges)


causality_engine = CausalityEngine()
