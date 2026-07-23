"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import {
  BrainCircuit,
  Eye,
  BarChart3,
  GitBranch,
  Lightbulb,
  FlaskConical,
  BookOpen,
  FileText,
  Search,
  TrendingUp,
  Target,
  Zap,
  CheckCircle,
  XCircle,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface MetaEngineState {
  initialized: boolean;
  running: boolean;
  observations: number;
  patterns: number;
  recommendations: { total: number; pending: number; accepted: number; rejected: number; average_confidence: number };
  knowledge: { total_entries: number; total_reports: number; entry_types: Record<string, number> };
}

interface Pattern {
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
  status: string;
}

interface Recommendation {
  id: string;
  title: string;
  description: string;
  type: string;
  domain: string;
  suggested_change: string;
  expected_impact: string;
  confidence: number;
  limitations: string;
  status: string;
}

interface Experiment {
  id: string;
  name: string;
  description: string;
  type: string;
  variable_name: string;
  duration_ticks: number;
  status: string;
  result_summary: string;
}

interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  type: string;
  source: string;
  confidence: number;
  created_at: string;
}

export default function MetaPage() {
  const [state, setState] = useState<MetaEngineState | null>(null);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [knowledge, setKnowledge] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "patterns" | "experiments" | "knowledge" | "recommendations">("overview");
  const [expName, setExpName] = useState("");
  const [expVar, setExpVar] = useState("");
  const [insightText, setInsightText] = useState("");

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  };

  useEffect(() => {
    loadMetaState();
  }, []);

  const loadMetaState = async () => {
    try {
      const [stateRes, patRes, recRes, expRes, knowRes] = await Promise.all([
        fetch(`${API}/api/v1/meta/state`, { headers: authHeaders() }),
        fetch(`${API}/api/v1/meta/patterns`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/meta/recommendations`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/meta/experiments`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/meta/knowledge`, { headers: authHeaders() }).catch(() => null),
      ]);
      if (stateRes.ok) setState(await stateRes.json());
      if (patRes?.ok) {
        const d = await patRes.json();
        setPatterns(d.patterns || []);
      }
      if (recRes?.ok) {
        const d = await recRes.json();
        setRecommendations(d.recommendations || []);
      }
      if (expRes?.ok) {
        const d = await expRes.json();
        setExperiments(d.experiments || []);
      }
      if (knowRes?.ok) {
        const d = await knowRes.json();
        setKnowledge(d.entries || []);
      }
    } catch (err) {
      console.error("Failed to load meta state", err);
    } finally {
      setLoading(false);
    }
  };

  const discoverPatterns = async () => {
    try {
      await fetch(`${API}/api/v1/meta/patterns/discover`, { method: "POST", headers: authHeaders() });
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const evaluateRules = async () => {
    try {
      await fetch(`${API}/api/v1/meta/rules/evaluate`, { method: "POST", headers: authHeaders() });
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const generateRecommendations = async () => {
    try {
      await fetch(`${API}/api/v1/meta/recommendations/generate`, { method: "POST", headers: authHeaders() });
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const createExperiment = async () => {
    if (!expName.trim()) return;
    try {
      await fetch(`${API}/api/v1/meta/experiments/create`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ name: expName, description: expVar ? `Test ${expVar}` : "", variable_name: expVar || undefined, experiment_type: "controlled", duration_ticks: 100 }),
      });
      setExpName("");
      setExpVar("");
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const addInsight = async () => {
    if (!insightText.trim()) return;
    try {
      await fetch(`${API}/api/v1/meta/knowledge/insight?insight=${encodeURIComponent(insightText)}`, { method: "POST", headers: authHeaders() });
      setInsightText("");
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const reviewRec = async (recId: string, status: string) => {
    try {
      await fetch(`${API}/api/v1/meta/recommendations/${recId}/review?status=${status}`, { method: "POST", headers: authHeaders() });
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const runExperiment = async (expId: string) => {
    try {
      await fetch(`${API}/api/v1/meta/experiments/${expId}/run`, { method: "POST", headers: authHeaders() });
      loadMetaState();
    } catch (err) {
      console.error(err);
    }
  };

  const confidenceColor = (c: number) => {
    if (c >= 0.7) return "text-green-400";
    if (c >= 0.4) return "text-yellow-400";
    return "text-red-400";
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading meta intelligence...</div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <BrainCircuit className="h-8 w-8" />
              Meta Intelligence
            </h1>
            <p className="text-muted-foreground mt-1">
              Analyze simulations, discover patterns, run experiments, and generate recommendations
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={discoverPatterns} className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium hover:bg-secondary/80">
              <Lightbulb className="h-4 w-4" /> Discover Patterns
            </button>
            <button onClick={evaluateRules} className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium hover:bg-secondary/80">
              <BarChart3 className="h-4 w-4" /> Evaluate Rules
            </button>
            <button onClick={generateRecommendations} className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium hover:bg-secondary/80">
              <Target className="h-4 w-4" /> Generate Recommendations
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Observations</div>
            <div className="text-2xl font-bold mt-1">{state?.observations || 0}</div>
            <div className="text-xs text-muted-foreground mt-1">Civilization snapshots</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Patterns</div>
            <div className="text-2xl font-bold mt-1">{state?.patterns || 0}</div>
            <div className="text-xs text-muted-foreground mt-1">Discovered relationships</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Recommendations</div>
            <div className="text-2xl font-bold mt-1">{state?.recommendations?.total || 0}</div>
            <div className="text-xs text-muted-foreground mt-1">{state?.recommendations?.pending || 0} pending review</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Knowledge Base</div>
            <div className="text-2xl font-bold mt-1">{state?.knowledge?.total_entries || 0}</div>
            <div className="text-xs text-muted-foreground mt-1">{state?.knowledge?.total_reports || 0} reports</div>
          </div>
        </div>

        <div className="flex gap-1 border-b">
          {(["overview", "patterns", "experiments", "knowledge", "recommendations"] as const).map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab ? "border-foreground text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
              }`}>
              {tab === "overview" && <Eye className="h-4 w-4" />}
              {tab === "patterns" && <GitBranch className="h-4 w-4" />}
              {tab === "experiments" && <FlaskConical className="h-4 w-4" />}
              {tab === "knowledge" && <BookOpen className="h-4 w-4" />}
              {tab === "recommendations" && <Target className="h-4 w-4" />}
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Meta Intelligence Dashboard</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The Meta Intelligence layer observes all civilizations, analyzes simulation outcomes, discovers patterns, runs controlled experiments, and generates evidence-backed recommendations. It never directly controls civilizations — it observes, explains, and proposes.
              </p>
              <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><Eye className="h-4 w-4" /> Observation</div>
                  <div className="text-xs text-muted-foreground mt-1">Monitors population, economy, research, technology, education, governance, environment, innovation, stability</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><GitBranch className="h-4 w-4" /> Pattern Discovery</div>
                  <div className="text-xs text-muted-foreground mt-1">Detects recurring causal relationships like "High research → Technology growth" with confidence scores</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><FlaskConical className="h-4 w-4" /> Experiments</div>
                  <div className="text-xs text-muted-foreground mt-1">Creates controlled experiments, changes one variable, runs simulations, compares outcomes</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><BarChart3 className="h-4 w-4" /> Rule Evaluation</div>
                  <div className="text-xs text-muted-foreground mt-1">Evaluates simulation rules for effectiveness, stability, and side effects</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><Target className="h-4 w-4" /> Recommendations</div>
                  <div className="text-xs text-muted-foreground mt-1">Generates evidence-backed suggestions for improving future simulations</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><BookOpen className="h-4 w-4" /> Knowledge Base</div>
                  <div className="text-xs text-muted-foreground mt-1">Maintains long-term findings, best practices, experiment results, and simulation reports</div>
                </div>
              </div>
            </div>

            {patterns.length > 0 && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3">Active Patterns</h3>
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  {patterns.slice(0, 4).map((pat) => (
                    <div key={pat.id} className="rounded-md border p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{pat.title}</span>
                        <span className={`text-xs font-medium ${confidenceColor(pat.confidence)}`}>{(pat.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{pat.description}</p>
                      <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
                        <span>Support: {(pat.support * 100).toFixed(0)}%</span>
                        <span>Lift: {pat.lift.toFixed(1)}</span>
                        <span>Samples: {pat.sample_size}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "patterns" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Discovered Patterns</h3>
              {patterns.length === 0 ? (
                <p className="text-muted-foreground text-sm">Click "Discover Patterns" to start detecting recurring relationships across simulations.</p>
              ) : (
                <div className="space-y-3">
                  {patterns.map((pat) => (
                    <div key={pat.id} className="rounded-md border p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <GitBranch className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{pat.title}</span>
                        </div>
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${confidenceColor(pat.confidence)} bg-secondary`}>
                          {(pat.confidence * 100).toFixed(0)}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">{pat.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span>Type: {pat.type}</span>
                        <span>Support: {(pat.support * 100).toFixed(0)}%</span>
                        <span>Lift: {pat.lift.toFixed(2)}</span>
                        <span>Sample: {pat.sample_size} runs</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "experiments" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Create Controlled Experiment</h3>
              <div className="flex gap-2">
                <input type="text" value={expName} onChange={(e) => setExpName(e.target.value)} placeholder="Experiment name..."
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm" />
                <input type="text" value={expVar} onChange={(e) => setExpVar(e.target.value)} placeholder="Variable to change..."
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm" />
                <button onClick={createExperiment} disabled={!expName.trim()}
                  className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                  <FlaskConical className="h-4 w-4" /> Create
                </button>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Experiments</h3>
              {experiments.length === 0 ? (
                <p className="text-muted-foreground text-sm">No experiments created yet. Create an experiment to compare different simulation outcomes.</p>
              ) : (
                <div className="space-y-2">
                  {experiments.map((exp) => (
                    <div key={exp.id} className="flex items-center gap-3 rounded-md border p-3 hover:bg-secondary/50">
                      <FlaskConical className="h-5 w-5 text-muted-foreground shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium">{exp.name}</div>
                        {exp.variable_name && <div className="text-xs text-muted-foreground">Variable: {exp.variable_name}</div>}
                      </div>
                      <div className="text-right shrink-0">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          exp.status === "completed" ? "bg-green-500/20 text-green-400" :
                          exp.status === "running" ? "bg-blue-500/20 text-blue-400" :
                          "bg-yellow-500/20 text-yellow-400"
                        }`}>{exp.status}</span>
                      </div>
                      {exp.status === "pending" && (
                        <button onClick={() => runExperiment(exp.id)}
                          className="rounded-md bg-secondary px-3 py-1 text-xs font-medium hover:bg-secondary/80">
                          Run
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "knowledge" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Record Insight</h3>
              <div className="flex gap-2">
                <input type="text" value={insightText} onChange={(e) => setInsightText(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addInsight()}
                  placeholder="Enter a universe insight..."
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm" />
                <button onClick={addInsight} disabled={!insightText.trim()}
                  className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                  <BookOpen className="h-4 w-4" /> Save Insight
                </button>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Knowledge Base Entries</h3>
              {knowledge.length === 0 ? (
                <p className="text-muted-foreground text-sm">No knowledge entries yet. Knowledge is accumulated from patterns, experiments, and insights.</p>
              ) : (
                <div className="space-y-2">
                  {knowledge.map((entry) => (
                    <div key={entry.id} className="rounded-md border p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs font-medium">{entry.type}</span>
                          <span className="text-sm font-medium">{entry.title}</span>
                        </div>
                        <span className={`text-xs font-medium ${confidenceColor(entry.confidence)}`}>{(entry.confidence * 100).toFixed(0)}%</span>
                      </div>
                      {entry.content && <p className="text-xs text-muted-foreground mt-1">{entry.content}</p>}
                      <div className="text-xs text-muted-foreground mt-1">
                        {entry.source && <span>Source: {entry.source} · </span>}
                        <span>{entry.created_at ? new Date(entry.created_at).toLocaleDateString() : ""}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "recommendations" && (
          <div className="space-y-4">
            {recommendations.length === 0 ? (
              <div className="rounded-lg border bg-card p-8 text-center">
                <Target className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-semibold mb-2">No Recommendations Yet</h3>
                <p className="text-sm text-muted-foreground mb-4">Click "Generate Recommendations" to get evidence-backed suggestions for improving simulations.</p>
                <button onClick={generateRecommendations} className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                  Generate Recommendations
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="rounded-lg border bg-card p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Target className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{rec.title}</span>
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                            rec.status === "accepted" ? "bg-green-500/20 text-green-400" :
                            rec.status === "rejected" ? "bg-red-500/20 text-red-400" :
                            "bg-yellow-500/20 text-yellow-400"
                          }`}>{rec.status}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
                        <div className="grid grid-cols-2 gap-4 mt-2 text-xs">
                          <div><span className="text-muted-foreground">Suggested Change:</span> <span className="font-medium">{rec.suggested_change}</span></div>
                          <div><span className="text-muted-foreground">Expected Impact:</span> <span className="font-medium">{rec.expected_impact}</span></div>
                          <div><span className="text-muted-foreground">Domain:</span> <span className="font-medium">{rec.domain}</span></div>
                          <div><span className={`font-medium ${confidenceColor(rec.confidence)}`}>Confidence: {(rec.confidence * 100).toFixed(0)}%</span></div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">{rec.limitations}</div>
                      </div>
                      {rec.status === "pending" && (
                        <div className="flex gap-1 ml-4">
                          <button onClick={() => reviewRec(rec.id, "accepted")} className="flex items-center gap-1 rounded-md bg-green-500/20 px-2 py-1 text-xs font-medium text-green-400 hover:bg-green-500/30">
                            <CheckCircle className="h-3 w-3" /> Accept
                          </button>
                          <button onClick={() => reviewRec(rec.id, "rejected")} className="flex items-center gap-1 rounded-md bg-red-500/20 px-2 py-1 text-xs font-medium text-red-400 hover:bg-red-500/30">
                            <XCircle className="h-3 w-3" /> Reject
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
