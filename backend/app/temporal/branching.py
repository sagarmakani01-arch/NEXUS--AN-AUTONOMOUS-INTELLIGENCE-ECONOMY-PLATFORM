import json
from typing import Optional

from app.temporal.persistence import temporal_persistence
from app.temporal.snapshots import snapshot_manager


class TimelineManager:
    """Manages timeline branching and alternate futures."""

    def __init__(self):
        self._active_branch: Optional[str] = None

    async def create_branch(
        self,
        clock_id: str,
        name: str,
        description: str = None,
        branch_point_tick: int = None,
        divergence_cause: str = None,
    ) -> dict:
        clock = await temporal_persistence.get_clock(clock_id)
        if not clock:
            return {"error": "Clock not found"}

        if branch_point_tick is None:
            branch_point_tick = clock.tick_count

        snapshot = await snapshot_manager.get_closest(clock_id, branch_point_tick)
        branch_state = snapshot.get("full_state", {}) if snapshot else {}

        branch = await temporal_persistence.create_timeline(
            name=name,
            description=description,
            branch_point_tick=branch_point_tick,
            branch_point_year=clock.current_year,
            divergence_cause=divergence_cause,
        )

        await snapshot_manager.capture(
            clock_id=clock_id,
            tick=branch_point_tick,
            year=clock.current_year,
            world_state=branch_state,
            label=f"Branch point for {name}",
            timeline_id=branch.id,
        )

        self._active_branch = branch.id

        return {
            "branch_id": branch.id,
            "name": branch.name,
            "branch_point_tick": branch_point_tick,
            "branch_point_year": clock.current_year,
            "divergence_cause": divergence_cause,
        }

    async def get_branch(self, branch_id: str) -> Optional[dict]:
        timeline = await temporal_persistence.get_timeline(branch_id)
        if not timeline:
            return None
        return {
            "id": timeline.id,
            "name": timeline.name,
            "description": timeline.description,
            "parent_timeline_id": timeline.parent_timeline_id,
            "branch_point_tick": timeline.branch_point_tick,
            "branch_point_year": timeline.branch_point_year,
            "divergence_cause": timeline.divergence_cause,
            "event_count": timeline.event_count,
            "status": timeline.status,
        }

    async def list_branches(self, parent_id: str = None) -> list[dict]:
        timelines = await temporal_persistence.get_timelines(parent_id)
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "branch_point_tick": t.branch_point_tick,
                "branch_point_year": t.branch_point_year,
                "divergence_cause": t.divergence_cause,
                "event_count": t.event_count,
                "status": t.status,
            }
            for t in timelines
        ]

    async def get_branch_tree(self, clock_id: str) -> dict:
        all_timelines = await temporal_persistence.get_timelines()
        tree = {"trunk": None, "branches": []}

        trunk_events = await temporal_persistence.count_events(clock_id)
        tree["trunk"] = {
            "id": None,
            "name": "Main Timeline",
            "event_count": trunk_events,
            "children": [],
        }

        def build_tree(parent_id, node):
            children = [t for t in all_timelines if t.parent_timeline_id == parent_id]
            for child in children:
                child_node = {
                    "id": child.id,
                    "name": child.name,
                    "event_count": child.event_count,
                    "branch_point_tick": child.branch_point_tick,
                    "divergence_cause": child.divergence_cause,
                    "children": [],
                }
                node["children"].append(child_node)
                build_tree(child.id, child_node)

        build_tree(None, tree["trunk"])

        return tree

    async def compare_branches(self, branch_a_id: str, branch_b_id: str, clock_id: str) -> dict:
        branch_a = await temporal_persistence.get_timeline(branch_a_id)
        branch_b = await temporal_persistence.get_timeline(branch_b_id)

        if not branch_a or not branch_b:
            return {"error": "One or both branches not found"}

        events_a = await temporal_persistence.get_events(clock_id, branch_a_id, limit=1000)
        events_b = await temporal_persistence.get_events(clock_id, branch_b_id, limit=1000)

        type_counts_a = {}
        type_counts_b = {}
        for e in events_a:
            type_counts_a[e.event_type] = type_counts_a.get(e.event_type, 0) + 1
        for e in events_b:
            type_counts_b[e.event_type] = type_counts_b.get(e.event_type, 0) + 1

        all_types = set(list(type_counts_a.keys()) + list(type_counts_b.keys()))

        comparison = {}
        for t in all_types:
            comparison[t] = {
                "branch_a": type_counts_a.get(t, 0),
                "branch_b": type_counts_b.get(t, 0),
                "difference": type_counts_a.get(t, 0) - type_counts_b.get(t, 0),
            }

        return {
            "branch_a": {"id": branch_a.id, "name": branch_a.name, "events": len(events_a)},
            "branch_b": {"id": branch_b.id, "name": branch_b.name, "events": len(events_b)},
            "comparison": comparison,
            "summary": {
                "total_events_a": len(events_a),
                "total_events_b": len(events_b),
                "event_types_compared": len(all_types),
            },
        }

    def set_active_branch(self, branch_id: str):
        self._active_branch = branch_id

    def get_active_branch(self) -> Optional[str]:
        return self._active_branch

    def get_state(self) -> dict:
        return {
            "active_branch": self._active_branch,
        }


timeline_manager = TimelineManager()
