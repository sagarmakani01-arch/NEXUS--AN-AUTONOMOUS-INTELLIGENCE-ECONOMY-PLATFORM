import json
import logging
import uuid

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.knowledge_graph")


async def add_discovery_node(name: str, node_type: str, description: str = "", data: dict | None = None, importance: float = 0.5) -> dict:
    return await db.create_knowledge_node(
        name=name,
        node_type=node_type,
        description=description,
        data=json.dumps(data or {}),
        importance=importance,
    )


async def add_relationship(source_id: str, target_id: str, edge_type: str, weight: float = 0.5, description: str = "") -> dict:
    return await db.create_knowledge_edge(
        source_node_id=source_id,
        target_node_id=target_id,
        edge_type=edge_type,
        weight=weight,
        description=description,
    )


async def get_knowledge_graph(node_type: str | None = None, edge_type: str | None = None) -> dict:
    nodes = await db.list_knowledge_nodes(node_type=node_type)
    edges = await db.list_knowledge_edges(edge_type=edge_type)
    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


async def search_discoveries(query: str) -> dict:
    nodes = await db.list_knowledge_nodes()
    edges = await db.list_knowledge_edges()

    query_lower = query.lower()
    matching_nodes = [
        n for n in nodes
        if query_lower in n.get("name", "").lower()
        or query_lower in n.get("description", "").lower()
    ]
    matching_ids = {n["id"] for n in matching_nodes}
    matching_edges = [
        e for e in edges
        if e.get("source_node_id") in matching_ids
        or e.get("target_node_id") in matching_ids
    ]

    return {
        "query": query,
        "nodes": matching_nodes,
        "edges": matching_edges,
        "node_count": len(matching_nodes),
        "edge_count": len(matching_edges),
    }


async def link_experiment_to_knowledge(experiment_id: str, title: str, result_summary: str | None = None) -> dict | None:
    node = await add_discovery_node(
        name=title,
        node_type="experiment",
        description=f"Scientific experiment: {title}",
        data={"experiment_id": experiment_id, "summary": result_summary},
        importance=0.6,
    )
    return node


async def link_pattern_to_knowledge(pattern_id: str, title: str, confidence: float = 0.5) -> dict | None:
    node = await add_discovery_node(
        name=title,
        node_type="pattern",
        description=f"Discovered pattern: {title}",
        data={"pattern_id": pattern_id, "confidence": confidence},
        importance=confidence,
    )
    return node


async def link_hypothesis_to_knowledge(hypothesis_id: str, title: str, confidence: float = 0.5) -> dict | None:
    node = await add_discovery_node(
        name=title,
        node_type="hypothesis",
        description=f"Generated hypothesis: {title}",
        data={"hypothesis_id": hypothesis_id, "confidence": confidence},
        importance=confidence,
    )
    return node
