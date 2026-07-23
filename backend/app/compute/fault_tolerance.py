import json
import random

from app.compute.persistence import compute_db


class FaultTolerance:
    FAULT_TYPES = ["node_crash", "network_failure", "storage_failure", "task_timeout", "data_corruption"]

    async def check_health(self) -> list[dict]:
        nodes = await compute_db.list_nodes("online")
        faults = []
        for node in nodes:
            if random.random() < 0.02:
                fault_type = random.choice(self.FAULT_TYPES)
                partitions = await compute_db.get_partitions(node["id"])
                fault = await compute_db.record_fault(
                    node_id=node["id"],
                    fault_type=fault_type,
                    severity=random.choice(["warning", "critical"]),
                    description=f"{fault_type.replace('_', ' ').title()} detected on {node['name']}",
                    affected_partitions=json.dumps([p["partition_key"] for p in partitions[:3]]),
                    recovery_action=f"Auto-recovery initiated for {fault_type}",
                )
                faults.append(fault)
                await self._recover(fault["id"], node["id"])
        return faults

    async def _recover(self, fault_id: str, node_id: str) -> None:
        partitions = await compute_db.get_partitions(node_id)
        for p in partitions:
            other = await compute_db.get_available_node()
            if other:
                await compute_db.update_partition(p["id"], node_id=other["id"])
        from datetime import datetime
        await compute_db.update_fault_recovered(fault_id, datetime.utcnow())

    async def get_fault_history(self) -> list[dict]:
        return await compute_db.get_faults()

    async def get_fault_stats(self) -> dict:
        faults = await compute_db.get_faults()
        total = len(faults)
        recovered = len([f for f in faults if f["recovered"]])
        by_severity: dict[str, int] = {}
        for f in faults:
            by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1
        return {
            "total_faults": total,
            "recovered": recovered,
            "unresolved": total - recovered,
            "by_severity": by_severity,
        }


fault_tolerance = FaultTolerance()
