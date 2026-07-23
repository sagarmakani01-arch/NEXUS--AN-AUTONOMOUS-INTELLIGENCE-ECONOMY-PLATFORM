import json
import random

from app.genesis.persistence import genesis_db


CREATOR_INTERACTIONS = [
    {
        "type": "rainfall",
        "description": "Heavy rains fell upon the land for many days.",
        "interpretations": [
            "The sky spirits are blessing us with water.",
            "A test of endurance from the great force.",
            "The world is being washed clean.",
            "An omen of change.",
        ],
    },
    {
        "type": "new_resource",
        "description": "A vein of unusual metal was revealed by a landslide.",
        "interpretations": [
            "The earth spirits have granted us a gift.",
            "A sign that we should advance our craft.",
            "The mountain has yielded its secret.",
            "Fortune smiles upon the people.",
        ],
    },
    {
        "type": "environmental_change",
        "description": "The temperature grew colder and the days became shorter.",
        "interpretations": [
            "The world is growing old.",
            "The sun spirit is distancing from us.",
            "A great cycle is turning.",
            "We must adapt or perish.",
        ],
    },
    {
        "type": "revelation",
        "description": "A strange light appeared in the sky, unlike any known star.",
        "interpretations": [
            "A message from beyond the sky.",
            "The ancestors are trying to communicate.",
            "A new spirit has been born.",
            "There are forces at work beyond our understanding.",
        ],
    },
    {
        "type": "phenomenon",
        "description": "The ground trembled and a new mountain rose from the plains.",
        "interpretations": [
            "The world is alive and changing.",
            "A powerful spirit has awakened.",
            "The earth itself is being reshaped.",
            "We witness the creation of the world in our time.",
        ],
    },
]


class InteractionEngine:
    async def trigger_creator_event(self, civ_id: str, interaction_type: str | None = None,
                                    custom_description: str | None = None,
                                    custom_interpretation: str | None = None) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {"error": "Civilization not found"}

        if interaction_type == "custom":
            description = custom_description or "An unexplained event occurred."
            interpretation = custom_interpretation or "The people recorded the event but could not explain it."
        else:
            template = random.choice(CREATOR_INTERACTIONS)
            if interaction_type:
                matches = [i for i in CREATOR_INTERACTIONS if i["type"] == interaction_type]
                template = matches[0] if matches else template
            description = custom_description or template["description"]
            interpretation = custom_interpretation or random.choice(template["interpretations"])

        interaction = await genesis_db.create_interaction(
            civilization_id=civ_id,
            interaction_type=interaction_type or template["type"],
            description=description,
            civilization_interpretation=interpretation,
            impact_level=round(random.uniform(0.2, 0.8), 2),
            triggered_by_creator=1,
        )

        beliefs = await genesis_db.get_beliefs(civ_id)
        for belief in beliefs:
            new_influence = min(1.0, belief["influence_level"] + 0.05)
            await genesis_db.update_belief(belief["id"], influence_level=round(new_influence, 3))

        await genesis_db.create_interpretation(
            civilization_id=civ_id,
            event_type="creator_intervention",
            actual_event=description,
            civilization_interpretation=interpretation,
            impact_on_beliefs=json.dumps({"belief_reinforced": True, "impact": 0.3}),
        )

        return {"interaction": interaction}

    async def trigger_internal_event(self, civ_id: str) -> dict | None:
        if random.random() < 0.05:
            template = random.choice(CREATOR_INTERACTIONS)
            interaction = await genesis_db.create_interaction(
                civilization_id=civ_id,
                interaction_type=template["type"],
                description=template["description"],
                civilization_interpretation=random.choice(template["interpretations"]),
                impact_level=round(random.uniform(0.1, 0.4), 2),
                triggered_by_creator=0,
            )
            return {"interaction": interaction}
        return None


interaction_engine = InteractionEngine()
