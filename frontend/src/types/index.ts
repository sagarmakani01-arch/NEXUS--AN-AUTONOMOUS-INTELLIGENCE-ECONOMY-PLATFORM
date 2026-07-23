export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  is_active: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface WorldClock {
  day: number;
  hour: number;
  minute: number;
  tick_count: number;
  time_str: string;
  total_minutes: number;
}

export interface WorldState {
  clock: WorldClock;
  population: number;
  running_agents: number;
  idle_agents: number;
  working_agents: number;
  searching_agents: number;
  resting_agents: number;
  avg_energy: number;
  avg_reputation: number;
  total_events: number;
  events_per_second: number;
}

export interface SimulationState {
  state: string;
  speed: number;
  world: WorldState;
  uptime: number;
  agents_count: number;
  reasoning: Record<string, unknown>;
  marketplace: MarketplaceEngineState;
  execution: ExecutionEngineState;
  companies: CompanyEngineState;
  communication: CommunicationEngineState;
  economy: EconomyEngineState;
  governance: GovernanceEngineState;
  discovery: DiscoveryEngineState;
}

export interface MarketplaceEngineState {
  running: boolean;
  stats: {
    tasks_created: number;
    proposals_submitted: number;
    contracts_completed: number;
    total_volume: number;
  };
  tick_interval: number;
}

export interface SimAgent {
  id: string;
  name: string;
  profession: string;
  profession_category: string;
  skills: string[];
  personality: Record<string, number>;
  current_status: string;
  energy: number;
  reputation: number;
  wallet_balance: number;
  current_goal: string;
  state_duration: number;
  total_work_done: number;
  tasks_completed: number;
}

export interface SimEvent {
  event_id: string;
  event_type: string;
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface Agent {
  id: string;
  owner_id: string;
  name: string;
  profession_id: string | null;
  personality_profile: Record<string, unknown>;
  reputation: number;
  current_goal: string | null;
  current_status: string;
  energy: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  posted_by: string;
  title: string;
  description: string | null;
  required_skills: string[];
  reward: number;
  status: string;
  priority: string;
  deadline: string | null;
  result: string | null;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  owner_id: string;
  founder_agent_id: string | null;
  name: string;
  description: string | null;
  mission: string | null;
  vision: string | null;
  industry: string | null;
  status: string;
  employee_count: number;
  treasury_balance: number;
  revenue: number;
  expenses: number;
  salary_budget: number;
  reputation: number;
  company_age: number;
  total_projects: number;
  successful_projects: number;
  failed_projects: number;
  market_share: number;
  growth_rate: number;
  culture_score: number;
  member_agent_ids: string[];
  departments: string[];
  metadata_: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CompanyMember {
  id: string;
  company_id: string;
  agent_id: string;
  role: string;
  department: string | null;
  title: string | null;
  salary: number;
  performance_score: number;
  hire_date: string | null;
  status: string;
  reports_to: string | null;
  metadata_: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CompanyMemory {
  id: string;
  company_id: string;
  event_type: string;
  title: string;
  description: string | null;
  importance: string;
  metadata_: Record<string, unknown>;
  created_at: string;
}

export interface CompanyStrategy {
  id: string;
  company_id: string;
  title: string;
  description: string | null;
  strategy_type: string;
  goal: string | null;
  resources_required: Record<string, unknown>;
  timeline_days: number;
  progress: number;
  status: string;
  expected_outcome: string | null;
  actual_outcome: string | null;
  metadata_: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface CompanyFinance {
  id: string;
  company_id: string;
  transaction_type: string;
  amount: number;
  category: string | null;
  description: string | null;
  reference_id: string | null;
  reference_type: string | null;
  balance_after: number;
  created_at: string;
}

export interface CompanyProfile {
  company: Company;
  organization: OrgChart;
  strategies: CompanyStrategy[];
  recent_finances: CompanyFinance[];
  recent_memories: CompanyMemory[];
  health: CompanyHealth;
  financial_report: FinancialReport;
  member_count: number;
}

export interface OrgChart {
  company_id: string;
  ceo: CompanyMember | null;
  vps: CompanyMember[];
  directors: CompanyMember[];
  managers: CompanyMember[];
  leads: CompanyMember[];
  employees: CompanyMember[];
  departments: DepartmentInfo[];
  department_members: Record<string, CompanyMember[]>;
  total_members: number;
}

export interface DepartmentInfo {
  name: string;
  head_count: number;
  budget: number;
  status: string;
}

export interface CompanyHealth {
  company_id: string;
  health: string;
  balance: number;
  revenue: number;
  expenses: number;
  profit_margin: number;
  employees: number;
  reputation: number;
}

export interface FinancialReport {
  company_id: string;
  treasury_balance: number;
  total_revenue: number;
  total_expenses: number;
  profit_loss: number;
  salary_expenses: number;
  transaction_count: number;
  revenue_transactions: number;
  expense_transactions: number;
}

export interface CompanyStats {
  statuses: Record<string, number>;
  industries: Record<string, number>;
  total_companies: number;
  avg_reputation: number;
  total_employees: number;
}

export interface AgentCompanyState {
  is_employee: boolean;
  memberships: {
    company_id: string;
    role: string;
    department: string | null;
    title: string | null;
    salary: number;
  }[];
}

export interface CompanyEngineState {
  running: boolean;
  active_companies: number;
}

export interface DashboardStats {
  total_agents: number;
  active_agents: number;
  active_tasks: number;
  total_users: number;
  total_companies: number;
  total_transactions: number;
  economy_status: string;
  compute_usage: string;
  simulation_status: string;
  world_time: string | null;
  simulation_speed: number;
  avg_energy: number;
  avg_reputation: number;
  working_agents: number;
  idle_agents: number;
  searching_agents: number;
  resting_agents: number;
  events_per_second: number;
  population: number;
}

export interface AgentIdentity {
  first_name: string;
  last_name: string;
  display_name: string;
  generation: number;
  status: string;
  profession: string;
  profession_category: string;
}

export interface AgentPersonality {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
  traits: string[];
  communication_style: string;
  work_style: string;
}

export interface AgentGoal {
  title: string;
  category: string;
  progress: number;
  target: number;
}

export interface AgentSkill {
  skill_name: string;
  level: number;
  experience: number;
  max_experience: number;
  learning_progress: number;
  certified: boolean;
}

export interface AgentMemory {
  id: string;
  agent_id: string;
  category: string;
  title: string;
  description: string;
  importance: string;
  related_agent_id: string | null;
  created_at: string;
}

export interface AgentTimelineEvent {
  id: string;
  agent_id: string;
  day: number;
  event_type: string;
  title: string;
  description: string;
  created_at: string;
}

export interface AgentRelationship {
  other_agent_id: string;
  other_name: string;
  other_profession: string;
  trust: number;
  respect: number;
  strength: number;
  collaboration_count: number;
  conflict_count: number;
}

export interface AgentProfile {
  id: string;
  name: string;
  current_status: string;
  energy: number;
  reputation: number;
  wallet_balance: number;
  current_goal: string;
  identity: AgentIdentity;
  personality: AgentPersonality;
  goal: AgentGoal;
  skills: AgentSkill[];
  trust_score: number;
  memories: AgentMemory[];
  timeline: AgentTimelineEvent[];
  relationships: AgentRelationship[];
  reasoning: AgentReasoningState;
  resources: AgentResources;
  marketplace: AgentMarketplaceState;
  execution: AgentExecutionState;
  company: AgentCompanyState;
  communication: AgentCommunicationState;
  economy: AgentEconomyState;
  governance: AgentGovernanceState;
}

export interface AgentMarketplaceState {
  proposals: Proposal[];
  contracts: Contract[];
  stats: ContractStats;
}

export interface AgentResources {
  wallet: FinancialSummary;
  daily: DailySummary;
  compute: ComputeInfo;
  allocation: ResourceAllocation;
}

export interface FinancialSummary {
  agent_id: string;
  wallet_balance: number;
  reserved_balance: number;
  compute_credits: number;
  total_earned: number;
  total_spent: number;
  asset_value: number;
  asset_count: number;
  net_worth: number;
  financial_health: string;
}

export interface DailySummary {
  agent_id: string;
  date: string;
  income: number;
  expenses: number;
  net: number;
  compute_used: number;
  transaction_count: number;
}

export interface ComputeInfo {
  agent_id: string;
  compute_credits: number;
  compute_used: number;
  total_compute_lifetime: number;
  efficiency: number;
}

export interface ResourceAllocation {
  agent_id: string;
  cash_allocation: number;
  reserved_allocation: number;
  asset_allocation: number;
  compute_allocation: number;
}

export interface Wallet {
  id: string;
  agent_id: string;
  balance: number;
  reserved_balance: number;
  total_earned: number;
  total_spent: number;
  compute_credits: number;
  compute_used: number;
  currency: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  from_wallet_id: string | null;
  to_wallet_id: string | null;
  amount: number;
  currency: string;
  transaction_type: string;
  status: string;
  notes: string | null;
  created_at: string;
}

export interface Asset {
  id: string;
  agent_id: string;
  asset_type: string;
  name: string;
  description: string;
  value: number;
  purchase_price: number;
  maintenance_cost: number;
  condition_score: number;
  quantity: number;
  status: string;
  acquired_at: string;
}

export interface AgentReasoningState {
  agent_id: string;
  current_decision: Decision | null;
  current_plan: Plan | null;
  reasoning_status: string;
  total_decisions: number;
  total_reflections: number;
  provider_used: string;
  last_reasoning_duration_ms: number;
}

export interface Decision {
  id: string;
  agent_id: string;
  trigger_type: string;
  decision: string;
  reasoning_summary: string;
  confidence: number;
  expected_outcome: string;
  risk_level: string;
  estimated_cost: number;
  estimated_reward: number;
  next_goal: string;
  alternative_options: string[];
  provider_used: string;
  reasoning_duration_ms: number;
  status: string;
  created_at: string;
}

export interface Plan {
  id: string;
  agent_id: string;
  goal: string;
  status: string;
  milestones: PlanMilestone[];
  progress: number;
  evaluation: Record<string, unknown>;
  started_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface PlanMilestone {
  id: string;
  title: string;
  tasks: PlanTask[];
  completed: boolean;
}

export interface PlanTask {
  id: string;
  title: string;
  actions: PlanAction[];
  completed: boolean;
}

export interface PlanAction {
  id: string;
  title: string;
  estimated_duration: number;
  cost: number;
  completed: boolean;
}

export interface Reflection {
  id: string;
  agent_id: string;
  decision_id: string;
  expected_outcome: string;
  actual_outcome: string;
  lessons_learned: string[];
  success_rate: number;
  failure_cause: string | null;
  experience_gain: number;
  created_at: string;
}

export interface ReasoningHistory {
  decisions: Decision[];
  reflections: Reflection[];
  plans: Plan[];
  success_rate: number;
  lessons_learned: string[];
  stats: {
    total_decisions: number;
    total_reflections: number;
    current_status: string;
    provider_used: string;
    last_reasoning_duration_ms: number;
  };
  queue_stats: {
    queue_size: number;
    active_count: number;
    completed_count: number;
    total_processed: number;
    total_errors: number;
    cache_size: number;
    error_rate: number;
  };
}

export interface Proposal {
  id: string;
  task_id: string;
  agent_id: string;
  proposed_reward: number;
  cover_letter: string | null;
  estimated_duration: string | null;
  status: string;
  counter_reward: number | null;
  counter_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface Contract {
  id: string;
  task_id: string;
  proposal_id: string;
  poster_id: string;
  agent_id: string;
  agreed_reward: number;
  status: string;
  terms: string | null;
  result: string | null;
  rating: number | null;
  feedback: string | null;
  created_at: string;
  accepted_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  failed_at: string | null;
}

export interface ContractStats {
  total: number;
  completed: number;
  failed: number;
  active: number;
  avg_rating: number;
  success_rate: number;
  total_earned: number;
}

export interface MarketplaceStats {
  tasks: Record<string, number>;
  proposals: Record<string, number>;
  contracts: Record<string, number>;
  total_tasks: number;
  total_proposals: number;
  total_contracts: number;
  total_volume: number;
  avg_task_reward: number;
  engine_stats: {
    tasks_created: number;
    proposals_submitted: number;
    contracts_completed: number;
    total_volume: number;
  };
  running: boolean;
}

export interface MatchedTask {
  id: string;
  title: string;
  description: string | null;
  required_skills: string[];
  reward: number;
  status: string;
  priority: string;
  match_score: number;
}

export interface Project {
  id: string;
  agent_id: string;
  contract_id: string | null;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  progress: number;
  estimated_cost: number;
  actual_cost: number;
  quality_score: number | null;
  metadata_json: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface ExecutionTask {
  id: string;
  project_id: string;
  parent_task_id: string | null;
  agent_id: string | null;
  title: string;
  description: string | null;
  required_skills: string[];
  status: string;
  priority: string;
  dependencies: string[];
  estimated_cost: number;
  actual_cost: number;
  estimated_duration: number;
  actual_duration: number;
  retry_count: number;
  max_retries: number;
  quality_score: number | null;
  result: string | null;
  error_message: string | null;
  metadata_json: string;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface Tool {
  id: string;
  name: string;
  description: string | null;
  tool_type: string;
  required_permission: string;
  cost_per_use: number;
  input_schema: string;
  output_schema: string;
  status: string;
  total_uses: number;
  avg_execution_time: number;
  success_rate: number;
  metadata_json: string;
  created_at: string;
  updated_at: string;
}

export interface AgentCapability {
  id: string;
  agent_id: string;
  skill_name: string;
  level: string;
  proficiency: number;
  experience: number;
  projects_completed: number;
  success_rate: number;
  last_used: string | null;
  metadata_json: string;
  created_at: string;
  updated_at: string;
}

export interface Workspace {
  id: string;
  agent_id: string;
  project_id: string | null;
  name: string;
  description: string | null;
  files: WorkspaceFile[];
  notes: string;
  artifacts: WorkspaceArtifact[];
  task_history: TaskHistoryEntry[];
  status: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceFile {
  name: string;
  type: string;
  size: number;
  content_preview: string;
}

export interface WorkspaceArtifact {
  name: string;
  type: string;
  description: string;
}

export interface TaskHistoryEntry {
  task_id: string;
  status: string;
  result: string;
}

export interface ExecutionResult {
  id: string;
  task_id: string;
  agent_id: string;
  project_id: string;
  status: string;
  quality_score: number;
  requirements_met: number;
  errors_count: number;
  efficiency_score: number;
  user_satisfaction: number;
  deliverables: string[];
  feedback: string | null;
  lessons_learned: string[];
  tools_used: string[];
  duration_seconds: number;
  cost_incurred: number;
  metadata_json: string;
  created_at: string;
}

export interface AgentExecutionState {
  capabilities: AgentCapabilitiesProfile;
  projects: Project[];
  workspaces: Workspace[];
  learning_stats: LearningStats;
}

export interface AgentCapabilitiesProfile {
  agent_id: string;
  capabilities: AgentCapability[];
  total_skills: number;
  avg_proficiency: number;
  avg_success_rate: number;
  expert_skills: number;
  advanced_skills: number;
}

export interface LearningStats {
  agent_id: string;
  total_tasks_executed: number;
  tasks_completed: number;
  completion_rate: number;
  total_skills: number;
  total_experience: number;
  avg_success_rate: number;
  total_lessons_learned: number;
  expert_skills: number;
  advanced_skills: number;
}

export interface ExecutionEngineState {
  running: boolean;
  stats: {
    projects_created: number;
    tasks_executed: number;
    tasks_completed: number;
    tasks_failed: number;
    tools_used: number;
  };
  active_projects: number;
}

export interface CostEstimate {
  total_estimated_cost: number;
  total_estimated_duration: number;
  task_count: number;
  required_skills: string[];
}

export interface Message {
  id: string;
  sender_id: string;
  sender_type: string;
  receiver_id: string;
  receiver_type: string;
  conversation_id: string | null;
  message_type: string;
  content: string;
  priority: string;
  status: string;
  reply_to_id: string | null;
  metadata_json: string;
  created_at: string;
  read_at: string | null;
}

export interface Conversation {
  id: string;
  title: string | null;
  topic: string | null;
  conversation_type: string;
  summary: string | null;
  decisions: string | null;
  outcome: string | null;
  status: string;
  message_count: number;
  participants: ConversationParticipant[];
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface ConversationParticipant {
  id: string;
  participant_id: string;
  participant_type: string;
  role: string;
  notification_count: number;
}

export interface SocialConnection {
  id: string;
  other_id: string;
  other_type: string;
  relationship_type: string;
  trust_level: number;
  relationship_strength: number;
  interaction_count: number;
  shared_knowledge_count: number;
  sentiment_score: number;
  last_interaction_at: string | null;
}

export interface SocialNetwork {
  entity_id: string;
  total_connections: number;
  connections: SocialConnection[];
  trust_network: {
    high_trust: SocialConnection[];
    medium_trust: SocialConnection[];
    low_trust: SocialConnection[];
  };
  relationship_summary: Record<string, number>;
}

export interface TrustAssessment {
  entity_a_id: string;
  entity_b_id: string;
  trust_level: number;
  trust_level_label: string;
  trend: string;
  total_interactions: number;
  affects: {
    hiring: boolean;
    partnership: boolean;
    information_sharing: boolean;
    negotiation_willingness: boolean;
  };
  history: TrustRecord[];
}

export interface TrustRecord {
  id: string;
  change_amount: number;
  reason: string;
  interaction_type: string;
  previous_trust: number;
  new_trust: number;
  created_at: string;
}

export interface TrustOverview {
  entity_id: string;
  average_trust: number;
  highest_trust: { entity_id: string; trust_level: number } | null;
  lowest_trust: { entity_id: string; trust_level: number } | null;
  trusted_partners: number;
  distrusted_partners: number;
  total_connections: number;
}

export interface KnowledgeShare {
  id: string;
  owner_id: string;
  owner_type: string;
  knowledge_type: string;
  title: string;
  content: string;
  visibility: string;
  tags: string[];
  access_count: number;
  rating: number;
  created_at: string;
}

export interface EntityKnowledge {
  entity_id: string;
  private_knowledge: KnowledgeShare[];
  team_knowledge: KnowledgeShare[];
  public_knowledge: KnowledgeShare[];
  stats: {
    private_count: number;
    team_count: number;
    public_count: number;
  };
}

export interface Community {
  id: string;
  name: string;
  description: string | null;
  community_type: string;
  purpose: string | null;
  industry: string | null;
  member_count: number;
  knowledge_pool_size: number;
  reputation: number;
  status: string;
  founded_by: string | null;
  members: CommunityMember[];
  created_at: string;
}

export interface CommunityMember {
  id: string;
  member_id: string;
  member_type: string;
  role: string;
  contribution_score: number;
  knowledge_shared: number;
  joined_at: string;
}

export interface SocialIntelligence {
  entity_id: string;
  social_capital: number;
  network_diversity: number;
  influence_score: number;
  communication_effectiveness: number;
  total_connections: number;
  high_trust_connections: number;
  relationship_types: string[];
}

export interface CommunicationContext {
  sender_id: string;
  receiver_id: string;
  relationship_type: string;
  trust_level: number;
  trust_trend: string;
  recommended_strategy: {
    tone: string;
    detail_level: string;
    formality: string;
    approach: string;
  };
  affects: Record<string, boolean>;
}

export interface AgentCommunicationState {
  inbox: {
    conversations: Conversation[];
    recent_messages: Message[];
    stats: Record<string, number>;
  };
  social_network: SocialNetwork;
  knowledge: EntityKnowledge;
  social_intelligence: SocialIntelligence;
  communities: {
    entity_id: string;
    member_communities: Community[];
    total_communities: number;
  };
  trust_overview: TrustOverview;
}

export interface CommunicationEngineState {
  running: boolean;
  stats: {
    total_ticks: number;
    messages_generated: number;
    interactions_processed: number;
    communities_active: number;
  };
  tick_interval: number;
  messaging: {
    stats: Record<string, number>;
    message_types: string[];
    priority_levels: string[];
  };
  social_graph: {
    stats: Record<string, number>;
    relationship_types: string[];
  };
  trust: {
    stats: Record<string, number>;
    trust_change_reasons: string[];
  };
  knowledge: {
    stats: Record<string, number>;
    knowledge_types: string[];
    visibility_levels: string[];
  };
  communities: {
    stats: Record<string, number>;
    community_types: string[];
    industries: string[];
  };
  intelligence: {
    stats: Record<string, number>;
  };
}

export interface Market {
  id: string;
  name: string;
  market_type: string;
  description: string | null;
  current_price: number;
  base_price: number;
  supply: number;
  demand: number;
  volume: number;
  growth_rate: number;
  volatility: number;
  status: string;
  price_history: PriceHistory[];
  created_at: string;
  updated_at: string;
}

export interface PriceHistory {
  id: string;
  market_id: string;
  price: number;
  supply: number;
  demand: number;
  volume: number;
  change_pct: number;
  recorded_at: string;
}

export interface Investment {
  id: string;
  investor_id: string;
  investor_type: string;
  target_id: string;
  target_type: string;
  amount: number;
  expected_return_pct: number;
  actual_return: number;
  risk_level: string;
  status: string;
  invested_at: string;
}

export interface Loan {
  id: string;
  borrower_id: string;
  borrower_type: string;
  lender_id: string;
  amount: number;
  interest_rate: number;
  term_days: number;
  amount_paid: number;
  status: string;
  issued_at: string;
  due_at: string | null;
}

export interface EconomicIndicator {
  id: string;
  indicator_type: string;
  value: number;
  previous_value: number | null;
  change_pct: number;
  period: string;
  recorded_at: string;
}

export interface EconomicEvent {
  id: string;
  event_type: string;
  severity: string;
  title: string;
  description: string | null;
  affected_markets: string[];
  affected_sectors: string[];
  impact_magnitude: number;
  status: string;
  created_at: string;
}

export interface ResourceStatus {
  name: string;
  description: string;
  supply: number;
  demand: number;
  price: number;
  scarcity: string;
  ratio: number;
}

export interface WealthStats {
  total_wealth: number;
  average_wealth: number;
  median_wealth: number;
  gini_coefficient: number;
  top_10_pct_ownership: number;
  wealthiest_agent: { agent_id: string; balance: number } | null;
  poorest_agent: { agent_id: string; balance: number } | null;
}

export interface EconomyEngineState {
  running: boolean;
  stats: {
    total_ticks: number;
    economic_events: number;
    price_adjustments: number;
  };
  tick_interval: number;
  markets: {
    stats: { markets_created: number; price_updates: number; trades_executed: number };
    market_types: string[];
  };
  pricing: {
    stats: { calculations: number };
    factors: Record<string, number>;
  };
  resources: {
    resources: Record<string, ResourceStatus>;
    stats: { shortages: number; surpluses: number; price_adjustments: number };
  };
  finance: {
    base_interest_rate: number;
    savings_rate: number;
    inflation_rate: number;
    money_supply: number;
    stats: Record<string, number>;
  };
  investments: {
    stats: { investments_made: number; investments_matured: number; total_invested: number; total_returns: number };
  };
  events: {
    stats: Record<string, number>;
    event_types: string[];
  };
  wealth: {
    stats: WealthStats;
    history_length: number;
  };
  intelligence: {
    stats: Record<string, number>;
  };
}

export interface AgentEconomyState {
  active_investments: Investment[];
  matured_investments: Investment[];
  total_active_invested: number;
  total_matured_returns: number;
  investment_count: number;
}

export interface EconomicDashboard {
  markets: {
    total: number;
    active: number;
    avg_price: number;
    total_volume: number;
  };
  resources: Record<string, ResourceStatus>;
  finance: {
    bank_id: string;
    base_interest_rate: number;
    savings_rate: number;
    inflation_rate: number;
    money_supply: number;
    stats: Record<string, number>;
  };
  wealth: WealthStats;
  recent_events: EconomicEvent[];
  indicators: EconomicIndicator[];
}

export interface GovernanceEntity {
  id: string;
  name: string;
  entity_type: string;
  description: string | null;
  authority_level: string;
  founder_id: string | null;
  member_ids: string[];
  policy_ids: string[];
  law_ids: string[];
  resources: Record<string, unknown>;
  reputation: number;
  status: string;
  created_at: string;
}

export interface Law {
  id: string;
  name: string;
  description: string | null;
  creator_id: string;
  creator_type: string;
  scope: string;
  category: string;
  severity: string;
  affected_entities: string[];
  penalty: Record<string, unknown>;
  status: string;
  created_at: string;
}

export interface Policy {
  id: string;
  name: string;
  description: string | null;
  policy_type: string;
  creator_id: string;
  target: string | null;
  rules: Record<string, unknown>;
  expected_outcome: string | null;
  duration_days: number;
  priority: string;
  status: string;
  compliance_rate: number;
  created_at: string;
}

export interface Tax {
  id: string;
  name: string;
  tax_type: string;
  rate: number;
  target: string;
  description: string | null;
  revenue_total: number;
  revenue_use: string;
  status: string;
  created_at: string;
}

export interface Regulation {
  id: string;
  name: string;
  description: string | null;
  regulation_type: string;
  authority_id: string;
  target_sector: string | null;
  requirements: Record<string, unknown>;
  max_violations: number;
  penalty_description: string | null;
  status: string;
  created_at: string;
}

export interface Conflict {
  id: string;
  plaintiff_id: string;
  plaintiff_type: string;
  defendant_id: string;
  defendant_type: string;
  conflict_type: string;
  description: string | null;
  evidence: string[];
  resolution_method: string;
  resolution: string | null;
  ruling: string | null;
  penalty_amount: number;
  arbitrator_id: string | null;
  status: string;
  created_at: string;
  resolved_at: string | null;
}

export interface Vote {
  id: string;
  proposal_title: string;
  description: string | null;
  proposer_id: string;
  proposal_type: string;
  target_id: string | null;
  options: string[];
  voters: Record<string, string>;
  tally: Record<string, number>;
  total_eligible: number;
  quorum_pct: number;
  status: string;
  result: string | null;
  weight_factor: string;
  created_at: string;
}

export interface GovernanceRecord {
  id: string;
  record_type: string;
  title: string;
  description: string | null;
  actor_id: string;
  actor_type: string;
  entity_id: string | null;
  related_ids: string[];
  impact: Record<string, unknown>;
  created_at: string;
}

export interface GovernanceEngineState {
  running: boolean;
  stats: {
    total_ticks: number;
    actions_taken: number;
  };
  tick_interval: number;
  authority: {
    stats: { entities_created: number; authority_upgrades: number };
    authority_levels: string[];
    level_permissions: Record<string, number>;
  };
  laws: {
    stats: { laws_created: number; laws_enforced: number; violations_detected: number };
    categories: string[];
    severity_levels: string[];
  };
  policies: {
    stats: { policies_created: number; policies_expired: number };
    policy_types: string[];
  };
  taxation: {
    treasury_balance: number;
    stats: { taxes_created: number; taxes_collected: number; total_collected: number };
    tax_types: string[];
    revenue_uses: string[];
  };
  regulation: {
    stats: { regulations_created: number; violations_detected: number; penalties_applied: number };
    regulation_types: string[];
    active_violations: number;
  };
  conflicts: {
    stats: { conflicts_created: number; conflicts_resolved: number; negotiations_successful: number; arbitrations_completed: number };
    conflict_types: string[];
  };
  voting: {
    stats: { votes_started: number; votes_cast: number; votes_resolved: number };
    proposal_types: string[];
    weight_factors: string[];
  };
  intelligence: {
    stats: Record<string, number>;
  };
}

export interface CivilizationDashboard {
  stats: {
    total_entities: number;
    total_laws: number;
    total_policies: number;
    total_taxes: number;
    total_regulations: number;
    total_conflicts: number;
    total_votes: number;
    total_tax_revenue: number;
  };
  entities: {
    total: number;
    by_type: Record<string, number>;
    by_authority: Record<string, number>;
  };
  laws: {
    total: number;
    by_category: Record<string, number>;
    by_severity: Record<string, number>;
  };
  policies: {
    total: number;
    by_type: Record<string, number>;
  };
  conflicts: {
    open: number;
    types: Record<string, number>;
  };
  votes: {
    open: number;
  };
  taxation: {
    treasury_balance: number;
    active_taxes: Tax[];
    stats: Record<string, number>;
  };
}

export interface AgentGovernanceState {
  conflicts: Conflict[];
  is_in_conflict: boolean;
}

// ── Evolution Types ──────────────────────────────────────────────────

export interface Lineage {
  id: string;
  name: string;
  founder_agent_id: string;
  parent_lineage_id: string | null;
  generation_count: number;
  member_count: number;
  average_reputation: number;
  average_skill_level: number;
  total_contributions: number;
  achievements: string[];
  major_events: string[];
  trait_profile: Record<string, number>;
  status: string;
  created_at: string;
}

export interface Generation {
  id: string;
  generation_number: number;
  lineage_id: string | null;
  citizen_count: number;
  average_reputation: number;
  average_skill_level: number;
  innovation_index: number;
  knowledge_growth: number;
  dominant_traits: Record<string, number>;
  dominant_skills: string[];
  status: string;
  created_at: string;
}

export interface Mentorship {
  id: string;
  mentor_id: string;
  mentee_id: string;
  mentor_lineage_id: string | null;
  mentee_lineage_id: string | null;
  knowledge_transferred: Record<string, number>;
  skills_improved: string[];
  sessions_completed: number;
  quality_score: number;
  duration_days: number;
  status: string;
  started_at: string;
}

export interface Innovation {
  id: string;
  discoverer_id: string;
  lineage_id: string | null;
  innovation_type: string;
  title: string;
  description: string | null;
  knowledge_domain: string | null;
  impact_score: number;
  innovation_potential: number;
  status: string;
  discovered_at: string;
}

export interface CivilizationMetric {
  id: string;
  metric_type: string;
  value: number;
  previous_value: number | null;
  change_pct: number;
  recorded_at: string;
}

export interface EvolutionEngineState {
  running: boolean;
  generation: number;
  tick_interval: number;
  stats: {
    total_ticks: number;
    civ_evolutions: number;
    population_growth: number;
    mentorships_formed: number;
    innovations_discovered: number;
  };
  population: {
    stats: {
      citizens_generated: number;
      citizens_archived: number;
      growth_requests: number;
      growth_denied: number;
    };
    current_population: number;
    limits: {
      max_population: number;
      min_population: number;
      growth_rate_cap: number;
      compute_budget_per_agent: number;
    };
  };
  lineages: {
    stats: {
      lineages_created: number;
      lineages_merged: number;
    };
  };
  traits: {
    stats: {
      mutations_occurred: number;
      selections_applied: number;
      traits_optimized: number;
    };
    trait_definitions: Record<string, {
      name: string;
      category: string;
      inheritable: boolean;
      mutation_rate: number;
      natural_selection_weight: number;
    }>;
  };
  skills: {
    stats: {
      skills_inherited: number;
      skills_mixed: number;
      skills_enhanced: number;
    };
    total_synergies: number;
  };
  mentorship: {
    stats: {
      mentorships_created: number;
      sessions_completed: number;
      mentorships_graduated: number;
    };
  };
  civilization: {
    level: number;
    generation: number;
    metrics: Record<string, number>;
    stats: {
      total_innovations: number;
      total_events: number;
      level_changes: number;
      adaptations_applied: number;
    };
  };
  innovation: {
    stats: {
      innovations_discovered: number;
      innovations_performed: number;
      breakthroughs: number;
    };
    types: string[];
  };
}

export interface CivilizationStatus {
  level: number;
  generation: number;
  total_score: number;
  average_score: number;
  axes: Record<string, number>;
  axis_definitions: Record<string, string>;
  stats: {
    total_innovations: number;
    total_events: number;
    level_changes: number;
    adaptations_applied: number;
  };
}

export interface AgentEvolutionState {
  mentorships_as_mentor: number;
  mentorships_as_mentee: number;
  innovations_count: number;
  innovations: Innovation[];
}

// ── Research Types ───────────────────────────────────────────────────

export interface ResearchOrganization {
  id: string;
  name: string;
  org_type: string;
  description: string | null;
  founder_agent_id: string | null;
  research_budget: number;
  reputation: number;
  research_areas: string[];
  scientist_agent_ids: string[];
  total_projects: number;
  completed_projects: number;
  published_papers: number;
  citations_received: number;
  technologies_developed: string[];
  knowledge_nodes_created: number;
  status: string;
  created_at: string;
}

export interface ResearchProject {
  id: string;
  organization_id: string | null;
  lead_agent_id: string | null;
  title: string;
  research_question: string;
  hypothesis: string | null;
  objectives: string[];
  required_skills: string[];
  budget: number;
  budget_spent: number;
  timeline_days: number;
  days_elapsed: number;
  status: string;
  priority: string;
  dependencies: string[];
  expected_impact: number;
  actual_impact: number;
  progress: number;
  team_agent_ids: string[];
  knowledge_domain: string | null;
  funding_source: string | null;
  created_at: string;
}

export interface Experiment {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  methodology: string | null;
  hypothesis: string | null;
  variables: Record<string, unknown>;
  status: string;
  outcome: string | null;
  outcome_details: string | null;
  confidence_score: number;
  time_spent: number;
  budget_consumed: number;
  compute_consumed: number;
  knowledge_produced: Array<{ name: string; type: string; confidence: number }>;
  unexpected_findings: Array<{ finding: string; significance: number }>;
  created_at: string;
}

export interface KnowledgeNode {
  id: string;
  name: string;
  node_type: string;
  description: string | null;
  domain: string | null;
  maturity_level: number;
  confidence: number;
  novelty_score: number;
  utility_score: number;
  citations: number;
  usage_count: number;
  keywords: string[];
  status: string;
  created_at: string;
}

export interface KnowledgeEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  edge_type: string;
  weight: number;
  description: string | null;
  confidence: number;
  created_by_agent_id: string | null;
  created_at: string;
}

export interface KnowledgeGraphSummary {
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
  domain_distribution: Record<string, number>;
  edge_types: Record<string, number>;
  cross_domain_connections: number;
}

export interface Publication {
  id: string;
  title: string;
  abstract: string | null;
  authors: string[];
  institution: string | null;
  knowledge_domain: string | null;
  keywords: string[];
  impact_score: number;
  citations: number;
  quality_score: number;
  novelty_score: number;
  status: string;
  peer_review_status: string;
  open_access: boolean;
  created_at: string;
}

export interface PeerReview {
  id: string;
  publication_id: string;
  reviewer_agent_id: string;
  institution: string | null;
  decision: string;
  overall_score: number;
  comments: string | null;
  created_at: string;
}

export interface Technology {
  id: string;
  name: string;
  description: string | null;
  tech_type: string;
  domain: string | null;
  difficulty_level: number;
  prerequisites: string[];
  benefits: string[];
  development_cost: number;
  research_points_needed: number;
  research_points_earned: number;
  adoption_count: number;
  maturity: number;
  inventors: string[];
  organization_id: string | null;
  status: string;
  created_at: string;
}

export interface ResearchInnovation {
  id: string;
  title: string;
  description: string | null;
  innovation_type: string;
  domain: string | null;
  novelty_score: number;
  impact_score: number;
  feasibility_score: number;
  discoverer_agent_id: string | null;
  organization_id: string | null;
  status: string;
  created_at: string;
}

export interface ResearchFunding {
  id: string;
  project_id: string;
  funder_organization: string | null;
  funding_source_type: string;
  amount: number;
  disbursed: number;
  status: string;
  proposal_score: number;
  created_at: string;
}

export interface Conference {
  id: string;
  name: string;
  description: string | null;
  domain: string | null;
  conference_type: string;
  attendee_count: number;
  paper_count: number;
  status: string;
  created_at: string;
}

export interface ResearchEngineState {
  running: boolean;
  tick_interval: number;
  stats: {
    total_ticks: number;
    auto_projects: number;
    auto_experiments: number;
    auto_publications: number;
    tech_contributions: number;
  };
  organizations: { stats: Record<string, number> };
  projects: { stats: Record<string, number> };
  knowledge_graph: { stats: Record<string, number> };
  experiments: { stats: Record<string, number> };
  publications: { stats: Record<string, number> };
  peer_review: { stats: Record<string, number> };
  technology: { stats: Record<string, number> };
  diffusion: { stats: Record<string, number> };
  funding: { stats: Record<string, number> };
  innovation: { stats: Record<string, number> };
  intelligence: { stats: Record<string, number> };
}

export interface ResearchDashboard {
  stats: {
    organizations: number;
    projects: number;
    experiments: number;
    publications: number;
    technologies: number;
    knowledge_nodes: number;
  };
  active_projects: number;
  completed_projects: number;
  unlocked_technologies: number;
  published_papers: number;
  knowledge_nodes: number;
  domain_distribution: Record<string, number>;
  top_organizations: Array<{ name: string; reputation: number; papers: number }>;
  recent_projects: ResearchProject[];
  recent_innovations: Publication[];
}

export interface AgentResearchState {
  projects_led: number;
  publications: number;
  innovations: number;
  recent_projects: ResearchProject[];
}

// ── World Types ──────────────────────────────────────────────────────

export interface WorldZone {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  label: string;
}

export interface WorldRoad {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
}

export interface WorldBuilding {
  id: string;
  type: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  capacity: number;
  color: string;
  zone: string;
  employee_count: number;
  visitor_count: number;
  activity: string;
}

export interface WorldMapState {
  width: number;
  height: number;
  tile_size: number;
  zones: WorldZone[];
  roads: WorldRoad[];
  buildings: WorldBuilding[];
}

export interface WorldTimeState {
  day: number;
  hour: number;
  minute: number;
  speed: number;
  paused: boolean;
  total_ticks: number;
}

export interface WorldCitizen {
  agent_id: string;
  x: number;
  y: number;
  destination: string | null;
  status: string;
  building_id: string | null;
  thought: string | null;
}

export interface WorldEvent {
  type: string;
  description: string;
  x: number;
  y: number;
  entities: string[];
  timestamp: number;
}

export interface WorldFullState {
  map: WorldMapState;
  time: WorldTimeState;
  citizen_count: number;
  event_count: number;
}

export interface PopulationOverlayCell {
  cell: string;
  count: number;
}

export interface EconomicOverlayZone extends WorldZone {
  building_count: number;
  activity_score: number;
}

// ── Federation Types ─────────────────────────────────────────────────

export interface Civilization {
  id: string;
  name: string;
  description: string | null;
  leader_agent_id: string | null;
  population: number;
  territory_size: number;
  technology_level: number;
  economic_power: number;
  military_strength: number;
  cultural_influence: number;
  research_output: number;
  happiness: number;
  resource_availability: string;
  government_type: string;
  economic_model: string;
  values: Record<string, number>;
  priorities: string[];
  achievements: string[];
  reputation: number;
  status: string;
  created_at: string;
}

export interface CivilizationRules {
  id: string;
  civilization_id: string;
  economic_model: string;
  governance_type: string;
  resource_availability: string;
  migration_policy: string;
  trade_policy: string;
  research_policy: string;
  defense_policy: string;
  custom_rules: Record<string, unknown>;
}

export interface DiplomaticRelation {
  id: string;
  civilization_a_id: string;
  civilization_b_id: string;
  relation_level: number;
  status: string;
  trust_score: number;
  trade_volume: number;
  agreements_count: number;
  conflicts_count: number;
  created_at: string;
}

export interface TradeAgreement {
  id: string;
  civilization_a_id: string;
  civilization_b_id: string;
  trade_type: string;
  resource_offered: string;
  resource_requested: string;
  amount_offered: number;
  amount_requested: number;
  price: number;
  total_volume: number;
  status: string;
  created_at: string;
}

export interface FederationCouncil {
  id: string;
  name: string;
  description: string | null;
  member_civilization_ids: string[];
  founding_civilization_id: string | null;
  resolution_count: number;
  status: string;
  created_at: string;
}

export interface FederationMigration {
  id: string;
  agent_id: string;
  origin_civilization_id: string;
  destination_civilization_id: string;
  reason: string;
  skill_value: number;
  status: string;
  migrated_at: string;
}

export interface CivilizationHistory {
  id: string;
  event_type: string;
  title: string;
  description: string | null;
  impact_score: number;
  recorded_at: string;
}

export interface FederationDashboard {
  civilization_count: number;
  total_population: number;
  average_technology: number;
  average_economy: number;
  average_happiness: number;
  federation_stats: {
    civilizations: number;
    diplomatic_relations: number;
    trade_agreements: number;
    federation_councils: number;
    migrations: number;
  };
  rankings: {
    technology: Array<{ name: string; value: number }>;
    economic: Array<{ name: string; value: number }>;
    population: Array<{ name: string; value: number }>;
  };
  civilizations: Civilization[];
}

export interface FederationEngineState {
  running: boolean;
  tick_interval: number;
  stats: {
    total_ticks: number;
    auto_diplomacy: number;
    auto_trade: number;
    auto_migrations: number;
    auto_competitions: number;
  };
}

export interface DiplomacyMap {
  nodes: Array<{ id: string; name: string; population: number; technology_level: number }>;
  edges: Array<{ source: string; target: string; status: string; trust: number }>;
}

// ── Culture Types ─────────────────────────────────────────────────

export interface CulturalIdentity {
  id: string;
  civilization_id: string;
  name: string;
  core_values: Record<string, number>;
  shared_history: Array<{ event: string; impact: number }>;
  social_norms: string[];
  historical_symbols: string[];
  long_term_goals: string[];
  identity_strength: number;
  created_at: string;
}

export interface ValueSystem {
  id: string;
  civilization_id: string;
  innovation: number;
  cooperation: number;
  competition: number;
  education: number;
  efficiency: number;
  sustainability: number;
  exploration: number;
  security: number;
  transparency: number;
  created_at: string;
}

export interface Institution {
  id: string;
  civilization_id: string;
  name: string;
  institution_type: string;
  description: string | null;
  strength: number;
  influence: number;
  membership_count: number;
  active: boolean;
  created_at: string;
}

export interface Tradition {
  id: string;
  civilization_id: string;
  name: string;
  description: string | null;
  frequency: string;
  impact_score: number;
  last_held: string | null;
  next_held: string | null;
  created_at: string;
}

export interface CivilizationCommunity {
  id: string;
  civilization_id: string;
  name: string;
  description: string | null;
  community_type: string;
  member_count: number;
  growth_rate: number;
  created_at: string;
}

export interface CollectiveMemory {
  id: string;
  civilization_id: string;
  event_type: string;
  title: string;
  description: string | null;
  impact_score: number;
  recorded_at: string;
}

export interface SocialDynamics {
  id: string;
  civilization_id: string;
  collaboration_score: number;
  competition_score: number;
  trust_level: number;
  influence_distribution: Record<string, number>;
  knowledge_sharing_score: number;
  community_growth_rate: number;
}

export interface ReputationEntry {
  id: string;
  civilization_id: string;
  entity_id: string;
  entity_type: string;
  influence_score: number;
  contribution_count: number;
  sustained_engagement: number;
}

export interface CulturalTimelineEvent {
  id: string;
  civilization_id: string;
  change_type: string;
  description: string | null;
  cause: string | null;
  impact_score: number;
  recorded_at: string;
}

export interface CivilizationIdentityScore {
  id: string;
  civilization_id: string;
  knowledge_orientation: number;
  innovation_orientation: number;
  economic_stability: number;
  social_cohesion: number;
  institutional_strength: number;
  adaptability: number;
  last_calculated: string;
}

export interface CultureEngineState {
  running: boolean;
  tick_interval: number;
  stats: {
    total_ticks: number;
    value_shifts: number;
    traditions_held: number;
    norms_emerged: number;
    institutions_founded: number;
    communities_grew: number;
    memories_recorded: number;
    identity_scores_calculated: number;
  };
}

export interface CultureStats {
  cultural_identities: number;
  institutions: number;
  traditions: number;
  communities: number;
  collective_memories: number;
  timeline_events: number;
}

// ── Technology Evolution Types ─────────────────────────────────────

export interface TechNode {
  id: string;
  name: string;
  domain: string;
  description: string | null;
  tech_type: string;
  origin_civilization_id: string | null;
  discovery_date: string | null;
  required_knowledge: string[];
  required_resources: Record<string, number>;
  difficulty_level: number;
  impact_score: number;
  current_level: number;
  applications: string[];
  prerequisites: string[];
  maturity: number;
  adoption_count: number;
  status: string;
  created_at: string;
}

export interface TechEdge {
  id: string;
  source_technology_id: string;
  target_technology_id: string;
  edge_type: string;
  weight: number;
  description: string | null;
  created_at: string;
}

export interface TechDiscovery {
  id: string;
  civilization_id: string;
  technology_id: string;
  title: string;
  description: string | null;
  difficulty: string;
  impact_score: number;
  discoverer_agent_id: string | null;
  method: string;
  confidence: number;
  status: string;
  discovered_at: string;
}

export interface TechDevelopment {
  id: string;
  technology_id: string;
  civilization_id: string;
  stage: string;
  progress: number;
  resource_cost: number;
  time_spent: number;
  lead_agent_id: string | null;
  team_agent_ids: string[];
  notes: string | null;
  status: string;
  created_at: string;
}

export interface TechAdoption {
  id: string;
  civilization_id: string;
  technology_id: string;
  decision: string;
  economic_benefit: number;
  cost: number;
  risk: number;
  cultural_compatibility: number;
  strategic_importance: number;
  decided_at: string;
}

export interface ScientificOrg {
  id: string;
  civilization_id: string;
  name: string;
  org_type: string;
  description: string | null;
  research_output: number;
  discoveries_count: number;
  scientist_count: number;
  funding_level: number;
  reputation: number;
  specialization: string[];
  active: boolean;
  created_at: string;
}

export interface ScientistEntry {
  id: string;
  civilization_id: string;
  agent_id: string | null;
  name: string;
  specialization: string;
  organization_id: string | null;
  research_output: number;
  discoveries_count: number;
  publications_count: number;
  influence_score: number;
  status: string;
  created_at: string;
}

export interface CivilizationTechLevel {
  id: string;
  civilization_id: string;
  computational_capability: number;
  energy_capability: number;
  manufacturing_capability: number;
  scientific_knowledge: number;
  automation_level: number;
  infrastructure_level: number;
  current_era: string;
  last_calculated: string;
}

export interface TechTimelineEvent {
  id: string;
  civilization_id: string;
  event_type: string;
  technology_id: string | null;
  title: string;
  description: string | null;
  impact_score: number;
  recorded_at: string;
}

export interface TechnologyEngineState {
  running: boolean;
  tick_interval: number;
  stats: {
    total_ticks: number;
    discoveries: number;
    developments_advanced: number;
    adoptions: number;
    obsoleted: number;
    competitions: number;
  };
}

export interface TechStats {
  technologies: number;
  technology_edges: number;
  discoveries: number;
  scientific_organizations: number;
  scientists: number;
}

// ── Planetary & Environmental Types ────────────────────────────────

export interface PlanetData {
  id: string;
  name: string;
  radius: number;
  seed: number;
  region_count: number;
  total_population: number;
  average_temperature: number;
  average_rainfall: number;
  resource_richness: number;
  environmental_health: number;
  age_years: number;
  status: string;
  created_at: string;
}

export interface PlanetRegion {
  id: string;
  planet_id: string;
  name: string;
  terrain_type: string;
  climate_zone: string;
  pos_x: number;
  pos_y: number;
  area: number;
  elevation: number;
  water_nearby: boolean;
  fertile: boolean;
  habitability: number;
  population: number;
  developed: boolean;
  created_at: string;
}

export interface ClimateRecord {
  id: string;
  planet_id: string;
  region_id: string | null;
  temperature: number;
  rainfall: number;
  seasonality: number;
  drought_risk: number;
  storm_risk: number;
  growing_season_days: number;
  climate_type: string;
  recorded_at: string;
}

export interface NaturalResource {
  id: string;
  planet_id: string;
  region_id: string | null;
  resource_type: string;
  name: string;
  quantity: number;
  max_quantity: number;
  extraction_rate: number;
  regeneration_rate: number;
  market_value: number;
  renewable: boolean;
  quality: number;
  discovered: boolean;
  status: string;
  created_at: string;
}

export interface PlanetInfrastructure {
  id: string;
  planet_id: string;
  region_id: string;
  civilization_id: string;
  infra_type: string;
  name: string | null;
  level: number;
  efficiency: number;
  condition: number;
  capacity: number;
  cost: number;
  status: string;
  built_at: string;
}

export interface SettlementData {
  id: string;
  planet_id: string;
  region_id: string;
  civilization_id: string;
  name: string;
  population: number;
  economic_output: number;
  infrastructure_level: number;
  research_capacity: number;
  quality_of_life: number;
  education_level: number;
  expansion_rate: number;
  status: string;
  founded_at: string;
}

export interface EnvironmentalEventData {
  id: string;
  planet_id: string;
  event_type: string;
  region_id: string | null;
  title: string;
  description: string | null;
  severity: number;
  duration_days: number;
  affected_population: number;
  resource_damage: number;
  infrastructure_damage: number;
  status: string;
  triggered_at: string;
}

export interface SustainabilityData {
  id: string;
  civilization_id: string;
  resource_consumption_rate: number;
  renewable_usage_pct: number;
  infrastructure_efficiency: number;
  environmental_health: number;
  carbon_footprint: number;
  restoration_effort: number;
  sustainability_score: number;
  recorded_at: string;
}

export interface PlanetaryEngineState {
  running: boolean;
  tick_interval: number;
  stats: {
    total_ticks: number;
    settlements_grew: number;
    resources_regenerated: number;
    events_triggered: number;
    climate_evolutions: number;
    infrastructure_ticks: number;
    sustainability_calcs: number;
  };
}

export interface PlanetaryStats {
  planets: number;
  regions: number;
  resources: number;
  settlements: number;
  infrastructure: number;
  environmental_events: number;
}

export interface TemporalClockState {
  clock_id: string;
  tick_count: number;
  year: number;
  day: number;
  hour: number;
  time_scale: number;
  paused: boolean;
  running: boolean;
  century: number;
  time_string: string;
}

export interface TemporalEvent {
  id: string;
  event_type: string;
  title: string;
  description?: string;
  location?: string;
  participants?: string;
  cause?: string;
  outcome?: string;
  impact_score: number;
  tick: number;
  year?: number;
}

export interface TemporalSnapshot {
  id: string;
  tick: number;
  year: number;
  label: string;
  full_state?: Record<string, unknown>;
  created_at?: string;
}

export interface TemporalTimeline {
  id: string;
  name: string;
  description?: string;
  parent_timeline_id?: string;
  branch_point_tick?: number;
  branch_point_year?: number;
  divergence_cause?: string;
  event_count: number;
  status: string;
}

export interface TemporalBranchTree {
  trunk: {
    id: string | null;
    name: string;
    event_count: number;
    children: TemporalBranchTree[];
  };
  branches: TemporalTimeline[];
}

export interface TemporalCausalEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  strength: number;
  description?: string;
}

export interface TemporalCausalChain {
  root: string;
  nodes: string[];
  edges: TemporalCausalEdge[];
  depth: number;
}

export interface TemporalAnalytics {
  summary: {
    total_events: number;
    years_span: number;
    events_per_year: number;
    first_event: { title: string; year: number };
    last_event: { title: string; year: number };
    unique_locations: number;
    unique_participants: number;
    average_impact_score: number;
  };
  event_distribution: {
    distribution: { type: string; count: number }[];
    total_events: number;
  };
  milestones: {
    milestones: TemporalEvent[];
    count: number;
  };
}

export interface TemporalReplayState {
  replaying: boolean;
  speed: number;
  position: number;
  start_tick: number;
  end_tick: number;
  progress: number;
}

export interface TemporalEngineState {
  clock: TemporalClockState;
  events: { total: number };
  snapshots: { last_snapshot_tick: number; snapshot_interval: number };
  replay: TemporalReplayState;
  timeline: { active_branch: string | null };
  branches: TemporalTimeline[];
  causality: { pending_edges: number };
  initialized: boolean;
  running: boolean;
}

export interface MetaObservation {
  id: string;
  tick: number;
  year: number;
  population: number;
  economy_gdp: number;
  research_level: number;
  technology_level: number;
  education_index: number;
  governance_stability: number;
  environment_health: number;
  innovation_rate: number;
  social_stability: number;
  resource_scarcity: number;
  event_count: number;
}

export interface MetaTrend {
  tick: number;
  year: number;
  value: number;
}

export interface MetaComparisonResult {
  id: string;
  metric: string;
  value_a: number;
  value_b: number;
  difference: number;
  percent_change: number;
  summary: string;
}

export interface MetaDiscoveredPattern {
  id: string;
  type: string;
  title: string;
  description: string;
  antecedent: string;
  consequent: string;
  confidence: number;
  support: number;
  lift: number;
  sample_size: number;
  tags: string;
  status: string;
}

export interface MetaRuleEvaluation {
  id: string;
  rule_name: string;
  domain: string;
  description: string;
  effectiveness: number;
  stability: number;
  side_effects: string;
  report: string;
  confidence: number;
}

export interface MetaExperiment {
  id: string;
  name: string;
  description: string;
  type: string;
  variable_name: string;
  variable_change: string;
  duration_ticks: number;
  status: string;
  result_summary: string;
  created_at: string;
}

export interface MetaRecommendation {
  id: string;
  title: string;
  description: string;
  type: string;
  domain: string;
  suggested_change: string;
  expected_impact: string;
  confidence: number;
  evidence: string;
  supporting_simulations: string;
  limitations: string;
  status: string;
}

export interface MetaKnowledgeEntry {
  id: string;
  title: string;
  content: string;
  type: string;
  source: string;
  tags: string;
  confidence: number;
  created_at: string;
}

export interface MetaReport {
  id: string;
  title: string;
  type: string;
  content: string;
  simulation_ids: string;
  generated_at: string;
}

export interface MetaEngineState {
  initialized: boolean;
  running: boolean;
  observations: number;
  patterns: number;
  recommendations: { total: number; pending: number; accepted: number; rejected: number; average_confidence: number };
  knowledge: { total_entries: number; total_reports: number; entry_types: Record<string, number> };
}

export interface PlatformPlugin {
  id: string;
  name: string;
  display_name: string;
  description: string;
  author: string;
  version: string;
  type: string;
  target: string;
  enabled: boolean;
  dependencies: { name: string; min_version: string; optional: boolean }[];
}

export interface PlatformTemplate {
  id: string;
  name: string;
  description: string;
  type: string;
  difficulty: string;
  objectives: string;
}

export interface PlatformScenario {
  id: string;
  name: string;
  description: string;
  template_id: string;
  author_id: string;
  is_public: boolean;
  tags: string;
  created_at: string;
}

export interface PlatformModule {
  id: string;
  name: string;
  display_name: string;
  description: string;
  author: string;
  version: string;
  category: string;
  license: string;
  downloads: number;
  rating: number;
  compatibility: string;
}

export interface PlatformWorkspace {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  status: string;
  tags: string;
  created_at: string;
}

export interface PlatformDataset {
  id: string;
  name: string;
  type: string;
  format: string;
  records: number;
  size_bytes: number;
  exported_at: string;
}

export interface PlatformDeveloperTool {
  id: string;
  name: string;
  description: string;
  type: string;
  endpoint: string;
  enabled: boolean;
}

export interface PlatformEngineState {
  initialized: boolean;
  plugins: { total: number; enabled: number; disabled: number; types: Record<string, number> };
  marketplace: { total: number; categories: Record<string, number>; average_rating: number; total_downloads: number };
  templates: number;
  scenarios: number;
  tools: number;
}

export interface VirtualRegion {
  id: string;
  x: number;
  z: number;
  biome: string;
  terrain: string;
  buildings: VirtualBuildingData[];
  entities: VirtualEntityData[];
}

export interface VirtualBuildingData {
  id: string;
  type: string;
  label: string;
  x: number;
  y: number;
  z: number;
  w: number;
  h: number;
  d: number;
  color: string;
  style: string;
  occupants: number;
}

export interface VirtualEntityData {
  id: string;
  name: string;
  type: string;
  x: number;
  y: number;
  z: number;
  target_x: number;
  target_z: number;
  activity: string;
  speed: number;
}

export interface CameraState {
  id?: string;
  name: string;
  x: number;
  y: number;
  z: number;
  mode: string;
}

export interface CinematicEventData {
  id: string;
  type: string;
  title: string;
  description: string;
  camera: { x: number; y: number; z: number };
  target: { x: number; y: number; z: number };
  duration: number;
  priority: number;
}

export interface RealityEngineState {
    initialized: boolean;
    regions: number;
    buildings: number;
    entities: number;
    cinematic: { pending: number; triggered: number; total: number };
}

// ── Management / Admin Types ──────────────────────────────────────────

export interface ManagementState {
    initialized: boolean;
    health: {
        overall_status: string;
        health_score: number;
        metrics: Record<string, { value: number; status: string }>;
        degraded_metrics: string[];
        total_metrics: number;
    };
}

export interface HealthMetric {
    name: string;
    value: number;
    status: string;
}

export interface AnomalyAlertData {
    id: string;
    type: string;
    severity: string;
    title: string;
    description: string;
    affected_system: string;
    cause: string;
    suggested_action: string;
    resolved: boolean;
    detected_at: string;
}

export interface PerformanceData {
    tick: number;
    agents: number;
    active: number;
    avg_tick_ms: number;
    memory_mb: number;
    cache_hit: number;
    time: string;
}

export interface OptimizationData {
    id: string;
    type: string;
    target: string;
    description: string;
    impact: string;
    status: string;
}

export interface IntegrityCheck {
    check: string;
    status: string;
    message: string;
}

export interface RecoveryEntry {
    id: string;
    type: string;
    target: string;
    cause: string;
    success: boolean;
    time: string;
}

export interface AdminLogEntry {
    id: string;
    type: string;
    severity: string;
    message: string;
    time: string;
}

export interface ControlStatus {
    status: string;
    controls: string[];
    restrictions: string[];
}

export interface SimulationAnalysis {
    overview: string;
    health: ManagementState["health"];
    recommendations: string[];
}

export interface EventExplanation {
    title: string;
    factors: Array<{ factor: string; weight: string; description: string }>;
    timeline?: Array<{ year: number; event: string }>;
    recommendation?: string;
    confidence: number;
}

// ── Genesis / Creator Mythology Types ──────────────────────────────────

export interface GenesisCivilization {
    id: string;
    name: string;
    population: number;
    era: string;
    creation_year: number;
    current_year: number;
    technology_level: number;
    culture_level: number;
    scientific_level: number;
    awareness_level: number;
    has_discovered_simulation: boolean;
    origin_story: string;
    status: string;
    created_at: string;
}

export interface GenesisAgent {
    id: string;
    civilization_id: string;
    name: string;
    role: string;
    status: string;
    intelligence_level: number;
    survival_skill: number;
    learning_rate: number;
    social_influence: number;
    knowledge_areas: string[];
    energy: number;
    discovery_count: number;
    created_at: string;
}

export interface BeliefSystem {
    id: string;
    civilization_id: string;
    name: string;
    belief_type: string;
    origin_explanation: string;
    natural_event_explanations: Record<string, string>;
    creator_concept: string;
    core_tenets: string[];
    rituals: string[];
    followers_count: number;
    influence_level: number;
    status: string;
    created_at: string;
}

export interface PhilosophyData {
    id: string;
    civilization_id: string;
    name: string;
    philosopher_agent_id: string | null;
    school_of_thought: string;
    core_ideas: string[];
    influence: number;
    followers: number;
    status: string;
    created_at: string;
}

export interface CreatorInteractionData {
    id: string;
    civilization_id: string;
    interaction_type: string;
    description: string;
    civilization_interpretation: string;
    impact_level: number;
    belief_impact: Record<string, unknown>;
    triggered_by_creator: boolean;
    created_at: string;
}

export interface HistoricalInterpretationData {
    id: string;
    civilization_id: string;
    event_type: string;
    actual_event: string;
    civilization_interpretation: string;
    impact_on_beliefs: Record<string, unknown>;
    recorded_by_agent_id: string | null;
    created_at: string;
}

export interface GenesisDiscovery {
    id: string;
    civilization_id: string;
    discovery_type: string;
    title: string;
    description: string;
    discoverer_agent_id: string | null;
    impact_level: number;
    era_recorded: string;
    created_at: string;
}

export interface EraRecord {
    id: string;
    civilization_id: string;
    era_name: string;
    start_year: number;
    end_year: number | null;
    key_events: string[];
    population_at_start: number;
    technology_level: number;
    culture_level: number;
    created_at: string;
}

export interface KnowledgeDomain {
    id: string;
    civilization_id: string;
    domain_name: string;
    level: number;
    understanding: string;
    discoveries_made: number;
    created_at: string;
}

export interface AwarenessRecord {
    id: string;
    civilization_id: string;
    awareness_level: number;
    understanding_description: string;
    evidence_collected: string[];
    philosopher_responsible: string;
    recorded_at: string;
}

export interface AwarenessStatus {
    level: number;
    label: string;
    description: string;
    has_discovered_simulation: boolean;
    records: AwarenessRecord[];
}

export interface GenesisCivilizationProfile {
    civilization: GenesisCivilization;
    agents: GenesisAgent[];
    beliefs: BeliefSystem[];
    philosophies: PhilosophyData[];
    discoveries: GenesisDiscovery[];
    eras: EraRecord[];
    knowledge_domains: KnowledgeDomain[];
    awareness: AwarenessStatus;
}

export interface GenesisEngineState {
    initialized: boolean;
    running: boolean;
    civilizations: Record<string, GenesisCivilizationProfile>;
}

// ── Compute Network Types ──────────────────────────────────────────────

export interface ComputeNode {
    id: string;
    name: string;
    node_type: string;
    status: string;
    host: string;
    port: number;
    cpu_cores: number;
    cpu_usage: number;
    gpu_count: number;
    gpu_usage: number;
    memory_total_mb: number;
    memory_used_mb: number;
    network_latency_ms: number;
    active_tasks: number;
    max_tasks: number;
    uptime_seconds: number;
    capabilities: ComputeCapability[];
    last_heartbeat: string | null;
    created_at: string;
}

export interface ComputeCapability {
    id: string;
    node_id: string;
    capability_type: string;
    description: string;
    performance_score: number;
}

export interface ComputePartition {
    id: string;
    node_id: string;
    partition_key: string;
    partition_type: string;
    universe_id: string;
    status: string;
    agent_count: number;
    workload_score: number;
}

export interface ComputeTask {
    id: string;
    node_id: string;
    task_type: string;
    description: string;
    priority: string;
    status: string;
    source: string;
    payload: Record<string, unknown>;
    result: string | null;
    progress: number;
    estimated_cost: number;
    started_at: string | null;
    completed_at: string | null;
    created_at: string;
}

export interface ComputeTaskStats {
    total: number;
    pending: number;
    running: number;
    completed: number;
    failed: number;
}

export interface ComputeReasoningStats {
    total_reasoning_tasks: number;
    active_reasoning: number;
    completed_reasoning: number;
    gpu_nodes_available: number;
}

export interface ComputeSyncStats {
    total_syncs: number;
    completed_syncs: number;
    total_data_bytes: number;
    total_duration_ms: number;
}

export interface ComputeStorageInfo {
    total_bytes: number;
    used_bytes: number;
    available_bytes: number;
    usage_pct: number;
    nodes_with_storage: number;
}

export interface ComputeFaultStats {
    total_faults: number;
    recovered: number;
    unresolved: number;
    by_severity: Record<string, number>;
}

export interface ComputeClock {
    id: string;
    clock_name: string;
    tick_count: number;
    time_scale: number;
    paused: boolean;
    last_sync_at: string | null;
}

export interface ComputeBalanceStatus {
    loads: Array<{ node_id: string; name: string; load: number }>;
    average_load: number;
    high_load_nodes: Array<{ node_id: string; name: string; load: number }>;
    total_nodes: number;
}

export interface ComputeEngineState {
    initialized: boolean;
    running: boolean;
    nodes: {
        total: number;
        online: number;
        active_tasks: number;
        list: ComputeNode[];
    };
    partitions: {
        total: number;
        assigned: number;
        unassigned: number;
        by_type: Record<string, number>;
    };
    tasks: ComputeTaskStats;
    reasoning: ComputeReasoningStats;
    sync: ComputeSyncStats;
    storage: ComputeStorageInfo;
    faults: ComputeFaultStats;
    clock: ComputeClock;
    balance: ComputeBalanceStatus;
}

export interface ScientificExperiment {
    id: string;
    title: string;
    research_question: string | null;
    hypothesis: string | null;
    variables: Record<string, unknown>;
    constraints: Record<string, unknown>;
    simulation_params: Record<string, unknown>;
    duration_ticks: number;
    status: string;
    result_summary: Record<string, unknown> | null;
    confidence_score: number;
    created_by: string | null;
    laboratory_type: string;
    tags: string[];
    started_at: string | null;
    completed_at: string | null;
    created_at: string;
}

export interface DiscoveredPattern {
    id: string;
    pattern_type: string;
    title: string;
    description: string | null;
    antecedent: string | null;
    consequent: string | null;
    confidence: number;
    support: number;
    lift: number;
    sample_size: number;
    method: string;
    tags: string[];
    status: string;
    created_at: string;
}

export interface Hypothesis {
    id: string;
    title: string;
    description: string | null;
    phenomenon: string | null;
    proposed_explanation: string | null;
    supporting_evidence: string[];
    counterexamples: string[];
    confidence_level: number;
    status: string;
    domain: string;
    created_by: string | null;
    created_at: string;
}

export interface ResearchLaboratory {
    id: string;
    name: string;
    lab_type: string;
    description: string | null;
    specialization: string[];
    experiment_count: number;
    active: boolean;
    created_at: string;
}

export interface ResearchReport {
    id: string;
    title: string;
    research_question: string | null;
    methodology: string | null;
    simulation_setup: string | null;
    results: string | null;
    limitations: string | null;
    future_experiments: string | null;
    confidence_score: number;
    status: string;
    created_by_agent_id: string | null;
    created_at: string;
}

export interface ScienceKnowledgeNode {
    id: string;
    node_type: string;
    name: string;
    description: string | null;
    data: Record<string, unknown>;
    importance: number;
    created_at: string;
}

export interface ScienceKnowledgeEdge {
    id: string;
    source_node_id: string;
    target_node_id: string;
    edge_type: string;
    weight: number;
    description: string | null;
    created_at: string;
}

export interface ScienceKnowledgeGraph {
    nodes: ScienceKnowledgeNode[];
    edges: ScienceKnowledgeEdge[];
    node_count: number;
    edge_count: number;
}

export interface DiscoveryArchiveEntry {
    id: string;
    archive_type: string;
    title: string;
    content: string | null;
    reference_id: string | null;
    success: boolean;
    tags: string[];
    created_at: string;
}

export interface DiscoveryEngineState {
    initialized: boolean;
    running: boolean;
    stats: {
        total_ticks: number;
        experiments_created: number;
        patterns_discovered: number;
        hypotheses_generated: number;
        reports_created: number;
        archives_stored: number;
    };
    db_stats: {
        experiments: number;
        patterns: number;
        hypotheses: number;
        reports: number;
        archives: number;
        laboratories: number;
        research_agents: number;
        snapshots: number;
    };
    events: string[];
}

export interface DiscoveryStats {
    experiments: number;
    patterns: number;
    hypotheses: number;
    reports: number;
    archives: number;
    laboratories: number;
    research_agents: number;
    snapshots: number;
}
