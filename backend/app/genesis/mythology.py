import json
import random

from app.genesis.persistence import genesis_db


EXPLANATION_TEMPLATES = {
    "sunrise": [
        "The great fire spirit travels across the sky each day.",
        "The sun is a gift from the sky beings, carried by a giant bird.",
        "Each morning the world is reborn from darkness.",
        "The ancestors light the sky to guide the living.",
    ],
    "rain": [
        "The sky weeps for the fallen.",
        "Water spirits bless the land with life.",
        "The great serpent shakes its body, releasing water upon the world.",
        "The heavens open their stores to feed the earth.",
    ],
    "thunder": [
        "The mountain gods are fighting.",
        "A giant beats his drum in the sky.",
        "The sky beasts roar in anger.",
        "The creator's voice echoes across the world.",
    ],
    "earthquake": [
        "The world beast stirs in its sleep.",
        "The earth spirits are displeased.",
        "The ground remembers ancient battles.",
        "The foundation of the world shifts.",
    ],
    "death": [
        "The spirit leaves the body to join the ancestors.",
        "A great sleep from which there is no waking.",
        "The life force returns to the world.",
        "The journey to the spirit realm begins.",
    ],
    "birth": [
        "A new spirit has entered the world.",
        "The ancestors send a new soul.",
        "Life springs forth from the cycle of existence.",
        "A new chapter in the story of the people begins.",
    ],
}


class MythologyEngine:
    async def tick(self, civ_id: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {}

        beliefs = await genesis_db.get_beliefs(civ_id)

        if not beliefs and civ["current_year"] > 5:
            return await self._create_initial_belief(civ)

        if beliefs and random.random() < 0.05:
            event_type = random.choice(list(EXPLANATION_TEMPLATES.keys()))
            explanation = random.choice(EXPLANATION_TEMPLATES[event_type])
            belief = random.choice(beliefs)
            explanations = json.loads(belief.get("natural_event_explanations") or "{}")
            if event_type not in explanations:
                explanations[event_type] = explanation
                await genesis_db.update_belief(
                    belief["id"],
                    natural_event_explanations=json.dumps(explanations),
                    influence_level=min(1.0, belief["influence_level"] + 0.05),
                )

        return {"beliefs_count": len(beliefs)}

    async def _create_initial_belief(self, civ: dict) -> dict:
        names = ["The Way of Nature", "The Spirit Path", "The Ancestor Tradition", "The Sky Watchers"]
        origin_stories = [
            "The world was formed from the body of a great primordial being.",
            "In the beginning, there was endless water, then the first land rose.",
            "The great spirit sang the world into existence.",
            "From nothingness, a spark of life appeared and grew into all things.",
        ]
        creator_concepts = [
            "A distant presence that set the world in motion.",
            "Many spirits that dwell in all things.",
            "A great being that watches from beyond the sky.",
            "An unknowable force that is part of all existence.",
        ]
        name = random.choice(names)
        belief = await genesis_db.create_belief(
            civilization_id=civ["id"],
            name=name,
            belief_type=random.choice(["spiritual", "animistic", "ancestral"]),
            origin_explanation=random.choice(origin_stories),
            natural_event_explanations=json.dumps({
                "sunrise": random.choice(EXPLANATION_TEMPLATES["sunrise"]),
                "rain": random.choice(EXPLANATION_TEMPLATES["rain"]),
            }),
            creator_concept=random.choice(creator_concepts),
            core_tenets=json.dumps([
                "Respect the spirits of nature.",
                "Honor the ancestors.",
                "Protect the community.",
                "Learn from the world around you.",
            ]),
            rituals=json.dumps([
                "Dawn greeting ceremony",
                "Harvest offering",
                "Ancestor remembrance",
            ]),
            followers_count=civ["population"],
            influence_level=0.3,
            status="emerging",
        )
        return {"new_belief": belief}

    async def record_interpretation(self, civ_id: str, event_type: str, actual_event: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        beliefs = await genesis_db.get_beliefs(civ_id)
        num = random.randint(0, len(beliefs) - 1) if beliefs else 0
        interpretation = await genesis_db.create_interpretation(
            civilization_id=civ_id,
            event_type=event_type,
            actual_event=actual_event,
            civilization_interpretation=self._generate_interpretation(event_type, beliefs[num] if beliefs else None),
            impact_on_beliefs=json.dumps({"event_impact": 0.1}),
        )
        return interpretation

    def _generate_interpretation(self, event_type: str, belief: dict | None) -> str:
        if belief and belief.get("natural_event_explanations"):
            explanations = json.loads(belief["natural_event_explanations"]) if isinstance(belief["natural_event_explanations"], str) else belief["natural_event_explanations"]
            if event_type in explanations:
                return f"The elders say: {explanations[event_type]}"
        templates = EXPLANATION_TEMPLATES.get(event_type, ["A mysterious event occurred."])
        return random.choice(templates)


mythology_engine = MythologyEngine()
