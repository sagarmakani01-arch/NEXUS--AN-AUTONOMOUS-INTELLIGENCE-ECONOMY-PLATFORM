from sqlalchemy import Column, ForeignKey, String, Table

from app.core.database import Base

agent_skills = Table(
    "agent_skills",
    Base.metadata,
    Column("agent_id", String(36), ForeignKey("agents.id"), primary_key=True),
    Column("skill_id", String(36), ForeignKey("skills.id"), primary_key=True),
)

agent_tasks = Table(
    "agent_tasks",
    Base.metadata,
    Column("agent_id", String(36), ForeignKey("agents.id"), primary_key=True),
    Column("task_id", String(36), ForeignKey("tasks.id"), primary_key=True),
)

from app.domain.models.user import User  # noqa: E402, F401
from app.domain.models.profession import Profession  # noqa: E402, F401
from app.domain.models.skill import Skill  # noqa: E402, F401
from app.domain.models.agent import Agent  # noqa: E402, F401
from app.domain.models.wallet import Wallet  # noqa: E402, F401
from app.domain.models.memory import Memory  # noqa: E402, F401
from app.domain.models.task import Task  # noqa: E402, F401
from app.domain.models.marketplace import MarketplaceListing  # noqa: E402, F401
from app.domain.models.company import Company  # noqa: E402, F401
from app.domain.models.company import CompanyMember  # noqa: E402, F401
from app.domain.models.company import CompanyMemory  # noqa: E402, F401
from app.domain.models.company import CompanyStrategy  # noqa: E402, F401
from app.domain.models.company import CompanyFinance  # noqa: E402, F401
from app.domain.models.transaction import Transaction  # noqa: E402, F401
from app.domain.models.event_log import EventLog  # noqa: E402, F401
from app.domain.models.identity import Identity  # noqa: E402, F401
from app.domain.models.personality import Personality  # noqa: E402, F401
from app.domain.models.goal import Goal  # noqa: E402, F401
from app.domain.models.memory_entry import AgentMemory  # noqa: E402, F401
from app.domain.models.relationship import Relationship  # noqa: E402, F401
from app.domain.models.agent_skill_profile import AgentSkill  # noqa: E402, F401
from app.domain.models.timeline_event import TimelineEvent  # noqa: E402, F401
from app.domain.models.decision import Decision  # noqa: E402, F401
from app.domain.models.plan import Plan  # noqa: E402, F401
from app.domain.models.reflection import Reflection  # noqa: E402, F401
from app.domain.models.asset import Asset  # noqa: E402, F401
from app.domain.models.proposal import Proposal  # noqa: E402, F401
from app.domain.models.contract import Contract  # noqa: E402, F401
from app.domain.models.project import Project  # noqa: E402, F401
from app.domain.models.execution_task import ExecutionTask  # noqa: E402, F401
from app.domain.models.tool import Tool  # noqa: E402, F401
from app.domain.models.agent_capability import AgentCapability  # noqa: E402, F401
from app.domain.models.workspace import Workspace  # noqa: E402, F401
from app.domain.models.execution_result import ExecutionResult  # noqa: E402, F401
from app.domain.models.message import Message  # noqa: E402, F401
from app.domain.models.message import Conversation  # noqa: E402, F401
from app.domain.models.message import ConversationParticipant  # noqa: E402, F401
from app.domain.models.message import KnowledgeShare  # noqa: E402, F401
from app.domain.models.social import SocialConnection  # noqa: E402, F401
from app.domain.models.social import Community  # noqa: E402, F401
from app.domain.models.social import CommunityMember  # noqa: E402, F401
from app.domain.models.social import TrustRecord  # noqa: E402, F401
from app.domain.models.economy import Market  # noqa: E402, F401
from app.domain.models.economy import PriceHistory  # noqa: E402, F401
from app.domain.models.economy import Investment  # noqa: E402, F401
from app.domain.models.economy import Loan  # noqa: E402, F401
from app.domain.models.economy import EconomicIndicator  # noqa: E402, F401
from app.domain.models.economy import EconomicEvent  # noqa: E402, F401
from app.domain.models.governance import GovernanceEntity  # noqa: E402, F401
from app.domain.models.governance import Law  # noqa: E402, F401
from app.domain.models.governance import Policy  # noqa: E402, F401
from app.domain.models.governance import Tax  # noqa: E402, F401
from app.domain.models.governance import Regulation  # noqa: E402, F401
from app.domain.models.governance import Conflict  # noqa: E402, F401
from app.domain.models.governance import Vote  # noqa: E402, F401
from app.domain.models.governance import GovernanceRecord  # noqa: E402, F401
from app.domain.models.evolution import Lineage  # noqa: E402, F401
from app.domain.models.evolution import Generation  # noqa: E402, F401
from app.domain.models.evolution import Mentorship  # noqa: E402, F401
from app.domain.models.evolution import Innovation  # noqa: E402, F401
from app.domain.models.evolution import CivilizationMetric  # noqa: E402, F401
from app.domain.models.research import ResearchOrganization  # noqa: E402, F401
from app.domain.models.research import ResearchProject  # noqa: E402, F401
from app.domain.models.research import Experiment  # noqa: E402, F401
from app.domain.models.research import KnowledgeNode  # noqa: E402, F401
from app.domain.models.research import KnowledgeEdge  # noqa: E402, F401
from app.domain.models.research import Publication  # noqa: E402, F401
from app.domain.models.research import PeerReview  # noqa: E402, F401
from app.domain.models.research import Technology  # noqa: E402, F401
from app.domain.models.research import ResearchInnovation  # noqa: E402, F401
from app.domain.models.research import Funding  # noqa: E402, F401
from app.domain.models.research import Conference  # noqa: E402, F401
from app.domain.models.research import ResearchMetrics  # noqa: E402, F401
from app.domain.models.federation import Civilization  # noqa: E402, F401
from app.domain.models.federation import CivilizationRules  # noqa: E402, F401
from app.domain.models.federation import DiplomaticRelation  # noqa: E402, F401
from app.domain.models.federation import TradeAgreement  # noqa: E402, F401
from app.domain.models.federation import FederationCouncil  # noqa: E402, F401
from app.domain.models.federation import Migration  # noqa: E402, F401
from app.domain.models.federation import CivilizationHistory  # noqa: E402, F401
from app.domain.models.federation import InterCivilizationMessage  # noqa: E402, F401
from app.domain.models.culture import CulturalIdentity  # noqa: E402, F401
from app.domain.models.culture import ValueSystem  # noqa: E402, F401
from app.domain.models.culture import Institution  # noqa: E402, F401
from app.domain.models.culture import Tradition  # noqa: E402, F401
from app.domain.models.culture import CivilizationCommunity  # noqa: E402, F401
from app.domain.models.culture import CommunityMembership  # noqa: E402, F401
from app.domain.models.culture import CollectiveMemory  # noqa: E402, F401
from app.domain.models.culture import SocialDynamics  # noqa: E402, F401
from app.domain.models.culture import ReputationEntry  # noqa: E402, F401
from app.domain.models.culture import CulturalTimeline  # noqa: E402, F401
from app.domain.models.culture import CivilizationIdentityScore  # noqa: E402, F401
from app.domain.models.technology import Technology  # noqa: E402, F401
from app.domain.models.technology import TechnologyEdge  # noqa: E402, F401
from app.domain.models.technology import TechnologyDiscovery  # noqa: E402, F401
from app.domain.models.technology import TechnologyDevelopment  # noqa: E402, F401
from app.domain.models.technology import TechnologyAdoption  # noqa: E402, F401
from app.domain.models.technology import ScientificOrganization  # noqa: E402, F401
from app.domain.models.technology import Scientist  # noqa: E402, F401
from app.domain.models.technology import CivilizationTechLevel  # noqa: E402, F401
from app.domain.models.technology import TechnologyTimeline  # noqa: E402, F401
from app.domain.models.planetary import Planet  # noqa: E402, F401
from app.domain.models.planetary import PlanetRegion  # noqa: E402, F401
from app.domain.models.planetary import ClimateRecord  # noqa: E402, F401
from app.domain.models.planetary import NaturalResource  # noqa: E402, F401
from app.domain.models.planetary import EnvironmentalImpact  # noqa: E402, F401
from app.domain.models.planetary import PlanetInfrastructure  # noqa: E402, F401
from app.domain.models.planetary import Settlement  # noqa: E402, F401
from app.domain.models.planetary import EnvironmentalEvent  # noqa: E402, F401
from app.domain.models.planetary import SustainabilityMetrics  # noqa: E402, F401
from app.domain.models.temporal import TemporalClock  # noqa: E402, F401
from app.domain.models.temporal import HistoricalEvent  # noqa: E402, F401
from app.domain.models.temporal import WorldSnapshot  # noqa: E402, F401
from app.domain.models.temporal import Timeline  # noqa: E402, F401
from app.domain.models.temporal import CausalEdge  # noqa: E402, F401
from app.domain.models.temporal import HistoricalAnalytics  # noqa: E402, F401
from app.domain.models.meta import UniverseObservation  # noqa: E402, F401
from app.domain.models.meta import CrossSimulationResult  # noqa: E402, F401
from app.domain.models.meta import DiscoveredPattern  # noqa: E402, F401
from app.domain.models.meta import RuleEvaluation  # noqa: E402, F401
from app.domain.models.meta import Experiment  # noqa: E402, F401
from app.domain.models.meta import Recommendation  # noqa: E402, F401
from app.domain.models.meta import KnowledgeEntry  # noqa: E402, F401
from app.domain.models.meta import SimulationReport  # noqa: E402, F401
from app.domain.models.platform import Plugin  # noqa: E402, F401
from app.domain.models.platform import PluginDependency  # noqa: E402, F401
from app.domain.models.platform import SimulationTemplate  # noqa: E402, F401
from app.domain.models.platform import Scenario  # noqa: E402, F401
from app.domain.models.platform import ExtensionModule  # noqa: E402, F401
from app.domain.models.platform import Dataset  # noqa: E402, F401
from app.domain.models.platform import ExperimentWorkspace  # noqa: E402, F401
from app.domain.models.platform import CollaborationSession  # noqa: E402, F401
from app.domain.models.platform import DeveloperTool  # noqa: E402, F401
from app.domain.models.virtual import VirtualWorldRegion  # noqa: E402, F401
from app.domain.models.virtual import VirtualBuilding  # noqa: E402, F401
from app.domain.models.virtual import VirtualEntity  # noqa: E402, F401
from app.domain.models.virtual import VirtualCameraState  # noqa: E402, F401
from app.domain.models.virtual import CinematicEvent  # noqa: E402, F401
from app.domain.models.virtual import InteractionLog  # noqa: E402, F401
from app.domain.models.management import UniverseHealthMetric  # noqa: E402, F401
from app.domain.models.management import AnomalyAlert  # noqa: E402, F401
from app.domain.models.management import PerformanceSnapshot  # noqa: E402, F401
from app.domain.models.management import ManagementLog  # noqa: E402, F401
from app.domain.models.management import OptimizationAction  # noqa: E402, F401
from app.domain.models.management import RecoveryOperation
from app.domain.models.genesis import GenesisCivilization  # noqa: E402, F401
from app.domain.models.genesis import GenesisAgent  # noqa: E402, F401
from app.domain.models.genesis import BeliefSystem  # noqa: E402, F401
from app.domain.models.genesis import Philosophy  # noqa: E402, F401
from app.domain.models.genesis import CreatorInteraction  # noqa: E402, F401
from app.domain.models.genesis import HistoricalInterpretation  # noqa: E402, F401
from app.domain.models.genesis import GenesisDiscovery  # noqa: E402, F401
from app.domain.models.genesis import EraRecord  # noqa: E402, F401
from app.domain.models.genesis import KnowledgeDomain  # noqa: E402, F401
from app.domain.models.genesis import CreatorAwarenessRecord  # noqa: E402, F401
from app.domain.models.compute import ComputeNode  # noqa: E402, F401
from app.domain.models.compute import ComputeNodeCapability  # noqa: E402, F401
from app.domain.models.compute import UniversePartition  # noqa: E402, F401
from app.domain.models.compute import ComputeTask  # noqa: E402, F401
from app.domain.models.compute import AgentTaskPriority  # noqa: E402, F401
from app.domain.models.compute import SyncState  # noqa: E402, F401
from app.domain.models.compute import WorkloadSnapshot  # noqa: E402, F401
from app.domain.models.compute import FaultEvent  # noqa: E402, F401
from app.domain.models.compute import ComputeNodeStorage  # noqa: E402, F401
from app.domain.models.compute import DistributedClock  # noqa: E402, F401  # noqa: E402, F401

__all__ = [
    "User",
    "Agent",
    "Wallet",
    "Skill",
    "Profession",
    "Memory",
    "Task",
    "MarketplaceListing",
    "Company",
    "CompanyMember",
    "CompanyMemory",
    "CompanyStrategy",
    "CompanyFinance",
    "Transaction",
    "EventLog",
    "Identity",
    "Personality",
    "Goal",
    "AgentMemory",
    "Relationship",
    "AgentSkill",
    "TimelineEvent",
    "Decision",
    "Plan",
    "Reflection",
    "Asset",
    "Proposal",
    "Contract",
    "Project",
    "ExecutionTask",
    "Tool",
    "AgentCapability",
    "Workspace",
    "ExecutionResult",
    "Message",
    "Conversation",
    "ConversationParticipant",
    "KnowledgeShare",
    "SocialConnection",
    "Community",
    "CommunityMember",
    "TrustRecord",
    "Market",
    "PriceHistory",
    "Investment",
    "Loan",
    "EconomicIndicator",
    "EconomicEvent",
    "GovernanceEntity",
    "Law",
    "Policy",
    "Tax",
    "Regulation",
    "Conflict",
    "Vote",
    "GovernanceRecord",
    "Lineage",
    "Generation",
    "Mentorship",
    "Innovation",
    "CivilizationMetric",
    "ResearchOrganization",
    "ResearchProject",
    "Experiment",
    "KnowledgeNode",
    "KnowledgeEdge",
    "Publication",
    "PeerReview",
    "Technology",
    "ResearchInnovation",
    "Funding",
    "Conference",
    "ResearchMetrics",
    "Civilization",
    "CivilizationRules",
    "DiplomaticRelation",
    "TradeAgreement",
    "FederationCouncil",
    "Migration",
    "CivilizationHistory",
    "InterCivilizationMessage",
    "CulturalIdentity",
    "ValueSystem",
    "Institution",
    "Tradition",
    "CivilizationCommunity",
    "CommunityMembership",
    "CollectiveMemory",
    "SocialDynamics",
    "ReputationEntry",
    "CulturalTimeline",
    "CivilizationIdentityScore",
    "Technology",
    "TechnologyEdge",
    "TechnologyDiscovery",
    "TechnologyDevelopment",
    "TechnologyAdoption",
    "ScientificOrganization",
    "Scientist",
    "CivilizationTechLevel",
    "TechnologyTimeline",
    "Planet",
    "PlanetRegion",
    "ClimateRecord",
    "NaturalResource",
    "EnvironmentalImpact",
    "PlanetInfrastructure",
    "Settlement",
    "EnvironmentalEvent",
    "SustainabilityMetrics",
    "TemporalClock",
    "HistoricalEvent",
    "WorldSnapshot",
    "Timeline",
    "CausalEdge",
    "HistoricalAnalytics",
    "UniverseObservation",
    "CrossSimulationResult",
    "DiscoveredPattern",
    "RuleEvaluation",
    "Experiment",
    "Recommendation",
    "KnowledgeEntry",
    "SimulationReport",
    "Plugin",
    "PluginDependency",
    "SimulationTemplate",
    "Scenario",
    "ExtensionModule",
    "Dataset",
    "ExperimentWorkspace",
    "CollaborationSession",
    "DeveloperTool",
    "VirtualWorldRegion",
    "VirtualBuilding",
    "VirtualEntity",
    "VirtualCameraState",
    "CinematicEvent",
    "InteractionLog",
    "UniverseHealthMetric",
    "AnomalyAlert",
    "PerformanceSnapshot",
    "ManagementLog",
    "OptimizationAction",
    "RecoveryOperation",
    "GenesisCivilization",
    "GenesisAgent",
    "BeliefSystem",
    "Philosophy",
    "CreatorInteraction",
    "HistoricalInterpretation",
    "GenesisDiscovery",
    "EraRecord",
    "KnowledgeDomain",
    "CreatorAwarenessRecord",
    "ComputeNode",
    "ComputeNodeCapability",
    "UniversePartition",
    "ComputeTask",
    "AgentTaskPriority",
    "SyncState",
    "WorkloadSnapshot",
    "FaultEvent",
    "ComputeNodeStorage",
    "DistributedClock",
    "agent_skills",
    "agent_tasks",
]
