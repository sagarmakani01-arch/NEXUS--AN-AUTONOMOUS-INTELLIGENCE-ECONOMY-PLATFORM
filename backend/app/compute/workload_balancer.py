import random

from app.compute.persistence import compute_db


class WorkloadBalancer:
    async def tick(self) -> dict:
        nodes = await compute_db.list_nodes("online")
        actions = []

        for node in nodes:
            cpu = node["cpu_usage"] or 0
            mem = node["memory_used_mb"] or 0
            mem_total = node["memory_total_mb"] or 1
            load = (cpu + (mem / mem_total * 100)) / 2

            await compute_db.record_workload(
                node_id=node["id"],
                cpu_usage=cpu,
                memory_usage=round(mem / mem_total, 3),
                active_tasks=node["active_tasks"] or 0,
                queue_depth=random.randint(0, 5),
                avg_tick_time_ms=round(random.uniform(10, 200), 1),
            )

            if load > 70:
                await self._rebalance_node(node["id"])
                actions.append({"node": node["name"], "action": "rebalanced", "load": round(load, 1)})

        return {
            "nodes_checked": len(nodes),
            "actions": actions,
            "avg_load": round(sum(
                (n["cpu_usage"] or 0) for n in nodes
            ) / max(1, len(nodes)), 1),
        }

    async def _rebalance_node(self, node_id: str) -> None:
        partitions = await compute_db.get_partitions(node_id)
        for p in partitions:
            other = await compute_db.get_available_node()
            if other and other["id"] != node_id:
                await compute_db.update_partition(
                    p["id"], node_id=other["id"])

    async def get_balance_status(self) -> dict:
        nodes = await compute_db.list_nodes()
        loads = []
        for n in nodes:
            mem_total = n["memory_total_mb"] or 1
            load = ((n["cpu_usage"] or 0) + ((n["memory_used_mb"] or 0) / mem_total * 100)) / 2
            loads.append({"node_id": n["id"], "name": n["name"], "load": round(load, 1)})
        avg = sum(l["load"] for l in loads) / max(1, len(loads))
        return {
            "loads": loads,
            "average_load": round(avg, 1),
            "high_load_nodes": [l for l in loads if l["load"] > 70],
            "total_nodes": len(nodes),
        }


workload_balancer = WorkloadBalancer()
