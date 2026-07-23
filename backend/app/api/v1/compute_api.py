from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.compute.engine import compute_engine
from app.compute.node_manager import node_manager
from app.compute.partition_manager import partition_manager
from app.compute.scheduler import scheduler
from app.compute.sync_engine import sync_engine
from app.compute.storage_manager import storage_manager
from app.compute.fault_tolerance import fault_tolerance
from app.compute.reasoning_layer import reasoning_layer
from app.compute.persistence import compute_db

router = APIRouter(prefix="/api/v1/compute", tags=["Compute"])


class RegisterNodeRequest(BaseModel):
    name: str
    node_type: str = "worker"
    cpu_cores: int = 4
    gpu_count: int = 0
    memory_total_mb: float = 4096
    max_tasks: int = 10
    host: Optional[str] = None
    port: int = 0


class AssignTaskRequest(BaseModel):
    task_type: str
    description: Optional[str] = None
    priority: str = "medium"
    source: Optional[str] = None
    payload: Optional[dict] = None
    node_id: Optional[str] = None


class SetPriorityRequest(BaseModel):
    agent_id: str
    priority: str = "medium"
    reason: Optional[str] = None
    node_id: Optional[str] = None


class ReasoningTaskRequest(BaseModel):
    agent_id: str
    task_type: str
    payload: Optional[dict] = None


# --- State ---

@router.get("/state")
async def get_compute_state():
    return await compute_engine.get_full_state()


# --- Nodes ---

@router.post("/nodes")
async def register_node(request: RegisterNodeRequest):
    return await node_manager.register_node(
        name=request.name, node_type=request.node_type,
        cpu_cores=request.cpu_cores, gpu_count=request.gpu_count,
        memory_total_mb=request.memory_total_mb, max_tasks=request.max_tasks,
        host=request.host, port=request.port,
    )


@router.get("/nodes")
async def list_nodes(status: Optional[str] = None):
    return {"nodes": await node_manager.list_nodes(status)}


@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    node = await node_manager.get_node(node_id)
    if not node:
        raise HTTPException(404, "Node not found")
    caps = await compute_db.get_capabilities(node_id)
    return {**node, "capabilities": caps}


@router.delete("/nodes/{node_id}")
async def remove_node(node_id: str):
    ok = await node_manager.remove_node(node_id)
    if not ok:
        raise HTTPException(404, "Node not found")
    return {"removed": True}


@router.post("/nodes/{node_id}/heartbeat")
async def node_heartbeat(node_id: str):
    result = await node_manager.heartbeat(node_id)
    if not result:
        raise HTTPException(404, "Node not found")
    return result


# --- Partitions ---

@router.post("/partitions")
async def create_partition(partition_key: str = Query(...),
                           partition_type: str = "region",
                           universe_id: Optional[str] = None):
    return await partition_manager.create_partition(partition_key, partition_type, universe_id)


@router.get("/partitions")
async def list_partitions(node_id: Optional[str] = None):
    return {"partitions": await partition_manager.list_partitions(node_id)}


@router.post("/partitions/{partition_id}/reassign")
async def reassign_partition(partition_id: str, node_id: Optional[str] = None):
    return await partition_manager.reassign_partition(partition_id, node_id)


# --- Tasks ---

@router.post("/tasks")
async def assign_task(request: AssignTaskRequest):
    return await scheduler.assign_task(
        task_type=request.task_type, description=request.description,
        priority=request.priority, source=request.source,
        payload=request.payload, node_id=request.node_id,
    )


@router.get("/tasks")
async def list_tasks(node_id: Optional[str] = None, status: Optional[str] = None):
    return {"tasks": await scheduler.list_tasks(node_id, status)}


@router.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str, result: Optional[str] = None):
    return await scheduler.complete_task(task_id, result)


@router.post("/tasks/{task_id}/fail")
async def fail_task(task_id: str, error: Optional[str] = None):
    return await scheduler.fail_task(task_id, error)


# --- Agent Priorities ---

@router.post("/priorities")
async def set_agent_priority(request: SetPriorityRequest):
    return await scheduler.set_agent_priority(
        agent_id=request.agent_id, priority=request.priority,
        reason=request.reason, node_id=request.node_id,
    )


@router.get("/priorities")
async def list_priorities(node_id: Optional[str] = None, priority: Optional[str] = None):
    return {"priorities": await scheduler.get_agent_priorities(node_id, priority)}


# --- Reasoning ---

@router.post("/reasoning")
async def assign_reasoning(request: ReasoningTaskRequest):
    return await reasoning_layer.assign_reasoning_task(
        agent_id=request.agent_id, task_type=request.task_type,
        payload=request.payload,
    )


# --- Sync ---

@router.post("/sync")
async def trigger_sync(source_node_id: str = Query(...), target_node_id: str = Query(...),
                       sync_type: str = "state"):
    return await sync_engine.synchronize(source_node_id, target_node_id, sync_type)


@router.get("/sync/history")
async def get_sync_history(node_id: Optional[str] = None):
    return {"syncs": await sync_engine.get_sync_history(node_id)}


@router.get("/sync/clock")
async def get_clock():
    return await sync_engine.get_clock_state()


# --- Storage ---

@router.get("/storage")
async def get_storage():
    return await storage_manager.get_all_storage()


@router.get("/storage/{node_id}")
async def get_node_storage(node_id: str):
    return {"storage": await storage_manager.get_storage(node_id)}


# --- Faults ---

@router.get("/faults")
async def get_faults():
    return {"faults": await fault_tolerance.get_fault_history(), "stats": await fault_tolerance.get_fault_stats()}


# --- Workload ---

@router.get("/workload")
async def get_workload():
    return await compute_db.get_node_stats()
