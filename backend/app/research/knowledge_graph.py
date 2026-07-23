import json
import logging
import random

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.knowledge_graph")

NODE_TYPES = ["concept", "technology", "method", "discovery", "skill", "domain"]
EDGE_TYPES = ["depends_on", "improves", "inspired_by", "contradicts", "extends"]

DEFAULT_DOMAINS = {
    "Artificial Intelligence": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning"],
    "Quantum Computing": ["Qubits", "Quantum Gates", "Quantum Algorithms", "Error Correction"],
    "Biotechnology": ["Genomics", "Protein Engineering", "Synthetic Biology", "Gene Editing"],
    "Materials Science": ["Nanomaterials", "Polymers", "Composites", "Superconductors"],
    "Neuroscience": ["Brain-Computer Interface", "Neural Networks", "Cognitive Science"],
    "Climate Science": ["Carbon Capture", "Climate Modeling", "Renewable Energy"],
}


class KnowledgeGraphEngine:
    def __init__(self):
        self.stats = {
            "nodes_created": 0,
            "edges_created": 0,
            "discoveries_made": 0,
            "cross_domain_connections": 0,
        }

    async def create_node(self, name: str, node_type: str, domain: str | None = None,
                          description: str | None = None,
                          discoverer_agent_id: str | None = None,
                          discovery_source: str | None = None) -> dict:
        novelty = random.uniform(0.5, 1.0)
        node_id = await db.create_knowledge_node(
            name=name, node_type=node_type, domain=domain,
            description=description, novelty_score=novelty,
            discoverer_agent_id=discoverer_agent_id,
            discovery_source=discovery_source,
        )
        self.stats["nodes_created"] += 1
        self.stats["discoveries_made"] += 1

        await dispatch(Event(EventType.PUBLICATION_RELEASED, {
            "node_id": node_id, "name": name, "type": node_type, "domain": domain,
        }))
        return {"node_id": node_id, "name": name, "type": node_type, "novelty": novelty}

    async def create_edge(self, source_id: str, target_id: str, edge_type: str,
                          weight: float = 1.0, description: str | None = None,
                          created_by_agent_id: str | None = None) -> dict:
        edge_id = await db.create_knowledge_edge(
            source_node_id=source_id, target_node_id=target_id,
            edge_type=edge_type, weight=weight, description=description,
            created_by_agent_id=created_by_agent_id,
        )
        self.stats["edges_created"] += 1

        source = await db.get_knowledge_node(source_id)
        target = await db.get_knowledge_node(target_id)
        if source and target and source.get("domain") != target.get("domain"):
            self.stats["cross_domain_connections"] += 1

        return {"edge_id": edge_id, "source": source_id, "target": target_id, "type": edge_type}

    async def auto_populate_domain(self, domain: str) -> dict:
        concepts = DEFAULT_DOMAINS.get(domain, [f"{domain} Fundamentals", f"{domain} Applications"])
        created_nodes = []
        for concept_name in concepts:
            node_id = await db.create_knowledge_node(
                name=concept_name, node_type="concept", domain=domain,
                description=f"Core concept in {domain}: {concept_name}",
                novelty_score=random.uniform(0.3, 0.8),
            )
            self.stats["nodes_created"] += 1
            created_nodes.append(node_id)

        for i in range(len(created_nodes) - 1):
            await db.create_knowledge_edge(
                source_node_id=created_nodes[i],
                target_node_id=created_nodes[i + 1],
                edge_type="extends", weight=random.uniform(0.5, 1.0),
            )
            self.stats["edges_created"] += 1

        if len(created_nodes) >= 3:
            await db.create_knowledge_edge(
                source_node_id=created_nodes[0],
                target_node_id=created_nodes[-1],
                edge_type="depends_on", weight=random.uniform(0.3, 0.7),
            )
            self.stats["edges_created"] += 1

        return {"domain": domain, "nodes_created": len(created_nodes), "edges_created": len(created_nodes)}

    async def get_graph_summary(self) -> dict:
        all_nodes = await db.list_knowledge_nodes(limit=500)
        all_edges = await db.list_knowledge_edges()

        type_counts = {}
        domain_counts = {}
        for n in all_nodes:
            t = n.get("node_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
            d = n.get("domain", "unknown")
            domain_counts[d] = domain_counts.get(d, 0) + 1

        edge_type_counts = {}
        for e in all_edges:
            et = e.get("edge_type", "unknown")
            edge_type_counts[et] = edge_type_counts.get(et, 0) + 1

        return {
            "total_nodes": len(all_nodes),
            "total_edges": len(all_edges),
            "node_types": type_counts,
            "domain_distribution": domain_counts,
            "edge_types": edge_type_counts,
            "cross_domain_connections": self.stats["cross_domain_connections"],
        }

    async def find_related_nodes(self, node_id: str, depth: int = 2) -> dict:
        visited = set()
        result = {"nodes": [], "edges": []}

        async def _traverse(nid, current_depth):
            if current_depth > depth or nid in visited:
                return
            visited.add(nid)
            node = await db.get_knowledge_node(nid)
            if node:
                result["nodes"].append(node)
            outgoing = await db.list_knowledge_edges(source_node_id=nid)
            incoming = await db.list_knowledge_edges(target_node_id=nid)
            for edge in outgoing + incoming:
                result["edges"].append(edge)
                neighbor = edge["target_node_id"] if edge["source_node_id"] == nid else edge["source_node_id"]
                await _traverse(neighbor, current_depth + 1)

        await _traverse(node_id, 0)
        return result

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


knowledge_graph_engine = KnowledgeGraphEngine()
