import json
import logging
import uuid

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.archive")


async def archive_experiment(experiment_id: str) -> dict | None:
    experiment = await db.get_experiment(experiment_id)
    if not experiment:
        return None
    return await db.create_archive_entry(
        archive_type="experiment",
        title=experiment.get("title", "Experiment"),
        content=json.dumps(experiment),
        reference_id=experiment_id,
        success=1 if experiment.get("status") == "completed" else 0,
        tags=json.dumps(experiment.get("tags", [])),
    )


async def archive_pattern(pattern_id: str) -> dict | None:
    pattern = await db.get_pattern(pattern_id)
    if not pattern:
        return None
    return await db.create_archive_entry(
        archive_type="pattern",
        title=pattern.get("title", "Pattern"),
        content=json.dumps(pattern),
        reference_id=pattern_id,
        success=1,
        tags=json.dumps(pattern.get("tags", [])),
    )


async def archive_hypothesis(hypothesis_id: str) -> dict | None:
    hypothesis = await db.get_hypothesis(hypothesis_id)
    if not hypothesis:
        return None
    return await db.create_archive_entry(
        archive_type="hypothesis",
        title=hypothesis.get("title", "Hypothesis"),
        content=json.dumps(hypothesis),
        reference_id=hypothesis_id,
        success=1,
        tags=json.dumps([]),
    )


async def archive_report(report_id: str) -> dict | None:
    report = await db.get_report(report_id)
    if not report:
        return None
    return await db.create_archive_entry(
        archive_type="report",
        title=report.get("title", "Report"),
        content=json.dumps(report),
        reference_id=report_id,
        success=1,
        tags=json.dumps([]),
    )


async def get_archive_timeline(limit: int = 100) -> list[dict]:
    return await db.list_archive(limit=limit)


async def clear_failed_archives():
    archives = await db.list_archive(limit=500)
    for arch in archives:
        if not arch.get("success", 1):
            pass
