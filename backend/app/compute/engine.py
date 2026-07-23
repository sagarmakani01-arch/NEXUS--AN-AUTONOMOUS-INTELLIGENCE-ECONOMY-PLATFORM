import logging

from app.compute.node_manager import node_manager
from app.compute.partition_manager import partition_manager
from app.compute.scheduler import scheduler
from app.compute.sync_engine import sync_engine
from app.compute.workload_balancer import workload_balancer
from app.compute.reasoning_layer import reasoning_layer
from app.compute.storage_manager import storage_manager
from app.compute.fault_tolerance import fault_tolerance
from app.compute.persistence import compute_db

logger = logging.getLogger("nexus.compute.engine")


class ComputeEngine:
    def __init__(self):
        self._initialized = False
        self._running = False

    async def initialize(self):
        if self._initialized:
            return
        existing = await compute_db.list_nodes()
        if not existing:
            await node_manager.register_node(
                name="nexus-local-main",
                node_type="worker",
                cpu_cores=8,
                gpu_count=1,
                memory_total_mb=16384,
                max_tasks=20,
                host="127.0.0.1",
                port=8000,
            )
            await node_manager.register_node(
                name="nexus-local-reasoning",
                node_type="gpu",
                cpu_cores=4,
                gpu_count=1,
                memory_total_mb=8192,
                max_tasks=10,
                host="127.0.0.1",
                port=8001,
            )
            logger.info("Compute network initialized with 2 local nodes")
        self._initialized = True

    async def start(self):
        await self.initialize()
        self._running = True
        logger.info("Compute engine started")

    async def stop(self):
        self._running = False
        logger.info("Compute engine stopped")

    async def tick(self) -> dict:
        if not self._initialized:
            await self.initialize()

        faults = await fault_tolerance.check_health()
        balance = await workload_balancer.tick()
        clock = await sync_engine.sync_distributed_clock()

        return {
            "faults_detected": len(faults),
            "balance": balance,
            "clock_tick": clock.get("tick_count", 0),
        }

    async def get_full_state(self) -> dict:
        node_stats = await compute_db.get_node_stats()
        nodes = await compute_db.list_nodes()
        enriched_nodes = []
        for n in nodes:
            caps = await compute_db.get_capabilities(n["id"])
            enriched_nodes.append({**n, "capabilities": caps})

        return {
            "initialized": self._initialized,
            "running": self._running,
            "nodes": {
                "total": node_stats["total_nodes"],
                "online": node_stats["online_nodes"],
                "active_tasks": node_stats["total_active_tasks"],
                "list": enriched_nodes,
            },
            "partitions": await partition_manager.get_partition_stats(),
            "tasks": await scheduler.get_scheduler_stats(),
            "reasoning": await reasoning_layer.get_layer_stats(),
            "sync": await sync_engine.get_sync_stats(),
            "storage": await storage_manager.get_all_storage(),
            "faults": await fault_tolerance.get_fault_stats(),
            "clock": await sync_engine.get_clock_state(),
            "balance": await workload_balancer.get_balance_status(),
        }


compute_engine = ComputeEngine()
