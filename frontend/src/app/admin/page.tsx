"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import {
  Shield,
  Activity,
  AlertTriangle,
  Gauge,
  CheckCircle2,
  RotateCcw,
  FileText,
  Play,
  Pause,
  Zap,
  Camera,
  BarChart3,
  ServerCrash,
  Search,
  Wrench,
} from "lucide-react";
import type {
  ManagementState, AnomalyAlertData, PerformanceData, OptimizationData,
  IntegrityCheck, RecoveryEntry, AdminLogEntry, SimulationAnalysis, EventExplanation,
} from "@/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminPage() {
  const [state, setState] = useState<ManagementState | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyAlertData[]>([]);
  const [performance, setPerformance] = useState<PerformanceData[]>([]);
  const [optimizations, setOptimizations] = useState<OptimizationData[]>([]);
  const [integrity, setIntegrity] = useState<IntegrityCheck[]>([]);
  const [recoveries, setRecoveries] = useState<RecoveryEntry[]>([]);
  const [logs, setLogs] = useState<AdminLogEntry[]>([]);
  const [analysis, setAnalysis] = useState<SimulationAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "anomalies" | "performance" | "integrity" | "recovery" | "logs" | "assistant">("overview");

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  };

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [s, a, p, o, i, r, l, an] = await Promise.all([
        fetch(`${API}/api/v1/admin/state`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/anomalies`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/performance`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/performance/optimizations`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/integrity`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/recovery/history`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/logs?limit=30`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/admin/assistant/analyze`, { headers: authHeaders() }).catch(() => null),
      ]);
      if (s?.ok) setState(await s.json());
      if (a?.ok) { const d = await a.json(); setAnomalies(d.anomalies || []); }
      if (p?.ok) { const d = await p.json(); setPerformance(d.snapshots || []); }
      if (o?.ok) { const d = await o.json(); setOptimizations(d.optimizations || []); }
      if (i?.ok) { const d = await i.json(); setIntegrity(d.checks || []); }
      if (r?.ok) { const d = await r.json(); setRecoveries(d.recoveries || []); }
      if (l?.ok) { const d = await l.json(); setLogs(d.logs || []); }
      if (an?.ok) setAnalysis(await an.json());
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const resolveAlert = async (id: string) => {
    await fetch(`${API}/api/v1/admin/anomalies/${id}/resolve`, { method: "POST", headers: authHeaders() });
    loadAll();
  };

  const applyOpt = async (id: string) => {
    await fetch(`${API}/api/v1/admin/performance/optimizations/${id}/apply`, { method: "POST", headers: authHeaders() });
    loadAll();
  };

  const triggerRecovery = async () => {
    await fetch(`${API}/api/v1/admin/recovery/restore-snapshot?snapshot_id=manual`, { method: "POST", headers: authHeaders() });
    loadAll();
  };

  if (loading) {
    return <AppLayout><div className="flex items-center justify-center h-64"><div className="text-muted-foreground">Loading admin console...</div></div></AppLayout>;
  }

  const health = state?.health;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Shield className="h-8 w-8" />
              Universe Management
            </h1>
            <p className="text-muted-foreground mt-1">Monitor, control, and maintain the NEXUS universe</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
              health?.overall_status === "healthy" ? "bg-green-500/20 text-green-400" :
              health?.overall_status === "degraded" ? "bg-yellow-500/20 text-yellow-400" :
              "bg-red-500/20 text-red-400"
            }`}>
              <Activity className="h-3 w-3" />
              {health?.overall_status || "unknown"}
            </span>
            <span className="text-sm text-muted-foreground">Score: {health?.health_score?.toFixed(2) || "—"}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Activity className="h-3 w-3" /> Health Metrics</div>
            <div className="text-xl font-bold">{health?.total_metrics || 0}</div>
            <div className="text-xs text-muted-foreground">{health?.degraded_metrics?.length || 0} degraded</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><AlertTriangle className="h-3 w-3" /> Anomalies</div>
            <div className="text-xl font-bold">{anomalies.filter(a => !a.resolved).length}</div>
            <div className="text-xs text-muted-foreground">{anomalies.length} total</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><BarChart3 className="h-3 w-3" /> Performance</div>
            <div className="text-xl font-bold">{performance.length > 0 ? `${performance[0].avg_tick_ms}ms` : "—"}</div>
            <div className="text-xs text-muted-foreground">{performance.length > 0 ? `${performance[0].agents} agents` : "No data"}</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><RotateCcw className="h-3 w-3" /> Recoveries</div>
            <div className="text-xl font-bold">{recoveries.length}</div>
            <div className="text-xs text-muted-foreground">{recoveries.filter(r => r.success).length} successful</div>
          </div>
        </div>

        <div className="flex gap-1 border-b overflow-x-auto">
          {(["overview", "anomalies", "performance", "integrity", "recovery", "logs", "assistant"] as const).map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === tab ? "border-foreground text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
              }`}>
              {tab === "overview" && <Shield className="h-4 w-4" />}
              {tab === "anomalies" && <AlertTriangle className="h-4 w-4" />}
              {tab === "performance" && <Gauge className="h-4 w-4" />}
              {tab === "integrity" && <CheckCircle2 className="h-4 w-4" />}
              {tab === "recovery" && <RotateCcw className="h-4 w-4" />}
              {tab === "logs" && <FileText className="h-4 w-4" />}
              {tab === "assistant" && <Search className="h-4 w-4" />}
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2"><Activity className="h-4 w-4" /> Health Monitor</h3>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                {health?.metrics && Object.entries(health.metrics).map(([name, m]) => (
                  <div key={name} className="rounded-md border p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium">{name.replace(/_/g, " ")}</span>
                      <span className={`text-xs font-medium ${
                        m.status === "healthy" ? "text-green-400" :
                        m.status === "degraded" ? "text-yellow-400" : "text-red-400"
                      }`}>{m.status}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 rounded-full bg-secondary overflow-hidden">
                        <div className={`h-full rounded-full transition-all ${
                          m.status === "healthy" ? "bg-green-500" :
                          m.status === "degraded" ? "bg-yellow-500" : "bg-red-500"
                        }`} style={{ width: `${m.value * 100}%` }} />
                      </div>
                      <span className="text-xs text-muted-foreground">{(m.value * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><Zap className="h-4 w-4" /> Quick Controls</h3>
                <div className="grid grid-cols-2 gap-2">
                  <button className="flex items-center gap-2 rounded-md border p-3 text-sm hover:bg-secondary/50 transition-colors">
                    <Pause className="h-4 w-4" /> Pause Universe
                  </button>
                  <button className="flex items-center gap-2 rounded-md border p-3 text-sm hover:bg-secondary/50 transition-colors">
                    <Play className="h-4 w-4" /> Resume Universe
                  </button>
                  <button className="flex items-center gap-2 rounded-md border p-3 text-sm hover:bg-secondary/50 transition-colors">
                    <Camera className="h-4 w-4" /> Create Snapshot
                  </button>
                  <button onClick={triggerRecovery} className="flex items-center gap-2 rounded-md border p-3 text-sm hover:bg-secondary/50 transition-colors">
                    <RotateCcw className="h-4 w-4" /> Restore Snapshot
                  </button>
                </div>
              </div>

              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Recent Integrity</h3>
                {integrity.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No integrity checks run yet.</p>
                ) : (
                  <div className="space-y-2">
                    {integrity.map((c, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <span className={`h-2 w-2 rounded-full ${c.status === "passed" ? "bg-green-400" : "bg-red-400"}`} />
                        <span className="flex-1">{c.check.replace(/_/g, " ")}</span>
                        <span className="text-xs text-muted-foreground">{c.status}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {analysis && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><Search className="h-4 w-4" /> Simulation Analysis</h3>
                <p className="text-sm mb-3">{analysis.overview}</p>
                <div className="space-y-2">
                  {analysis.recommendations.map((r, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm">
                      <span className="text-muted-foreground mt-0.5">•</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "anomalies" && (
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold flex items-center gap-2"><AlertTriangle className="h-4 w-4" /> Anomaly Alerts</h3>
              <button onClick={loadAll} className="text-xs text-muted-foreground hover:text-foreground">Refresh</button>
            </div>
            {anomalies.length === 0 ? (
              <p className="text-sm text-muted-foreground">No anomalies detected. The universe is stable.</p>
            ) : (
              <div className="space-y-2">
                {anomalies.map((a) => (
                  <div key={a.id} className={`rounded-md border p-3 ${a.resolved ? "opacity-50" : ""}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`h-2 w-2 rounded-full ${
                          a.severity === "critical" ? "bg-red-400" :
                          a.severity === "warning" ? "bg-yellow-400" : "bg-blue-400"
                        }`} />
                        <span className="text-sm font-medium">{a.title}</span>
                        <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                          a.severity === "critical" ? "bg-red-500/20 text-red-400" :
                          a.severity === "warning" ? "bg-yellow-500/20 text-yellow-400" :
                          "bg-blue-500/20 text-blue-400"
                        }`}>{a.severity}</span>
                      </div>
                      {!a.resolved && (
                        <button onClick={() => resolveAlert(a.id)}
                          className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded hover:bg-green-500/30">
                          Resolve
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{a.description}</p>
                    <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
                      <span>System: {a.affected_system}</span>
                      <span>Cause: {a.cause}</span>
                    </div>
                    {a.suggested_action && (
                      <div className="mt-1 text-xs text-muted-foreground">
                        <span className="font-medium">Action: </span>{a.suggested_action}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "performance" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold flex items-center gap-2"><Gauge className="h-4 w-4" /> Performance Snapshots</h3>
                <button onClick={loadAll} className="text-xs text-muted-foreground hover:text-foreground">Refresh</button>
              </div>
              {performance.length === 0 ? (
                <p className="text-sm text-muted-foreground">No performance data recorded yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-xs text-muted-foreground">
                        <th className="pb-2 pr-4">Tick</th>
                        <th className="pb-2 pr-4">Agents</th>
                        <th className="pb-2 pr-4">Active</th>
                        <th className="pb-2 pr-4">Tick Time</th>
                        <th className="pb-2 pr-4">Memory</th>
                        <th className="pb-2 pr-4">Cache Hit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {performance.map((p, i) => (
                        <tr key={i} className="border-b last:border-0">
                          <td className="py-2 pr-4 text-muted-foreground">{p.tick}</td>
                          <td className="py-2 pr-4">{p.agents}</td>
                          <td className="py-2 pr-4">{p.active}</td>
                          <td className="py-2 pr-4">{p.avg_tick_ms}ms</td>
                          <td className="py-2 pr-4">{p.memory_mb}MB</td>
                          <td className="py-2 pr-4">{(p.cache_hit * 100).toFixed(0)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="rounded-lg border bg-card p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold flex items-center gap-2"><Wrench className="h-4 w-4" /> Optimization Suggestions</h3>
                <button onClick={loadAll} className="text-xs text-muted-foreground hover:text-foreground">Refresh</button>
              </div>
              {optimizations.length === 0 ? (
                <p className="text-sm text-muted-foreground">No optimization suggestions available.</p>
              ) : (
                <div className="space-y-2">
                  {optimizations.map((o) => (
                    <div key={o.id} className="flex items-center justify-between rounded-md border p-3">
                      <div className="flex-1">
                        <div className="text-sm font-medium">{o.type}</div>
                        <div className="text-xs text-muted-foreground">{o.description}</div>
                        <div className="text-xs text-muted-foreground mt-1">Impact: {o.impact}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          o.status === "applied" ? "bg-green-500/20 text-green-400" :
                          o.status === "pending" ? "bg-yellow-500/20 text-yellow-400" :
                          "bg-gray-500/20 text-gray-400"
                        }`}>{o.status}</span>
                        {o.status !== "applied" && (
                          <button onClick={() => applyOpt(o.id)}
                            className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded hover:bg-blue-500/30">
                            Apply
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "integrity" && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Data Integrity Checks</h3>
            {integrity.length === 0 ? (
              <p className="text-sm text-muted-foreground">No integrity checks performed yet.</p>
            ) : (
              <div className="space-y-2">
                {integrity.map((c, i) => (
                  <div key={i} className="flex items-center gap-3 rounded-md border p-3">
                    <span className={`h-3 w-3 rounded-full ${
                      c.status === "passed" ? "bg-green-400" : "bg-red-400"
                    }`} />
                    <div className="flex-1">
                      <div className="text-sm font-medium">{c.check.replace(/_/g, " ")}</div>
                      <div className="text-xs text-muted-foreground">{c.message}</div>
                    </div>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                      c.status === "passed" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                    }`}>{c.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "recovery" && (
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold flex items-center gap-2"><RotateCcw className="h-4 w-4" /> Recovery Operations</h3>
              <div className="flex gap-2">
                <button onClick={triggerRecovery}
                  className="text-xs bg-blue-500/20 text-blue-400 px-3 py-1 rounded hover:bg-blue-500/30 flex items-center gap-1">
                  <ServerCrash className="h-3 w-3" /> Restore Snapshot
                </button>
              </div>
            </div>
            {recoveries.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recovery operations recorded.</p>
            ) : (
              <div className="space-y-2">
                {recoveries.map((r) => (
                  <div key={r.id} className="flex items-center gap-3 rounded-md border p-3">
                    <span className={`h-2 w-2 rounded-full ${r.success ? "bg-green-400" : "bg-red-400"}`} />
                    <div className="flex-1">
                      <div className="text-sm font-medium">{r.type.replace(/_/g, " ")}</div>
                      <div className="text-xs text-muted-foreground">Target: {r.target}</div>
                      <div className="text-xs text-muted-foreground">Cause: {r.cause}</div>
                    </div>
                    <span className="text-xs text-muted-foreground">{r.time ? new Date(r.time).toLocaleString() : ""}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "logs" && (
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold flex items-center gap-2"><FileText className="h-4 w-4" /> System Logs</h3>
              <button onClick={loadAll} className="text-xs text-muted-foreground hover:text-foreground">Refresh</button>
            </div>
            {logs.length === 0 ? (
              <p className="text-sm text-muted-foreground">No log entries recorded.</p>
            ) : (
              <div className="space-y-1 max-h-96 overflow-y-auto">
                {logs.map((l) => (
                  <div key={l.id} className="flex items-start gap-3 rounded-md border p-2 text-sm">
                    <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${
                      l.severity === "error" || l.severity === "critical" ? "bg-red-400" :
                      l.severity === "warning" ? "bg-yellow-400" : "bg-blue-400"
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-muted-foreground">{l.type}</span>
                        <span className={`text-xs px-1 py-0.5 rounded ${
                          l.severity === "error" || l.severity === "critical" ? "bg-red-500/20 text-red-400" :
                          l.severity === "warning" ? "bg-yellow-500/20 text-yellow-400" :
                          "bg-blue-500/20 text-blue-400"
                        }`}>{l.severity}</span>
                      </div>
                      <div className="text-sm">{l.message}</div>
                    </div>
                    <span className="text-xs text-muted-foreground shrink-0">{l.time ? new Date(l.time).toLocaleTimeString() : ""}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "assistant" && (
          <div className="space-y-4">
            {analysis && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><Search className="h-4 w-4" /> Simulation Analysis</h3>
                <p className="text-sm mb-3">{analysis.overview}</p>
                <div className="space-y-2">
                  {analysis.recommendations.map((r, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm p-2 rounded-md bg-secondary/30">
                      <span className="text-muted-foreground mt-0.5">•</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Event Explanations</h3>
              <p className="text-sm text-muted-foreground mb-3">Select an event type to get an AI-powered explanation of what happened and why.</p>
              <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
                {["civilization_collapse", "economic_boom"].map((evt) => (
                  <button key={evt}
                    onClick={async () => {
                      const res = await fetch(`${API}/api/v1/admin/assistant/explain/${evt}`, { headers: authHeaders() });
                      if (res.ok) {
                        const data: EventExplanation = await res.json();
                        alert(`${data.title}\n\nConfidence: ${(data.confidence * 100).toFixed(0)}%\n\nFactors:\n${data.factors.map(f => `- ${f.factor} (${f.weight}): ${f.description}`).join("\n")}${data.recommendation ? `\n\nRecommendation: ${data.recommendation}` : ""}`);
                      }
                    }}
                    className="rounded-md border p-3 text-sm hover:bg-secondary/50 transition-colors text-left">
                    <div className="font-medium">{evt.replace(/_/g, " ")}</div>
                    <div className="text-xs text-muted-foreground mt-1">Get explanation</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
