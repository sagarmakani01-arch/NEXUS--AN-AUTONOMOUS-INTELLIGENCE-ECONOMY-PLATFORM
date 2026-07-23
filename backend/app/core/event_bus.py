import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger("nexus.events")


class EventType(str, Enum):
    AGENT_CREATED = "AgentCreated"
    AGENT_UPDATED = "AgentUpdated"
    AGENT_DELETED = "AgentDeleted"
    WALLET_CREATED = "WalletCreated"
    WALLET_UPDATED = "WalletUpdated"
    TASK_POSTED = "TaskPosted"
    TASK_COMPLETED = "TaskCompleted"
    TASK_UPDATED = "TaskUpdated"
    TRANSACTION_CREATED = "TransactionCreated"
    SIMULATION_TICK = "SimulationTick"
    USER_REGISTERED = "UserRegistered"
    LISTING_CREATED = "ListingCreated"
    LISTING_COMPLETED = "ListingCompleted"
    PROPOSAL_SUBMITTED = "ProposalSubmitted"
    PROPOSAL_ACCEPTED = "ProposalAccepted"
    PROPOSAL_REJECTED = "ProposalRejected"
    PROPOSAL_COUNTERED = "ProposalCountered"
    CONTRACT_CREATED = "ContractCreated"
    CONTRACT_ACCEPTED = "ContractAccepted"
    CONTRACT_COMPLETED = "ContractCompleted"
    CONTRACT_FAILED = "ContractFailed"
    MARKETPLACE_TICK = "MarketplaceTick"
    TASK_ASSIGNED = "TaskAssigned"
    PROJECT_CREATED = "ProjectCreated"
    PROJECT_COMPLETED = "ProjectCompleted"
    EXECUTION_STARTED = "ExecutionStarted"
    EXECUTION_PAUSED = "ExecutionPaused"
    EXECUTION_RESUMED = "ExecutionResumed"
    TOOL_USED = "ToolUsed"
    PROGRESS_UPDATED = "ProgressUpdated"
    SKILL_IMPROVED = "SkillImproved"
    TEAM_CREATED = "TeamCreated"
    COMPANY_CREATED = "CompanyCreated"
    COMPANY_FAILED = "CompanyFailed"
    COMPANY_MERGED = "CompanyMerged"
    EMPLOYEE_HIRED = "EmployeeHired"
    EMPLOYEE_REMOVED = "EmployeeRemoved"
    EMPLOYEE_PROMOTED = "EmployeePromoted"
    STRATEGY_CHANGED = "StrategyChanged"
    REVENUE_GENERATED = "RevenueGenerated"
    PARTNERSHIP_FORMED = "PartnershipFormed"
    MESSAGE_SENT = "MessageSent"
    MESSAGE_RECEIVED = "MessageReceived"
    RELATIONSHIP_CREATED = "RelationshipCreated"
    TRUST_CHANGED = "TrustChanged"
    KNOWLEDGE_SHARED = "KnowledgeShared"
    COMMUNITY_FORMED = "CommunityFormed"
    COMMUNITY_JOINED = "CommunityJoined"
    COMMUNICATION_TICK = "CommunicationTick"
    PRICE_CHANGED = "PriceChanged"
    MARKET_CREATED = "MarketCreated"
    INVESTMENT_MADE = "InvestmentMade"
    LOAN_ISSUED = "LoanIssued"
    COMPANY_BANKRUPT = "CompanyBankrupt"
    RESOURCE_SHORTAGE = "ResourceShortage"
    ECONOMIC_GROWTH = "EconomicGrowth"
    ECONOMIC_RECESSION = "EconomicRecession"
    WEALTH_CHANGED = "WealthChanged"
    LAW_CREATED = "LawCreated"
    POLICY_CHANGED = "PolicyChanged"
    TAX_COLLECTED = "TaxCollected"
    CONFLICT_STARTED = "ConflictStarted"
    CONFLICT_RESOLVED = "ConflictResolved"
    VOTE_COMPLETED = "VoteCompleted"
    AUTHORITY_CREATED = "AuthorityCreated"
    REGULATION_VIOLATION = "RegulationViolation"
    CITIZEN_GENERATED = "CitizenGenerated"
    LINEAGE_CREATED = "LineageCreated"
    MENTORSHIP_STARTED = "MentorshipStarted"
    INNOVATION_DISCOVERED = "InnovationDiscovered"
    CIVILIZATION_EVOLVED = "CivilizationEvolved"
    EVOLUTION_TICK = "EvolutionTick"
    RESEARCH_STARTED = "ResearchStarted"
    EXPERIMENT_COMPLETED = "ExperimentCompleted"
    PUBLICATION_RELEASED = "PublicationReleased"
    TECHNOLOGY_UNLOCKED = "TechnologyUnlocked"
    FUNDING_GRANTED = "FundingGranted"
    PEER_REVIEW_COMPLETED = "PeerReviewCompleted"
    RESEARCH_TICK = "ResearchTick"
    CIVILIZATION_CREATED = "CivilizationCreated"
    ALLIANCE_FORMED = "AllianceFormed"
    TRADE_STARTED = "TradeStarted"
    TECHNOLOGY_SHARED = "TechnologyShared"
    MIGRATION_STARTED = "MigrationStarted"
    DIPLOMATIC_CHANGE = "DiplomaticChange"
    CIVILIZATION_MILESTONE = "CivilizationMilestone"
    INSTITUTION_FOUNDED = "InstitutionFounded"
    COMMUNITY_CREATED = "CommunityCreated"
    TRADITION_ESTABLISHED = "TraditionEstablished"
    CULTURAL_MILESTONE = "CulturalMilestone"
    HISTORICAL_EVENT_RECORDED = "HistoricalEventRecorded"
    VALUE_SHIFT_DETECTED = "ValueShiftDetected"
    DISCOVERY_MADE = "DiscoveryMade"
    PROTOTYPE_CREATED = "PrototypeCreated"
    TECHNOLOGY_ADOPTED = "TechnologyAdopted"
    TECHNOLOGY_REPLACED = "TechnologyReplaced"
    SCIENTIFIC_BREAKTHROUGH = "ScientificBreakthrough"
    NEW_INDUSTRY_CREATED = "NewIndustryCreated"
    PLANET_CREATED = "PlanetCreated"
    SETTLEMENT_FOUNDED = "SettlementFounded"
    RESOURCE_DISCOVERED = "ResourceDiscovered"
    INFRASTRUCTURE_COMPLETED = "InfrastructureCompleted"
    CLIMATE_CHANGED = "ClimateChanged"
    ENVIRONMENTAL_EVENT_OCCURRED = "EnvironmentalEventOccurred"
    SNAPSHOT_CREATED = "SnapshotCreated"
    TIMELINE_BRANCHED = "TimelineBranched"
    REPLAY_STARTED = "ReplayStarted"
    REPLAY_STOPPED = "ReplayStopped"
    TEMPORAL_MILESTONE = "TemporalMilestone"
    TIMELINE_COMPARED = "TimelineCompared"
    PATTERN_DISCOVERED = "PatternDiscovered"
    META_EXPERIMENT_COMPLETED = "MetaExperimentCompleted"
    RECOMMENDATION_GENERATED = "RecommendationGenerated"
    UNIVERSE_INSIGHT_RECORDED = "UniverseInsightRecorded"
    PLUGIN_INSTALLED = "PluginInstalled"
    MODULE_UPDATED = "ModuleUpdated"
    PLATFORM_SCENARIO_CREATED = "PlatformScenarioCreated"
    DATASET_EXPORTED = "DatasetExported"
    REGION_EXPLORED = "RegionExplored"
    CINEMATIC_EVENT_TRIGGERED = "CinematicEventTriggered"
    CITIZEN_OBSERVED = "CitizenObserved"
    HEALTH_METRIC_RECORDED = "HealthMetricRecorded"
    ANOMALY_DETECTED = "AnomalyDetected"
    PERFORMANCE_SNAPSHOT = "PerformanceSnapshot"
    INTEGRITY_CHECK_PASSED = "IntegrityCheckPassed"
    RECOVERY_OPERATION = "RecoveryOperation"
    MANAGEMENT_ACTION = "ManagementAction"
    SYSTEM_LOG = "SystemLog"
    GENESIS_CIVILIZATION_CREATED = "GenesisCivilizationCreated"
    GENESIS_DISCOVERY = "GenesisDiscovery"
    GENESIS_ERA_TRANSITION = "GenesisEraTransition"
    GENESIS_BELIEF_EMERGED = "GenesisBeliefEmerged"
    GENESIS_AWARENESS_SHIFT = "GenesisAwarenessShift"
    GENESIS_CREATOR_INTERACTION = "GenesisCreatorInteraction"
    GENESIS_TICK = "GenesisTick"
    NODE_CONNECTED = "NodeConnected"
    NODE_DISCONNECTED = "NodeDisconnected"
    EXPERIMENT_STARTED = "ExperimentStarted"
    PATTERN_DETECTED = "PatternDetected"
    HYPOTHESIS_GENERATED = "HypothesisGenerated"
    DISCOVERY_RECORDED = "DiscoveryRecorded"
    REPORT_CREATED = "ReportCreated"
    TASK_ASSIGNED = "TaskAssigned"
    TASK_COMPLETED = "TaskCompleted"
    SIMULATION_MIGRATED = "SimulationMigrated"
    RECOVERY_STARTED = "RecoveryStarted"
    RECOVERY_COMPLETED = "RecoveryCompleted"
    WORKLOAD_REBALANCED = "WorkloadRebalanced"
    CLOCK_SYNCED = "ClockSynced"


class Event:
    def __init__(self, event_type: EventType, payload: dict[str, Any]) -> None:
        self.event_type = event_type
        self.payload = payload
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.event_id = f"{event_type.value}_{int(datetime.now(timezone.utc).timestamp())}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


_subscribers: dict[EventType, list[Callable]] = defaultdict(list)


async def publish(event: Event) -> None:
    logger.info("event_published event_type=%s event_id=%s", event.event_type.value, event.event_id)


async def log_event(event: Event) -> None:
    from app.core.database import async_session_factory
    from app.domain.models.event_log import EventLog

    async with async_session_factory() as session:
        log_entry = EventLog(
            event_type=event.event_type.value,
            payload=event.payload,
            event_id=event.event_id,
        )
        session.add(log_entry)
        await session.commit()


def subscribe(event_type: EventType, handler: Callable) -> None:
    _subscribers[event_type].append(handler)


async def dispatch(event: Event) -> None:
    await publish(event)
    try:
        await log_event(event)
    except Exception as exc:
        logger.error("event_log_failed error=%s", str(exc))
    for handler in _subscribers.get(event.event_type, []):
        try:
            result = handler(event)
            if hasattr(result, "__await__"):
                await result
        except Exception as exc:
            logger.error("event_handler_failed error=%s event_type=%s", str(exc), event.event_type.value)
