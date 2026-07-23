from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.research.engine import research_engine
from app.research.organizations import organization_manager
from app.research.projects import project_manager
from app.research.knowledge_graph import knowledge_graph_engine
from app.research.experiments import experiment_engine
from app.research.publications import publication_engine
from app.research.peer_review import peer_review_engine
from app.research.technology_tree import technology_tree_engine
from app.research.diffusion import knowledge_diffusion_engine
from app.research.funding import funding_engine
from app.research.innovation import research_innovation_engine
from app.research.intelligence import research_intelligence
from app.research import persistence as db

router = APIRouter(prefix="/api/v1/research", tags=["research"])


# Engine control

@router.get("/engine/state")
async def get_engine_state():
    return research_engine.get_state()


@router.post("/engine/start")
async def start_engine():
    await research_engine.start()
    return {"status": "started"}


@router.post("/engine/stop")
async def stop_engine():
    await research_engine.stop()
    return {"status": "stopped"}


@router.post("/engine/tick")
async def manual_tick():
    await research_engine.tick()
    return {"status": "tick_completed"}


@router.post("/engine/speed")
async def set_speed(interval: int = Query(ge=10, le=300)):
    research_engine.set_speed(interval)
    return {"tick_interval": interval}


# Organizations

@router.get("/organizations")
async def list_organizations(org_type: str | None = None):
    return await organization_manager.list_organizations(org_type)


@router.get("/organizations/{org_id}")
async def get_organization(org_id: str):
    result = await organization_manager.get_organization(org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Organization not found")
    return result


@router.post("/organizations")
async def create_organization(name: str, org_type: str,
                              founder_agent_id: str | None = None,
                              initial_budget: float = 0):
    return await organization_manager.create_organization(name, org_type, founder_agent_id, initial_budget=initial_budget)


@router.post("/organizations/{org_id}/scientists")
async def add_scientist(org_id: str, agent_id: str):
    return await organization_manager.add_scientist(org_id, agent_id)


@router.post("/organizations/{org_id}/budget")
async def allocate_budget(org_id: str, amount: float):
    return await organization_manager.allocate_budget(org_id, amount)


# Projects

@router.get("/projects")
async def list_projects(organization_id: str | None = None,
                        status: str | None = None, limit: int = Query(ge=1, le=200, default=50)):
    return await project_manager.list_projects(organization_id, status, limit=limit)


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    result = await project_manager.get_project(project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.post("/projects")
async def create_project(title: str, research_question: str,
                         lead_agent_id: str | None = None,
                         organization_id: str | None = None,
                         hypothesis: str | None = None,
                         budget: float = 100, timeline_days: int = 30,
                         knowledge_domain: str | None = None):
    return await project_manager.create_project(
        title=title, research_question=research_question,
        lead_agent_id=lead_agent_id, organization_id=organization_id,
        hypothesis=hypothesis, budget=budget, timeline_days=timeline_days,
        knowledge_domain=knowledge_domain,
    )


@router.post("/projects/auto")
async def auto_generate_project(organization_id: str | None = None):
    return await project_manager.auto_generate_project(organization_id)


@router.post("/projects/{project_id}/progress")
async def progress_project(project_id: str):
    return await project_manager.progress_project(project_id)


# Knowledge Graph

@router.get("/knowledge/graph")
async def get_knowledge_graph():
    return await knowledge_graph_engine.get_graph_summary()


@router.get("/knowledge/nodes")
async def list_knowledge_nodes(node_type: str | None = None,
                               domain: str | None = None, limit: int = 100):
    return await db.list_knowledge_nodes(node_type, domain, limit)


@router.post("/knowledge/nodes")
async def create_knowledge_node(name: str, node_type: str,
                                domain: str | None = None,
                                description: str | None = None,
                                discoverer_agent_id: str | None = None):
    return await knowledge_graph_engine.create_node(name, node_type, domain, description, discoverer_agent_id)


@router.post("/knowledge/edges")
async def create_knowledge_edge(source_id: str, target_id: str, edge_type: str,
                                weight: float = 1.0, description: str | None = None):
    return await knowledge_graph_engine.create_edge(source_id, target_id, edge_type, weight, description)


@router.get("/knowledge/related/{node_id}")
async def find_related_nodes(node_id: str, depth: int = Query(ge=1, le=5, default=2)):
    return await knowledge_graph_engine.find_related_nodes(node_id, depth)


@router.post("/knowledge/populate/{domain}")
async def populate_domain(domain: str):
    return await knowledge_graph_engine.auto_populate_domain(domain)


# Experiments

@router.get("/experiments")
async def list_experiments(project_id: str | None = None, status: str | None = None):
    return await experiment_engine.list_experiments(project_id, status)


@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    result = await experiment_engine.get_experiment(experiment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


@router.post("/experiments")
async def create_experiment(project_id: str, title: str,
                            description: str | None = None,
                            methodology: str | None = None,
                            hypothesis: str | None = None):
    return await experiment_engine.create_experiment(project_id, title, description, methodology, hypothesis)


@router.post("/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    return await experiment_engine.start_experiment(experiment_id)


@router.post("/experiments/{experiment_id}/complete")
async def complete_experiment(experiment_id: str, outcome: str | None = None):
    return await experiment_engine.complete_experiment(experiment_id, outcome)


# Publications

@router.get("/publications")
async def list_publications(institution: str | None = None,
                            knowledge_domain: str | None = None,
                            status: str | None = None):
    return await publication_engine.list_publications(institution, knowledge_domain, status)


@router.get("/publications/{pub_id}")
async def get_publication(pub_id: str):
    result = await publication_engine.get_publication(pub_id)
    if not result:
        raise HTTPException(status_code=404, detail="Publication not found")
    return result


@router.post("/publications")
async def create_publication(title: str, authors: list[str],
                             institution: str | None = None,
                             abstract: str | None = None,
                             knowledge_domain: str | None = None,
                             project_id: str | None = None):
    return await publication_engine.create_publication(
        title=title, authors=authors, institution=institution,
        abstract=abstract, knowledge_domain=knowledge_domain,
        project_id=project_id,
    )


@router.post("/publications/{pub_id}/submit")
async def submit_for_review(pub_id: str):
    return await publication_engine.submit_for_review(pub_id)


@router.post("/publications/{pub_id}/publish")
async def publish_paper(pub_id: str):
    return await publication_engine.publish(pub_id)


@router.post("/publications/{pub_id}/cite")
async def add_citation(pub_id: str):
    return await publication_engine.add_citation(pub_id)


# Peer Review

@router.get("/reviews")
async def list_reviews(publication_id: str | None = None,
                       reviewer_agent_id: str | None = None):
    return await peer_review_engine.get_reviews_for_publication(publication_id) if publication_id else await db.list_peer_reviews(reviewer_agent_id=reviewer_agent_id)


@router.post("/reviews")
async def submit_review(publication_id: str, reviewer_agent_id: str,
                        institution: str | None = None, decision: str | None = None):
    return await peer_review_engine.submit_review(publication_id, reviewer_agent_id, institution, decision)


@router.get("/reviews/reviewer/{reviewer_id}")
async def get_reviewer_stats(reviewer_id: str):
    return await peer_review_engine.get_reviewer_stats(reviewer_id)


# Technology Tree

@router.get("/technology")
async def get_tech_tree(domain: str | None = None):
    return await technology_tree_engine.get_tech_tree(domain)


@router.get("/technology/{tech_id}")
async def get_technology(tech_id: str):
    result = await technology_tree_engine.get_technology(tech_id)
    if not result:
        raise HTTPException(status_code=404, detail="Technology not found")
    return result


@router.post("/technology/contribute")
async def contribute_research(tech_id: str, agent_id: str, points: int = Query(ge=1, le=100)):
    return await technology_tree_engine.contribute_research(tech_id, agent_id, points)


@router.post("/technology/{tech_id}/adopt")
async def adopt_technology(tech_id: str, organization_id: str):
    return await technology_tree_engine.adopt_technology(tech_id, organization_id)


@router.post("/technology/initialize")
async def initialize_tech_tree():
    return await technology_tree_engine.initialize_tech_tree()


# Knowledge Diffusion

@router.get("/diffusion/stats")
async def get_diffusion_stats():
    return await knowledge_diffusion_engine.get_diffusion_stats()


@router.post("/diffusion/share")
async def share_knowledge(source_agent_id: str, target_agent_id: str,
                          knowledge_node_ids: list[str],
                          mode: str = "collaboration", visibility: str = "public"):
    return await knowledge_diffusion_engine.share_knowledge(
        source_agent_id, target_agent_id, knowledge_node_ids, mode, visibility
    )


@router.post("/diffusion/conference")
async def hold_conference(name: str, domain: str | None = None,
                          organizer_id: str | None = None):
    return await knowledge_diffusion_engine.hold_conference(name, domain, organizer_id)


@router.get("/diffusion/conferences")
async def list_conferences(domain: str | None = None, status: str | None = None):
    return await db.list_conferences(domain, status)


# Funding

@router.get("/funding")
async def list_funding(project_id: str | None = None, status: str | None = None):
    return await funding_engine.list_funding(project_id, status)


@router.post("/funding/request")
async def request_funding(project_id: str, source_type: str,
                          funder_organization: str | None = None,
                          amount: float | None = None):
    return await funding_engine.request_funding(project_id, source_type, funder_organization, amount)


@router.get("/funding/stats")
async def get_funding_stats():
    return await funding_engine.get_funding_stats()


# Innovation

@router.get("/innovations")
async def list_innovations(organization_id: str | None = None):
    return await research_innovation_engine.get_innovations(organization_id)


@router.post("/innovations/generate")
async def generate_idea(discoverer_agent_id: str | None = None,
                        domain: str | None = None):
    return await research_innovation_engine.generate_idea(discoverer_agent_id, domain)


@router.post("/innovations/{innovation_id}/evaluate")
async def evaluate_idea(innovation_id: str):
    return await research_innovation_engine.evaluate_idea(innovation_id)


@router.post("/innovations/{innovation_id}/adopt")
async def adopt_innovation(innovation_id: str):
    return await research_innovation_engine.adopt_innovation(innovation_id)


@router.get("/innovations/stats")
async def get_innovation_stats():
    return await research_innovation_engine.get_innovation_stats()


# Intelligence / Dashboard

@router.get("/dashboard")
async def get_research_dashboard():
    return await research_intelligence.get_research_dashboard()


@router.get("/dashboard/organization/{org_id}")
async def get_organization_report(org_id: str):
    return await research_intelligence.get_organization_report(org_id)


@router.get("/dashboard/trends")
async def get_research_trends():
    return await research_intelligence.get_research_trends()


@router.get("/dashboard/citations")
async def get_citation_network():
    return await research_intelligence.get_citation_network()


# Stats

@router.get("/stats")
async def get_research_stats():
    return await db.get_research_stats()
