"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import {
  Puzzle,
  LayoutTemplate,
  FlaskConical,
  BookOpen,
  Download,
  Wrench,
  Users,
  Star,
  Package,
  FileDown,
  Globe,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PlatformState {
  initialized: boolean;
  plugins: { total: number; enabled: number; disabled: number; types: Record<string, number> };
  marketplace: { total: number; categories: Record<string, number>; average_rating: number; total_downloads: number };
  templates: number;
  scenarios: number;
  tools: number;
}

interface Plugin {
  id: string; name: string; display_name: string; description: string; author: string;
  version: string; type: string; target: string; enabled: boolean;
}

interface Module {
  id: string; name: string; display_name: string; description: string; author: string;
  version: string; category: string; downloads: number; rating: number;
}

interface Template {
  id: string; name: string; description: string; type: string; difficulty: string; objectives: string;
}

interface Dataset {
  id: string; name: string; type: string; format: string; records: number; size_bytes: number; exported_at: string;
}

export default function PlatformPage() {
  const [state, setState] = useState<PlatformState | null>(null);
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "plugins" | "templates" | "modules" | "datasets">("overview");

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  };

  useEffect(() => { loadPlatform(); }, []);

  const loadPlatform = async () => {
    try {
      const [s, p, m, t, d] = await Promise.all([
        fetch(`${API}/api/v1/platform/state`, { headers: authHeaders() }),
        fetch(`${API}/api/v1/platform/plugins`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/platform/modules`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/platform/templates`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/platform/export/datasets`, { headers: authHeaders() }).catch(() => null),
      ]);
      if (s.ok) setState(await s.json());
      if (p?.ok) { const d = await p.json(); setPlugins(d.plugins || []); }
      if (m?.ok) { const d = await m.json(); setModules(d.modules || []); }
      if (t?.ok) { const d = await t.json(); setTemplates(d.templates || []); }
      if (d?.ok) { const r = await d.json(); setDatasets(r.datasets || []); }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const togglePlugin = async (id: string, enabled: boolean) => {
    await fetch(`${API}/api/v1/platform/plugins/${id}/toggle?enabled=${!enabled}`, { method: "POST", headers: authHeaders() });
    loadPlatform();
  };

  if (loading) {
    return <AppLayout><div className="flex items-center justify-center h-64"><div className="text-muted-foreground">Loading platform...</div></div></AppLayout>;
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Puzzle className="h-8 w-8" />
              Platform & Extensions
            </h1>
            <p className="text-muted-foreground mt-1">Extend NEXUS with plugins, templates, modules, and developer tools</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          <div className="rounded-lg border bg-card p-3"><div className="text-xs text-muted-foreground">Plugins</div><div className="text-xl font-bold">{state?.plugins?.total || 0}</div><div className="text-xs text-muted-foreground">{state?.plugins?.enabled || 0} active</div></div>
          <div className="rounded-lg border bg-card p-3"><div className="text-xs text-muted-foreground">Templates</div><div className="text-xl font-bold">{state?.templates || 0}</div><div className="text-xs text-muted-foreground">Simulation starts</div></div>
          <div className="rounded-lg border bg-card p-3"><div className="text-xs text-muted-foreground">Modules</div><div className="text-xl font-bold">{state?.marketplace?.total || 0}</div><div className="text-xs text-muted-foreground">Avg rating: {state?.marketplace?.average_rating || 0}</div></div>
          <div className="rounded-lg border bg-card p-3"><div className="text-xs text-muted-foreground">Datasets</div><div className="text-xl font-bold">{datasets.length}</div><div className="text-xs text-muted-foreground">Exported records</div></div>
          <div className="rounded-lg border bg-card p-3"><div className="text-xs text-muted-foreground">Tools</div><div className="text-xl font-bold">{state?.tools || 0}</div><div className="text-xs text-muted-foreground">Developer tools</div></div>
        </div>

        <div className="flex gap-1 border-b">
          {(["overview", "plugins", "templates", "modules", "datasets"] as const).map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab ? "border-foreground text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
              }`}>
              {tab === "overview" && <Puzzle className="h-4 w-4" />}
              {tab === "plugins" && <Package className="h-4 w-4" />}
              {tab === "templates" && <LayoutTemplate className="h-4 w-4" />}
              {tab === "modules" && <Star className="h-4 w-4" />}
              {tab === "datasets" && <FileDown className="h-4 w-4" />}
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Platform Overview</h3>
              <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><Package className="h-4 w-4" /> Plugins</div>
                  <div className="text-xs text-muted-foreground mt-1">8 plugin types: economic, governance, reasoning, environmental, technology, visualization, physics, education</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><LayoutTemplate className="h-4 w-4" /> Templates</div>
                  <div className="text-xs text-muted-foreground mt-1">6 civilization templates: industrial, research, survival, aquatic, space, experimental</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><Star className="h-4 w-4" /> Module Marketplace</div>
                  <div className="text-xs text-muted-foreground mt-1">Community extensions across economy, governance, social, visualization, research, environmental categories</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><FlaskConical className="h-4 w-4" /> Workspaces</div>
                  <div className="text-xs text-muted-foreground mt-1">Research environments for creating, cloning civilizations, and comparing experiment outcomes</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><Wrench className="h-4 w-4" /> Developer Tools</div>
                  <div className="text-xs text-muted-foreground mt-1">Simulation debugger, event inspector, agent inspector, timeline explorer, performance monitor, API playground</div>
                </div>
                <div className="rounded-md border p-3">
                  <div className="flex items-center gap-2 text-sm font-medium"><Download className="h-4 w-4" /> Data Export</div>
                  <div className="text-xs text-muted-foreground mt-1">Export historical, economic, and population data in JSON and CSV formats</div>
                </div>
              </div>
            </div>

            {plugins.length > 0 && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3">Installed Plugins</h3>
                <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                  {plugins.map((pl) => (
                    <div key={pl.id} className="flex items-center gap-3 rounded-md border p-3">
                      <div className={`h-2 w-2 rounded-full ${pl.enabled ? "bg-green-400" : "bg-gray-400"}`} />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium">{pl.display_name || pl.name}</div>
                        <div className="text-xs text-muted-foreground">{pl.type} · v{pl.version}</div>
                      </div>
                      <span className="text-xs text-muted-foreground">{pl.enabled ? "Enabled" : "Disabled"}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "plugins" && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3">Plugin Manager</h3>
            {plugins.length === 0 ? (
              <p className="text-muted-foreground text-sm">No plugins installed. Plugins are auto-installed when the simulation starts.</p>
            ) : (
              <div className="space-y-2">
                {plugins.map((pl) => (
                  <div key={pl.id} className="flex items-center gap-3 rounded-md border p-3 hover:bg-secondary/50">
                    <Package className="h-5 w-5 text-muted-foreground shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium">{pl.display_name || pl.name}</div>
                      <div className="text-xs text-muted-foreground">{pl.description}</div>
                      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                        <span>Type: {pl.type}</span>
                        <span>Target: {pl.target}</span>
                        <span>v{pl.version}</span>
                      </div>
                    </div>
                    <button onClick={() => togglePlugin(pl.id, pl.enabled)}
                      className={`rounded-md px-3 py-1 text-xs font-medium ${
                        pl.enabled ? "bg-red-500/20 text-red-400 hover:bg-red-500/30" : "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                      }`}>
                      {pl.enabled ? "Disable" : "Enable"}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "templates" && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3">Simulation Templates</h3>
            {templates.length === 0 ? (
              <p className="text-muted-foreground text-sm">No templates available. Templates are seeded on platform initialization.</p>
            ) : (
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                {templates.map((t) => (
                  <div key={t.id} className="rounded-md border p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Globe className="h-5 w-5 text-muted-foreground" />
                      <span className="font-medium">{t.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">{t.description}</p>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 font-medium ${
                        t.difficulty === "easy" ? "bg-green-500/20 text-green-400" :
                        t.difficulty === "hard" ? "bg-red-500/20 text-red-400" :
                        "bg-yellow-500/20 text-yellow-400"
                      }`}>{t.difficulty}</span>
                      <span className="text-muted-foreground">{t.type}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "modules" && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3">Module Marketplace</h3>
            {modules.length === 0 ? (
              <p className="text-muted-foreground text-sm">No modules in the marketplace yet. Community modules are seeded on platform initialization.</p>
            ) : (
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                {modules.map((m) => (
                  <div key={m.id} className="rounded-md border p-3 hover:bg-secondary/50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className="font-medium">{m.display_name || m.name}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">v{m.version}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{m.description}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span>By {m.author}</span>
                      <span>{m.category}</span>
                      <span className="flex items-center gap-1"><Star className="h-3 w-3" />{m.rating}</span>
                      <span className="flex items-center gap-1"><Download className="h-3 w-3" />{m.downloads}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "datasets" && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-3">Exported Datasets</h3>
            {datasets.length === 0 ? (
              <p className="text-muted-foreground text-sm">No datasets exported yet. Use the export API to create datasets from simulation data.</p>
            ) : (
              <div className="space-y-2">
                {datasets.map((d) => (
                  <div key={d.id} className="flex items-center gap-3 rounded-md border p-3 hover:bg-secondary/50">
                    <FileDown className="h-5 w-5 text-muted-foreground shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium">{d.name}</div>
                      <div className="text-xs text-muted-foreground">{d.type} · {d.format} · {d.records} records</div>
                    </div>
                    <span className="text-xs text-muted-foreground">{(d.size_bytes / 1024).toFixed(1)} KB</span>
                    <span className="text-xs text-muted-foreground">{d.exported_at ? new Date(d.exported_at).toLocaleDateString() : ""}</span>
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
