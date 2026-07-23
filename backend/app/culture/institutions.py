import logging
import random
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.institutions")

INST_TYPES = [
    "academy", "scientific_council", "professional_association",
    "standards_committee", "historical_archive", "council_of_elders",
    "research_institute", "cultural_foundation", "education_board",
    "trade_guild", "innovation_lab", "library",
]


async def initialize_institutions(civ_id: str) -> list[dict]:
    existing = await db.list_institutions(civ_id)
    if existing:
        return existing
    defaults = [
        ("Academy of Sciences", "academy", "Central scientific research institution"),
        ("Standards Committee", "standards_committee", "Sets quality and interoperability standards"),
        ("Historical Archive", "historical_archive", "Preserves civilization memory and records"),
    ]
    created = []
    for name, itype, desc in defaults:
        iid = await db.create_institution(
            civilization_id=civ_id,
            name=name,
            institution_type=itype,
            description=desc,
            strength=random.uniform(40.0, 70.0),
            influence=random.uniform(40.0, 70.0),
            membership_count=random.randint(5, 20),
        )
        created.append({"id": iid, "name": name})
    logger.info("Initialized %d institutions for civ %s", len(created), civ_id)
    return created


async def create_institution(civ_id: str, name: str, inst_type: str | None = None,
                             description: str | None = None) -> dict:
    if inst_type not in INST_TYPES:
        inst_type = random.choice(INST_TYPES)
    iid = await db.create_institution(
        civilization_id=civ_id,
        name=name,
        institution_type=inst_type,
        description=description,
        strength=random.uniform(30.0, 60.0),
        influence=random.uniform(30.0, 60.0),
        membership_count=1,
    )
    await db.create_cultural_timeline(
        civilization_id=civ_id,
        change_type="institution_founded",
        description=f"Institution '{name}' founded",
        cause="cultural_initiative",
        impact_score=40.0,
    )
    institutions = await db.list_institutions(civ_id)
    return next((i for i in institutions if i["id"] == iid), {})


async def strengthen_institution(inst_id: str, amount: float) -> dict | None:
    inst = await db.get_institution(inst_id)
    if not inst:
        return None
    new_strength = min(100.0, inst["strength"] + amount)
    new_influence = min(100.0, inst["influence"] + amount * 0.5)
    await db.update_institution(inst_id, strength=new_strength, influence=new_influence)
    return await db.get_institution(inst_id)


def get_state() -> dict:
    return {"institution_types": INST_TYPES, "initialized": True}
