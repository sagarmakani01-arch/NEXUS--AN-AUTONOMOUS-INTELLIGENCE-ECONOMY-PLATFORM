"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { DiscoveryEngineState, DiscoveryStats, Hypothesis, ResearchLaboratory, ResearchReport, ScienceKnowledgeGraph, ScientificExperiment } from "@/types";

export default function ResearchPage() {
  const [state, setState] = useState<DiscoveryEngineState | null>(null);
  const [stats, setStats] = useState<DiscoveryStats | null>(null);
  const [experiments, setExperiments] = useState<ScientificExperiment[]>([]);
  const [patterns, setPatterns] = useState<unknown[]>([]);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [labs, setLabs] = useState<ResearchLaboratory[]>([]);
  const [reports, setReports] = useState<ResearchReport[]>([]);
  const [knowledgeGraph, setKnowledgeGraph] = useState<ScienceKnowledgeGraph | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  const fetchAll = async () => {
    try {
      const [stateRes, statsRes, expRes, patRes, hypRes, labsRes, repRes, kgRes] = await Promise.all([
        api.get("/api/v1/discovery/state"),
        api.get("/api/v1/discovery/stats"),
        api.get("/api/v1/discovery/experiments?limit=10"),
        api.get("/api/v1/discovery/patterns?limit=10"),
        api.get("/api/v1/discovery/hypotheses?limit=10"),
        api.get("/api/v1/discovery/laboratories"),
        api.get("/api/v1/discovery/reports?limit=10"),
        api.get("/api/v1/discovery/knowledge"),
      ]);
      if (stateRes) setState(stateRes as DiscoveryEngineState);
      if (statsRes) setStats(statsRes as DiscoveryStats);
      if (expRes) setExperiments(expRes as ScientificExperiment[]);
      if (patRes) setPatterns(patRes as unknown[]);
      if (hypRes) setHypotheses(hypRes as Hypothesis[]);
      if (labsRes) setLabs(labsRes as ResearchLaboratory[]);
      if (repRes) setReports(repRes as ResearchReport[]);
      if (kgRes) setKnowledgeGraph(kgRes as ScienceKnowledgeGraph);
    } catch (e) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); const iv = setInterval(fetchAll, 15000); return () => clearInterval(iv); }, []);

  const tabs = [
    { key: "overview", label: "Overview" },
    { key: "experiments", label: "Experiments" },
    { key: "patterns", label: "Patterns" },
    { key: "hypotheses", label: "Hypotheses" },
    { key: "labs", label: "Laboratories" },
    { key: "reports", label: "Reports" },
    { key: "knowledge", label: "Knowledge Graph" },
  ];

  if (loading) return <div className="p-8 text-center text-muted-foreground">Loading research data...</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Scientific Discovery</h1>
          <p className="text-muted-foreground">Computational research environment for experiment design, pattern discovery, and hypothesis testing</p>
        </div>
        <Badge className="text-xs">{state?.running ? "Active" : "Idle"}</Badge>
      </div>

      <div className="grid gap-4 grid-cols-2 md:grid-cols-4 lg:grid-cols-8">
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Experiments</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.experiments ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Patterns</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.patterns ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Hypotheses</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.hypotheses ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Reports</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.reports ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Laboratories</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.laboratories ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Research Agents</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.research_agents ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Archives</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.archives ?? 0}</p></CardContent></Card>
        <Card><CardHeader className="p-3"><CardTitle className="text-xs font-medium text-muted-foreground">Snapshots</CardTitle></CardHeader><CardContent className="p-3 pt-0"><p className="text-2xl font-bold">{stats?.snapshots ?? 0}</p></CardContent></Card>
      </div>

      <div className="flex flex-wrap gap-1 border-b pb-2">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => setActiveTab(t.key)} className={`px-3 py-1.5 text-sm rounded-md transition-colors ${activeTab === t.key ? "bg-secondary text-foreground font-medium" : "text-muted-foreground hover:text-foreground"}`}>{t.label}</button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader><CardTitle className="text-sm">Engine State</CardTitle></CardHeader>
            <CardContent className="text-sm space-y-2">
              <div className="flex justify-between"><span className="text-muted-foreground">Status</span><Badge className="text-xs">{state?.running ? "Running" : "Idle"}</Badge></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Ticks</span><span>{state?.stats.total_ticks ?? 0}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Experiments Created</span><span>{state?.stats.experiments_created ?? 0}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Patterns Discovered</span><span>{state?.stats.patterns_discovered ?? 0}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Hypotheses Generated</span><span>{state?.stats.hypotheses_generated ?? 0}</span></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm">Recent Experiments</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {experiments.slice(0, 5).map((exp) => (
                <div key={exp.id} className="text-xs border-b pb-1 last:border-0">
                  <div className="font-medium truncate">{exp.title}</div>
                  <div className="text-muted-foreground flex gap-2"><span>{exp.status}</span><span>Conf: {(exp.confidence_score * 100).toFixed(0)}%</span></div>
                </div>
              ))}
              {experiments.length === 0 && <p className="text-xs text-muted-foreground">No experiments yet</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm">Active Laboratories</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {labs.filter((l) => l.active).slice(0, 5).map((lab) => (
                <div key={lab.id} className="text-xs border-b pb-1 last:border-0">
                  <div className="font-medium">{lab.name}</div>
                  <div className="text-muted-foreground">{lab.experiment_count} experiments</div>
                </div>
              ))}
              {labs.length === 0 && <p className="text-xs text-muted-foreground">No laboratories initialized</p>}
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "experiments" && (
        <Card>
          <CardHeader><CardTitle>Scientific Experiments ({experiments.length})</CardTitle></CardHeader>
          <CardContent>
            {experiments.length === 0 ? (
              <p className="text-sm text-muted-foreground">No experiments conducted yet. The discovery engine will auto-generate experiments.</p>
            ) : (
              <div className="space-y-3">
                {experiments.map((exp) => (
                  <div key={exp.id} className="text-sm border rounded-lg p-3">
                    <div className="flex items-center justify-between"><span className="font-medium">{exp.title}</span><Badge className="text-xs">{exp.status}</Badge></div>
                    {exp.research_question && <p className="text-xs text-muted-foreground mt-1">{exp.research_question}</p>}
                    <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
                      <span>Lab: {exp.laboratory_type}</span><span>Duration: {exp.duration_ticks} ticks</span><span>Confidence: {(exp.confidence_score * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === "patterns" && (
        <Card>
          <CardHeader><CardTitle>Discovered Patterns ({patterns.length})</CardTitle></CardHeader>
          <CardContent>
            {patterns.length === 0 ? (
              <p className="text-sm text-muted-foreground">No patterns discovered yet. Pattern discovery runs automatically.</p>
            ) : (
              <div className="space-y-2">
                {(patterns as Array<{ id: string; title: string; pattern_type: string; confidence: number; description: string | null }>).map((p) => (
                  <div key={p.id} className="text-sm border rounded-lg p-3">
                    <div className="flex items-center justify-between"><span className="font-medium">{p.title}</span><Badge className="text-xs">{p.pattern_type}</Badge></div>
                    {p.description && <p className="text-xs text-muted-foreground mt-1">{p.description}</p>}
                    <div className="text-xs text-muted-foreground mt-1">Confidence: {(p.confidence * 100).toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === "hypotheses" && (
        <Card>
          <CardHeader><CardTitle>Generated Hypotheses ({hypotheses.length})</CardTitle></CardHeader>
          <CardContent>
            {hypotheses.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hypotheses generated yet. The engine will create them from discovered patterns.</p>
            ) : (
              <div className="space-y-3">
                {hypotheses.map((h) => (
                  <div key={h.id} className="text-sm border rounded-lg p-3">
                    <div className="flex items-center justify-between"><span className="font-medium">{h.title}</span><Badge className="text-xs">{h.status}</Badge></div>
                    {h.description && <p className="text-xs mt-1">{h.description}</p>}
                    <div className="flex gap-3 mt-2 text-xs text-muted-foreground"><span>Domain: {h.domain}</span><span>Confidence: {(h.confidence_level * 100).toFixed(1)}%</span></div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === "labs" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {labs.map((lab) => (
            <Card key={lab.id}>
              <CardHeader><CardTitle className="text-sm">{lab.name}</CardTitle></CardHeader>
              <CardContent className="text-xs space-y-2">
                {lab.description && <p className="text-muted-foreground">{lab.description}</p>}
                <div className="flex justify-between"><span className="text-muted-foreground">Type</span><span>{lab.lab_type}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Experiments</span><span>{lab.experiment_count}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Active</span><span>{lab.active ? "Yes" : "No"}</span></div>
                {lab.specialization.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">{lab.specialization.map((s) => <Badge key={s} className="text-xs">{s}</Badge>)}</div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {activeTab === "reports" && (
        <Card>
          <CardHeader><CardTitle>Research Reports ({reports.length})</CardTitle></CardHeader>
          <CardContent>
            {reports.length === 0 ? (
              <p className="text-sm text-muted-foreground">No reports generated yet.</p>
            ) : (
              <div className="space-y-3">
                {reports.map((r) => (
                  <div key={r.id} className="text-sm border rounded-lg p-3">
                    <div className="flex items-center justify-between"><span className="font-medium">{r.title}</span><Badge className="text-xs">{r.status}</Badge></div>
                    {r.research_question && <p className="text-xs text-muted-foreground mt-1">{r.research_question}</p>}
                    <div className="text-xs text-muted-foreground mt-1">Confidence: {(r.confidence_score * 100).toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === "knowledge" && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Knowledge Nodes ({knowledgeGraph?.node_count ?? 0})</CardTitle></CardHeader>
            <CardContent>
              {knowledgeGraph && knowledgeGraph.nodes.length > 0 ? (
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {knowledgeGraph.nodes.map((n) => (
                    <div key={n.id} className="text-xs border rounded p-2">
                      <div className="font-medium">{n.name}</div>
                      <div className="text-muted-foreground">Type: {n.node_type}</div>
                      <div className="text-muted-foreground">Importance: {n.importance.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              ) : <p className="text-sm text-muted-foreground">No knowledge nodes yet.</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Knowledge Edges ({knowledgeGraph?.edge_count ?? 0})</CardTitle></CardHeader>
            <CardContent>
              {knowledgeGraph && knowledgeGraph.edges.length > 0 ? (
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {knowledgeGraph.edges.map((e) => (
                    <div key={e.id} className="text-xs border rounded p-2">
                      <div className="font-medium">{e.edge_type}</div>
                      <div className="text-muted-foreground">{e.source_node_id.slice(0, 8)} &rarr; {e.target_node_id.slice(0, 8)}</div>
                      <div className="text-muted-foreground">Weight: {e.weight.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              ) : <p className="text-sm text-muted-foreground">No knowledge edges yet.</p>}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
