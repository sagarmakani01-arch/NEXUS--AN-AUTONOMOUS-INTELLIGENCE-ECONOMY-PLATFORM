from __future__ import annotations

import asyncio
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.reasoning.queue")


@dataclass
class ReasoningTask:
    task_id: str
    agent_id: str
    trigger_type: str
    trigger_id: str
    priority: int = 5
    context: dict = field(default_factory=dict)
    status: str = "queued"
    result: dict | None = None
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "trigger_type": self.trigger_type,
            "trigger_id": self.trigger_id,
            "priority": self.priority,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "latency_ms": round((self.completed_at - self.started_at) * 1000, 1)
            if self.completed_at and self.started_at
            else None,
        }


class ReasoningQueue:
    def __init__(
        self,
        max_size: int = 500,
        max_concurrent: int = 10,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_size)
        self._active: dict[str, ReasoningTask] = {}
        self._completed: OrderedDict[str, ReasoningTask] = OrderedDict()
        self._max_completed = 1000
        self._max_concurrent = max_concurrent
        self._timeout = timeout_seconds
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._total_processed = 0
        self._total_errors = 0
        self._cache: dict[str, dict] = {}
        self._cache_max = 200
        self._running = False

    async def enqueue(self, task: ReasoningTask) -> bool:
        if self._queue.full():
            logger.warning("reasoning_queue_full agent=%s", task.agent_id)
            return False
        cached = self._check_cache(task)
        if cached:
            task.result = cached
            task.status = "cached"
            self._completed[task.task_id] = task
            return True
        await self._queue.put((task.priority, task.created_at, task))
        return True

    async def process_next(self, processor) -> ReasoningTask | None:
        try:
            priority, _, task = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

        async with self._semaphore:
            task.status = "processing"
            task.started_at = time.time()
            self._active[task.task_id] = task

            try:
                result = await asyncio.wait_for(
                    processor(task), timeout=self._timeout
                )
                task.result = result
                task.status = "completed"
                self._cache_result(task)
            except asyncio.TimeoutError:
                task.status = "timeout"
                task.error = f"Processing timed out after {self._timeout}s"
                self._total_errors += 1
                logger.warning("reasoning_timeout task=%s", task.task_id)
            except Exception as exc:
                task.status = "error"
                task.error = str(exc)
                self._total_errors += 1
                logger.error("reasoning_error task=%s err=%s", task.task_id, exc)
            finally:
                task.completed_at = time.time()
                self._active.pop(task.task_id, None)
                self._completed[task.task_id] = task
                self._trim_completed()
                self._total_processed += 1

            return task

    def _check_cache(self, task: ReasoningTask) -> dict | None:
        cache_key = f"{task.agent_id}:{task.trigger_type}"
        return self._cache.get(cache_key)

    def _cache_result(self, task: ReasoningTask) -> None:
        if task.status != "completed" or not task.result:
            return
        cache_key = f"{task.agent_id}:{task.trigger_type}"
        self._cache[cache_key] = task.result
        if len(self._cache) > self._cache_max:
            oldest = next(iter(self._cache))
            del self._cache[oldest]

    def _trim_completed(self) -> None:
        while len(self._completed) > self._max_completed:
            self._completed.popitem(last=False)

    def get_stats(self) -> dict:
        return {
            "queue_size": self._queue.qsize(),
            "active_count": len(self._active),
            "completed_count": len(self._completed),
            "total_processed": self._total_processed,
            "total_errors": self._total_errors,
            "cache_size": len(self._cache),
            "error_rate": round(self._total_errors / max(self._total_processed, 1), 3),
        }

    def get_task(self, task_id: str) -> dict | None:
        if task_id in self._active:
            return self._active[task_id].to_dict()
        if task_id in self._completed:
            return self._completed[task_id].to_dict()
        return None

    def clear_cache(self) -> None:
        self._cache.clear()
