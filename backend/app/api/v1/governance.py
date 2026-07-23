from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/governance", tags=["Governance & Law"])


class CreateAuthorityRequest(BaseModel):
    name: str
    entity_type: str
    description: str | None = None
    authority_level: str = "individual"
    founder_id: str | None = None


class CreateLawRequest(BaseModel):
    name: str
    description: str | None = None
    creator_id: str
    scope: str = "global"
    category: str = "general"
    severity: str = "medium"
    affected_entities: list[str] | None = None
    penalty: dict | None = None


class CreatePolicyRequest(BaseModel):
    name: str
    description: str | None = None
    policy_type: str
    creator_id: str
    target: str | None = None
    rules: dict | None = None
    expected_outcome: str | None = None
    duration_days: int = 30
    priority: str = "medium"


class CreateTaxRequest(BaseModel):
    name: str
    tax_type: str
    rate: float
    target: str
    creator_id: str
    description: str | None = None
    revenue_use: str = "infrastructure"


class CreateRegulationRequest(BaseModel):
    name: str
    description: str | None = None
    regulation_type: str
    authority_id: str
    target_sector: str | None = None
    requirements: dict | None = None
    max_violations: int = 3
    penalty_description: str | None = None


class CreateConflictRequest(BaseModel):
    plaintiff_id: str
    plaintiff_type: str = "agent"
    defendant_id: str
    defendant_type: str = "agent"
    conflict_type: str
    description: str | None = None
    resolution_method: str = "arbitration"


class StartVoteRequest(BaseModel):
    proposal_title: str
    description: str | None = None
    proposer_id: str
    proposal_type: str = "law"
    target_id: str | None = None
    options: list[str] | None = None
    total_eligible: int = 0
    quorum_pct: float = 30.0


class CastVoteRequest(BaseModel):
    voter_id: str
    option: str


@router.get("/engine/state")
async def get_engine_state():
    from app.governance.engine import governance_engine
    return governance_engine.get_state()


@router.post("/authority/create")
async def create_authority(req: CreateAuthorityRequest):
    from app.governance.authority import authority_system
    return await authority_system.create_entity(
        name=req.name, entity_type=req.entity_type,
        description=req.description, authority_level=req.authority_level,
        founder_id=req.founder_id,
    )


@router.get("/authority")
async def list_authorities(entity_type: str | None = None, authority_level: str | None = None):
    from app.governance.authority import authority_system
    return await authority_system.list_entities(entity_type, authority_level)


@router.get("/authority/{entity_id}")
async def get_authority(entity_id: str):
    from app.governance.authority import authority_system
    entity = await authority_system.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/authority/permissions/{level}")
async def get_permissions(level: str):
    from app.governance.authority import authority_system
    return {"level": level, "permissions": authority_system.get_permissions(level)}


@router.post("/laws/create")
async def create_law(req: CreateLawRequest):
    from app.governance.laws import law_engine
    return await law_engine.create_law(
        name=req.name, description=req.description,
        creator_id=req.creator_id, scope=req.scope,
        category=req.category, severity=req.severity,
        affected_entities=req.affected_entities, penalty=req.penalty,
    )


@router.get("/laws")
async def list_laws(category: str | None = None):
    from app.governance.laws import law_engine
    return await law_engine.list_laws(category)


@router.get("/laws/{law_id}")
async def get_law(law_id: str):
    from app.governance.laws import law_engine
    law = await law_engine.get_law(law_id)
    if not law:
        raise HTTPException(status_code=404, detail="Law not found")
    return law


@router.get("/laws/stats")
async def get_law_stats():
    from app.governance.laws import law_engine
    return await law_engine.get_law_stats()


@router.post("/policies/create")
async def create_policy(req: CreatePolicyRequest):
    from app.governance.policies import policy_engine
    return await policy_engine.create_policy(
        name=req.name, description=req.description,
        policy_type=req.policy_type, creator_id=req.creator_id,
        target=req.target, rules=req.rules,
        expected_outcome=req.expected_outcome,
        duration_days=req.duration_days, priority=req.priority,
    )


@router.get("/policies")
async def list_policies(policy_type: str | None = None):
    from app.governance.policies import policy_engine
    return await policy_engine.list_policies(policy_type)


@router.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    from app.governance.policies import policy_engine
    policy = await policy_engine.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.post("/taxes/create")
async def create_tax(req: CreateTaxRequest):
    from app.governance.taxation import taxation_system
    return await taxation_system.create_tax(
        name=req.name, tax_type=req.tax_type,
        rate=req.rate, target=req.target,
        creator_id=req.creator_id, description=req.description,
        revenue_use=req.revenue_use,
    )


@router.get("/taxes")
async def list_taxes(tax_type: str | None = None):
    from app.governance.taxation import taxation_system
    from app.governance import persistence as gov_db
    return await gov_db.list_taxes(tax_type)


@router.get("/taxes/overview")
async def get_tax_overview():
    from app.governance.taxation import taxation_system
    return await taxation_system.get_tax_overview()


@router.post("/regulations/create")
async def create_regulation(req: CreateRegulationRequest):
    from app.governance.regulation import regulation_system
    return await regulation_system.create_regulation(
        name=req.name, description=req.description,
        regulation_type=req.regulation_type,
        authority_id=req.authority_id,
        target_sector=req.target_sector,
        requirements=req.requirements,
        max_violations=req.max_violations,
        penalty_description=req.penalty_description,
    )


@router.get("/regulations")
async def list_regulations(regulation_type: str | None = None):
    from app.governance.regulation import regulation_system
    from app.governance import persistence as gov_db
    return await gov_db.list_regulations(regulation_type)


@router.get("/regulations/stats")
async def get_regulation_stats():
    from app.governance.regulation import regulation_system
    return await regulation_system.get_regulation_stats()


@router.post("/conflicts/create")
async def create_conflict(req: CreateConflictRequest):
    from app.governance.conflict import conflict_resolution
    return await conflict_resolution.create_conflict(
        plaintiff_id=req.plaintiff_id, plaintiff_type=req.plaintiff_type,
        defendant_id=req.defendant_id, defendant_type=req.defendant_type,
        conflict_type=req.conflict_type, description=req.description,
        resolution_method=req.resolution_method,
    )


@router.get("/conflicts")
async def list_conflicts(status: str | None = None, party_id: str | None = None):
    from app.governance.conflict import conflict_resolution
    from app.governance import persistence as gov_db
    return await gov_db.list_conflicts(status, party_id)


@router.get("/conflicts/{conflict_id}")
async def get_conflict(conflict_id: str):
    from app.governance.conflict import conflict_resolution
    from app.governance import persistence as gov_db
    conflict = await gov_db.get_conflict(conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return conflict


@router.post("/conflicts/{conflict_id}/resolve-negotiation")
async def resolve_negotiation(conflict_id: str):
    from app.governance.conflict import conflict_resolution
    return await conflict_resolution.resolve_negotiation(conflict_id)


@router.post("/conflicts/{conflict_id}/resolve-arbitration")
async def resolve_arbitration(conflict_id: str):
    from app.governance.conflict import conflict_resolution
    return await conflict_resolution.resolve_arbitration(conflict_id)


@router.post("/votes/create")
async def start_vote(req: StartVoteRequest):
    from app.governance.voting import voting_system
    return await voting_system.start_vote(
        proposal_title=req.proposal_title, description=req.description,
        proposer_id=req.proposer_id, proposal_type=req.proposal_type,
        target_id=req.target_id, options=req.options,
        total_eligible=req.total_eligible, quorum_pct=req.quorum_pct,
    )


@router.get("/votes")
async def list_votes(status: str | None = None):
    from app.governance.voting import voting_system
    return await voting_system.list_votes(status)


@router.get("/votes/{vote_id}")
async def get_vote(vote_id: str):
    from app.governance.voting import voting_system
    vote = await voting_system.get_vote(vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    return vote


@router.post("/votes/{vote_id}/cast")
async def cast_vote(vote_id: str, req: CastVoteRequest):
    from app.governance.voting import voting_system
    return await voting_system.cast_vote(vote_id, req.voter_id, req.option)


@router.post("/votes/{vote_id}/resolve")
async def resolve_vote(vote_id: str):
    from app.governance.voting import voting_system
    return await voting_system.resolve_vote(vote_id)


@router.get("/records")
async def get_records(record_type: str | None = None):
    from app.governance import persistence as gov_db
    return await gov_db.get_governance_records(record_type)


@router.get("/dashboard")
async def get_civilization_dashboard():
    from app.governance.intelligence import governance_intelligence
    return await governance_intelligence.get_civilization_dashboard()


@router.get("/governance-dashboard")
async def get_governance_dashboard():
    from app.governance.intelligence import governance_intelligence
    return await governance_intelligence.get_governance_dashboard()


@router.get("/stats")
async def get_governance_stats():
    from app.governance import persistence as gov_db
    return await gov_db.get_governance_stats()


@router.get("/agent/{agent_id}")
async def get_agent_governance(agent_id: str):
    from app.governance.engine import governance_engine
    return await governance_engine.get_agent_governance_state(agent_id)
