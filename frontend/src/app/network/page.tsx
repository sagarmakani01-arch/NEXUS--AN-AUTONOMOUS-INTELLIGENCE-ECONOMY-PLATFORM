"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import {
  Server, Globe, Activity, Gauge, HardDrive, Clock, AlertTriangle,
  Zap, Cpu, Wifi, Database, Shield, Network, Boxes,
} from "lucide-react";
import type {
  ComputeEngineState, ComputeNode, ComputePartition, ComputeTask,
  ComputeBalanceStatus,
} from "@/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function NetworkPage() {
  const [state, setState] = useState<ComputeEngineState | null>(null);
  const [partitions, setPartitions] = useState<ComputePartition[]>([]);
  const [tasks, setTasks] = useState<ComputeTask[]>([]);
  const [loading, setLoading] = useState(true);

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  };

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [s, p, t] = await Promise.all([
        fetch(`${API}/api/v1/compute/state`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/compute/partitions`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/compute/tasks`, { headers: authHeaders() }).catch(() => null),
      ]);
      if (s?.ok) setState(await s.json());
      if (p?.ok) { const d = await p.json(); setPartitions(d.partitions || []); }
      if (t?.ok) { const d = await t.json(); setTasks(d.tasks || []); }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  if (loading) {
    return <AppLayout><div className="flex items-center justify-center h-64"><div className="text-muted-foreground">Connecting to compute network...</div></div></AppLayout>;
  }

  const nodes = state?.nodes?.list || [];
  const onlineNodes = nodes.filter(n => n.status === "online");
  const tasksData = state?.tasks;
  const balance = state?.balance;
  const storage = state?.storage;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Network className="h-8 w-8" />
              Compute Network
            </h1>
            <p className="text-muted-foreground mt-1">Distributed universe computation infrastructure</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-sm">
              <Clock className="h-4 w-4 text-muted-foreground" />
              Tick {state?.clock?.tick_count || 0}
            </span>
            <span className={`flex items-center gap-1.5 text-sm ${
              state?.clock?.paused ? "text-yellow-400" : "text-green-400"
            }`}>
              <Activity className="h-4 w-4" />
              {state?.clock?.paused ? "Paused" : "Running"}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Server className="h-3 w-3" /> Nodes</div>
            <div className="text-xl font-bold">{state?.nodes?.total || 0}</div>
            <div className="text-xs text-muted-foreground">{state?.nodes?.online || 0} online</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Boxes className="h-3 w-3" /> Partitions</div>
            <div className="text-xl font-bold">{state?.partitions?.total || 0}</div>
            <div className="text-xs text-muted-foreground">{state?.partitions?.assigned || 0} assigned</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Zap className="h-3 w-3" /> Tasks</div>
            <div className="text-xl font-bold">{tasksData?.total || 0}</div>
            <div className="text-xs text-muted-foreground">{tasksData?.running || 0} active</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Database className="h-3 w-3" /> Storage</div>
            <div className="text-xl font-bold">{storage ? `${(storage.used_bytes / 1024).toFixed(0)}KB` : "—"}</div>
            <div className="text-xs text-muted-foreground">{storage?.usage_pct || 0}% used</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><AlertTriangle className="h-3 w-3" /> Faults</div>
            <div className="text-xl font-bold">{state?.faults?.total_faults || 0}</div>
            <div className="text-xs text-muted-foreground">{state?.faults?.unresolved || 0} unresolved</div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-lg border bg-card p-4 lg:col-span-2">
            <h3 className="font-semibold mb-3 flex items-center gap-2"><Server className="h-4 w-4" /> Compute Nodes</h3>
            {nodes.length === 0 ? (
              <p className="text-sm text-muted-foreground">No compute nodes registered. Nodes are auto-created when the simulation starts.</p>
            ) : (
              <div className="space-y-2">
                {nodes.map((n) => (
                  <div key={n.id} className="rounded-md border p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`h-2.5 w-2.5 rounded-full ${n.status === "online" ? "bg-green-400" : "bg-gray-400"}`} />
                        <span className="font-medium">{n.name}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          n.node_type === "gpu" ? "bg-purple-500/20 text-purple-400" :
                          n.node_type === "worker" ? "bg-blue-500/20 text-blue-400" :
                          "bg-gray-500/20 text-gray-400"
                        }`}>{n.node_type}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Cpu className="h-3 w-3" />{n.cpu_cores}c</span>
                        {n.gpu_count > 0 && <span className="flex items-center gap-1"><Gpu className="h-3 w-3" />{n.gpu_count}g</span>}
                        <span className="flex items-center gap-1"><Wifi className="h-3 w-3" />{n.network_latency_ms}ms</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <div className="flex items-center justify-between text-xs text-muted-foreground mb-0.5">
                          <span>CPU</span>
                          <span>{n.cpu_usage.toFixed(0)}%</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                          <div className={`h-full rounded-full ${n.cpu_usage > 70 ? "bg-red-500" : n.cpu_usage > 40 ? "bg-yellow-500" : "bg-green-500"}`}
                            style={{ width: `${n.cpu_usage}%` }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between text-xs text-muted-foreground mb-0.5">
                          <span>Memory</span>
                          <span>{n.memory_used_mb.toFixed(0)}/{n.memory_total_mb.toFixed(0)}MB</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                          <div className={`h-full rounded-full ${(n.memory_used_mb / n.memory_total_mb) > 0.7 ? "bg-red-500" : (n.memory_used_mb / n.memory_total_mb) > 0.4 ? "bg-yellow-500" : "bg-green-500"}`}
                            style={{ width: `${(n.memory_used_mb / n.memory_total_mb) * 100}%` }} />
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span>Tasks: {n.active_tasks}/{n.max_tasks}</span>
                      {n.capabilities?.length > 0 && (
                        <span>Capabilities: {n.capabilities.map(c => c.capability_type).join(", ")}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2"><Gauge className="h-4 w-4" /> Workload Balance</h3>
              {balance ? (
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Average Load: </span>
                    <span className={`font-medium ${balance.average_load > 70 ? "text-red-400" : balance.average_load > 40 ? "text-yellow-400" : "text-green-400"}`}>
                      {balance.average_load}%
                    </span>
                  </div>
                  {balance.loads.map((l) => (
                    <div key={l.node_id} className="rounded-md bg-secondary/30 p-2">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span>{l.name}</span>
                        <span>{l.load}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                        <div className={`h-full rounded-full ${l.load > 70 ? "bg-red-500" : l.load > 40 ? "bg-yellow-500" : "bg-green-500"}`}
                          style={{ width: `${l.load}%` }} />
                      </div>
                    </div>
                  ))}
                  {balance.high_load_nodes.length > 0 && (
                    <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3" />
                      {balance.high_load_nodes.length} node(s) overloaded
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No workload data available.</p>
              )}
            </div>

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2"><Shield className="h-4 w-4" /> Fault Status</h3>
              {state?.faults ? (
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Total Faults</span>
                    <span>{state.faults.total_faults}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Recovered</span>
                    <span className="text-green-400">{state.faults.recovered}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Unresolved</span>
                    <span className={state.faults.unresolved > 0 ? "text-red-400" : ""}>{state.faults.unresolved}</span>
                  </div>
                  {Object.entries(state.faults.by_severity).map(([sev, count]) => (
                    <div key={sev} className="flex items-center justify-between">
                      <span className="text-muted-foreground capitalize">{sev}</span>
                      <span className={sev === "critical" ? "text-red-400" : "text-yellow-400"}>{count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No fault data.</p>
              )}
            </div>

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2"><Database className="h-4 w-4" /> Storage</h3>
              {storage ? (
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Used</span>
                    <span>{(storage.used_bytes / 1024).toFixed(1)} KB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Available</span>
                    <span>{(storage.available_bytes / 1024).toFixed(1)} KB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Usage</span>
                    <span>{storage.usage_pct}%</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No storage data.</p>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2"><Boxes className="h-4 w-4" /> Partitions ({partitions.length})</h3>
            {partitions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No universe partitions created.</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {partitions.map((p) => (
                  <div key={p.id} className="flex items-center gap-2 rounded-md border p-2 text-sm">
                    <Globe className="h-4 w-4 text-muted-foreground shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{p.partition_key}</div>
                      <div className="text-xs text-muted-foreground">{p.partition_type} · {p.agent_count} agents</div>
                    </div>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      p.status === "assigned" ? "bg-green-500/20 text-green-400" :
                      p.status === "unassigned" ? "bg-yellow-500/20 text-yellow-400" :
                      "bg-gray-500/20 text-gray-400"
                    }`}>{p.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2"><Zap className="h-4 w-4" /> Recent Tasks ({tasks.length})</h3>
            {tasks.length === 0 ? (
              <p className="text-sm text-muted-foreground">No compute tasks scheduled.</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {tasks.slice(0, 10).map((t) => (
                  <div key={t.id} className="flex items-center gap-2 rounded-md border p-2 text-sm">
                    <span className={`h-2 w-2 shrink-0 rounded-full ${
                      t.status === "completed" ? "bg-green-400" :
                      t.status === "assigned" ? "bg-blue-400" :
                      t.status === "failed" ? "bg-red-400" :
                      "bg-gray-400"
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{t.task_type}</div>
                      <div className="text-xs text-muted-foreground">{t.priority} · {t.status}</div>
                    </div>
                    {t.progress > 0 && <span className="text-xs text-muted-foreground">{(t.progress * 100).toFixed(0)}%</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Cpu className="h-3 w-3" /> AI Reasoning</div>
            <div className="text-lg font-bold mt-1">{state?.reasoning?.active_reasoning || 0}</div>
            <div className="text-xs text-muted-foreground">active · {state?.reasoning?.gpu_nodes_available || 0} GPU nodes</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Wifi className="h-3 w-3" /> Sync</div>
            <div className="text-lg font-bold mt-1">{state?.sync?.total_syncs || 0}</div>
            <div className="text-xs text-muted-foreground">syncs · {(state?.sync?.total_data_bytes || 0) / 1024}KB transferred</div>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground"><Network className="h-3 w-3" /> Partitions</div>
            <div className="text-lg font-bold mt-1">{state?.partitions?.total || 0} / {state?.nodes?.total || 1}</div>
            <div className="text-xs text-muted-foreground">partitions per node</div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

// Inline GPU icon since lucide may not export it
function Gpu(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <rect x="6" y="8" width="4" height="4" />
      <rect x="12" y="8" width="4" height="4" />
      <rect x="6" y="14" width="4" height="4" />
      <rect x="12" y="14" width="4" height="4" />
    </svg>
  );
}
