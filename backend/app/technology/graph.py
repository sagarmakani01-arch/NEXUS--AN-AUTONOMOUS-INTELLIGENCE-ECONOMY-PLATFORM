import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.graph")

DOMAINS = [
    "Artificial Intelligence", "Robotics", "Energy Systems",
    "Materials Science", "Computing", "Transportation",
    "Medicine", "Manufacturing", "Communication",
]

EDGE_TYPES = ["enables", "builds_on", "competes_with", "supplements", "replaces"]


async def initialize_graph() -> list[dict]:
    existing = await db.list_technologies()
    if len(existing) >= 5:
        return existing

    templates = [
        ("Machine Learning", "Artificial Intelligence", "concept", 30.0, 10.0, "AI"),
        ("Neural Networks", "Artificial Intelligence", "prototype", 40.0, 15.0, "AI"),
        ("Robotics Control Systems", "Robotics", "concept", 35.0, 12.0, "Robotics"),
        ("Industrial Automation", "Manufacturing", "concept", 45.0, 20.0, "Robotics"),
        ("Solar Energy", "Energy Systems", "mature", 20.0, 25.0, "Energy"),
        ("Battery Storage", "Energy Systems", "testing", 50.0, 18.0, "Energy"),
        ("Quantum Computing", "Computing", "concept", 80.0, 30.0, "Computing"),
        ("Graphene Materials", "Materials Science", "prototype", 55.0, 22.0, "Materials"),
        ("Autonomous Vehicles", "Transportation", "testing", 60.0, 35.0, "Transportation"),
        ("Telemedicine", "Medicine", "adoption", 25.0, 15.0, "Medicine"),
        ("Smart Grid", "Energy Systems", "prototype", 40.0, 20.0, "Energy"),
        ("5G Networks", "Communication", "mature", 30.0, 15.0, "Communication"),
        ("Nanotechnology", "Materials Science", "concept", 70.0, 28.0, "Materials"),
        ("CRISPR", "Medicine", "prototype", 65.0, 25.0, "Medicine"),
        ("Blockchain", "Computing", "adoption", 35.0, 12.0, "Computing"),
    ]

    tech_ids = {}
    for name, domain, status, difficulty, impact, app in templates:
        tid = await db.create_technology(
            name=name, domain=domain, status=status,
            difficulty_level=difficulty, impact_score=impact,
            tech_type="core",
            applications=str([app]),
            origin_civilization_id="aetheria",
        )
        tech_ids[name] = tid

    edge_templates = [
        ("Machine Learning", "Neural Networks", "builds_on"),
        ("Neural Networks", "Robotics Control Systems", "enables"),
        ("Robotics Control Systems", "Industrial Automation", "enables"),
        ("Solar Energy", "Battery Storage", "supplements"),
        ("Quantum Computing", "Machine Learning", "enables"),
        ("Graphene Materials", "Robotics Control Systems", "supplements"),
        ("Battery Storage", "Autonomous Vehicles", "enables"),
        ("5G Networks", "Telemedicine", "enables"),
        ("Nanotechnology", "Graphene Materials", "builds_on"),
        ("CRISPR", "Telemedicine", "supplements"),
    ]

    for src, tgt, etype in edge_templates:
        if src in tech_ids and tgt in tech_ids:
            await db.create_technology_edge(
                source_technology_id=tech_ids[src],
                target_technology_id=tech_ids[tgt],
                edge_type=etype, weight=random.uniform(0.5, 1.0),
            )

    logger.info("Initialized technology graph with %d nodes and %d edges", len(tech_ids), len(edge_templates))
    return await db.list_technologies()


def get_state() -> dict:
    return {"domains": DOMAINS, "edge_types": EDGE_TYPES, "initialized": True}
