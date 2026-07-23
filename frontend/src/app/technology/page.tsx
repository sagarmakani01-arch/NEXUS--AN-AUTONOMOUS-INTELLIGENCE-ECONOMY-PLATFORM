"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Cpu,
  Zap,
  Factory,
  Brain,
  Building2,
  Users,
  TrendingUp,
  RefreshCw,
  AlertTriangle,
  Clock,
  Target,
  Layers3,
  BarChart3,
} from "lucide-react";
import type {
  TechNode, TechEdge, TechDiscovery, TechDevelopment,
  ScientificOrg, CivilizationTechLevel, TechTimelineEvent,
  TechnologyEngineState, TechStats,
} from "@/types";

const API = "http://localhost:8000/api/v1/technology";

const CIVS = ["aetheria", "synthara", "quantos"];

const DOMAIN_COLORS: Record<string, string> = {
  "Artificial Intelligence": "bg-purple-500/15 text-purple-400",
  "Robotics": "bg-blue-500/15 text-blue-400",
  "Energy Systems": "bg-amber-500/15 text-amber-400",
  "Materials Science": "bg-cyan-500/15 text-cyan-400",
  "Computing": "bg-emerald-500/15 text-emerald-400",
  "Transportation": "bg-rose-500/15 text-rose-400",
  "Medicine": "bg-green-500/15 text-green-400",
  "Manufacturing": "bg-orange-500/15 text-orange-400",
  "Communication": "bg-sky-500/15 text-sky-400",
};

const STATUS_COLORS: Record<string, string> = {
  concept: "bg-gray-500/15 text-gray-400",
  prototype: "bg-blue-500/15 text-blue-400",
  testing: "bg-amber-500/15 text-amber-400",
  early_adoption: "bg-cyan-500/15 text-cyan-400",
  adoption: "bg-emerald-500/15 text-emerald-400",
  mature: "bg-green-500/15 text-green-400",
  obsolete: "bg-red-500/15 text-red-400",
  discovered: "bg-purple-500/15 text-purple-400",
};

const ERA_COLORS: Record<string, string> = {
  pre_industrial: "bg-gray-500/15 text-gray-400",
  early_industrial: "bg-amber-500/15 text-amber-400",
  industrial_age: "bg-orange-500/15 text-orange-400",
  digital_age: "bg-blue-500/15 text-blue-400",
  post_singularity: "bg-purple-500/15 text-purple-400",
};

function StatTile({ label, value, icon: Icon, color = "text-foreground" }: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color?: string;
}) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{label}</span>
        <Icon className={`h-3.5 w-3.5 ${color}`} />
      </div>
      <div className="text-xl font-bold tabular-nums tracking-tight">{value}</div>
    </div>
  );
}

function TechLevelCard({ level, civName }: { level: CivilizationTechLevel | null; civName: string }) {
  if (!level) return null;
  const dims = [
    { key: "computational_capability", label: "Computing", color: "bg-purple-500" },
    { key: "energy_capability", label: "Energy", color: "bg-amber-500" },
    { key: "manufacturing_capability", label: "Manufacturing", color: "bg-blue-500" },
    { key: "scientific_knowledge", label: "Science", color: "bg-emerald-500" },
    { key: "automation_level", label: "Automation", color: "bg-cyan-500" },
    { key: "infrastructure_level", label: "Infrastructure", color: "bg-rose-500" },
  ] as const;
  const eraClass = ERA_COLORS[level.current_era] || "bg-muted text-muted-foreground";

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{civName} Tech Level</CardTitle>
          <Badge className={`text-[10px] px-1.5 py-0 ${eraClass}`}>{level.current_era}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {dims.map((d) => (
            <div key={d.key} className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-24 truncate">{d.label}</span>
              <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
                <div className={`h-full rounded-full ${d.color}`} style={{ width: `${(level as unknown as Record<string, number>)[d.key]}%` }} />
              </div>
              <span className="text-[10px] font-mono tabular-nums w-8 text-right">{(level as unknown as Record<string, number>)[d.key].toFixed(0)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function TechNodeCard({ tech }: { tech: TechNode }) {
  const domainClass = DOMAIN_COLORS[tech.domain] || "bg-muted text-muted-foreground";
  const statusClass = STATUS_COLORS[tech.status] || "bg-muted text-muted-foreground";
  return (
    <div className="p-2 rounded border bg-card hover:border-foreground/20 transition-colors">
      <div className="flex items-start justify-between mb-1">
        <span className="text-xs font-medium truncate">{tech.name}</span>
        <Badge className={`text-[10px] px-1 py-0 ${statusClass}`}>{tech.status}</Badge>
      </div>
      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${domainClass}`}>{tech.domain}</span>
      <div className="flex items-center gap-2 mt-1.5 text-[10px] text-muted-foreground">
        <span>Lvl {tech.current_level.toFixed(0)}</span>
        <span>Impact {tech.impact_score.toFixed(0)}</span>
        <span>Diff {tech.difficulty_level.toFixed(0)}</span>
      </div>
    </div>
  );
}

function DiscoveryRow({ disc }: { disc: TechDiscovery }) {
  const diffClass = disc.difficulty === "hard" ? "text-red-400" : disc.difficulty === "medium" ? "text-amber-400" : "text-emerald-400";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <AlertTriangle className="h-3 w-3 text-purple-400 shrink-0" />
      <span className="text-xs font-medium flex-1 truncate">{disc.title}</span>
      <span className={`text-[10px] font-mono ${diffClass}`}>{disc.difficulty}</span>
      <span className="text-[10px] font-mono text-muted-foreground">{disc.method}</span>
    </div>
  );
}

function OrgRow({ org }: { org: ScientificOrg }) {
  const typeClass = org.org_type === "research_university" ? "bg-blue-500/15 text-blue-400"
    : org.org_type === "technology_company" ? "bg-emerald-500/15 text-emerald-400"
    : org.org_type === "government_lab" ? "bg-amber-500/15 text-amber-400"
    : "bg-muted text-muted-foreground";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <Building2 className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-xs font-medium flex-1 truncate">{org.name}</span>
      <Badge className={`text-[10px] px-1 py-0 ${typeClass}`}>{org.org_type}</Badge>
      <span className="text-[10px] font-mono tabular-nums">{org.reputation.toFixed(0)}</span>
    </div>
  );
}

function TimelineRow({ event }: { event: TechTimelineEvent }) {
  const typeClass = STATUS_COLORS[event.event_type] || "bg-muted text-muted-foreground";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <Clock className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-xs font-medium flex-1 truncate">{event.title}</span>
      <Badge className={`text-[10px] px-1 py-0 bg-secondary text-muted-foreground`}>{event.event_type}</Badge>
      <span className="text-[10px] font-mono text-muted-foreground">{event.impact_score.toFixed(0)}</span>
    </div>
  );
}

export default function TechnologyPage() {
  const [selectedCiv, setSelectedCiv] = useState<string>("aetheria");
  const [techs, setTechs] = useState<TechNode[]>([]);
  const [edges, setEdges] = useState<TechEdge[]>([]);
  const [discoveries, setDiscoveries] = useState<TechDiscovery[]>([]);
  const [orgs, setOrgs] = useState<ScientificOrg[]>([]);
  const [techLevel, setTechLevel] = useState<CivilizationTechLevel | null>(null);
  const [timeline, setTimeline] = useState<TechTimelineEvent[]>([]);
  const [engineState, setEngineState] = useState<TechnologyEngineState | null>(null);
  const [stats, setStats] = useState<TechStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [techRes, edgeRes, discRes, orgRes, levelRes, tlRes, engRes, statsRes] = await Promise.all([
        fetch(`${API}/graph`).then(r => r.json()),
        fetch(`${API}/graph/edges`).then(r => r.json()),
        fetch(`${API}/discoveries?civ_id=${selectedCiv}`).then(r => r.json()),
        fetch(`${API}/organizations?civ_id=${selectedCiv}`).then(r => r.json()),
        fetch(`${API}/tech-level/${selectedCiv}`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/timeline/${selectedCiv}`).then(r => r.json()),
        fetch(`${API}/engine/state`).then(r => r.json()),
        fetch(`${API}/stats`).then(r => r.json()),
      ]);
      setTechs(Array.isArray(techRes) ? techRes : []);
      setEdges(Array.isArray(edgeRes) ? edgeRes : []);
      setDiscoveries(Array.isArray(discRes) ? discRes : []);
      setOrgs(Array.isArray(orgRes) ? orgRes : []);
      setTechLevel(levelRes);
      setTimeline(Array.isArray(tlRes) ? tlRes : []);
      setEngineState(engRes);
      setStats(statsRes);
    } catch { /* backend offline */ }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const iv = setInterval(fetchData, 5000);
    return () => clearInterval(iv);
  }, [selectedCiv]);

  return (
    <AppLayout>
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Technology Evolution</h1>
            <p className="text-xs text-muted-foreground">Discovery, development, adoption, and obsolescence</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {CIVS.map((civ) => (
                <Button key={civ} size="sm" variant={selectedCiv === civ ? "default" : "outline"}
                  onClick={() => setSelectedCiv(civ)} className="h-7 px-3 text-xs capitalize">
                  {civ}
                </Button>
              ))}
            </div>
            <Button size="sm" variant="outline" onClick={fetchData} className="h-7 px-3">
              <RefreshCw className="mr-1 h-3 w-3" />Refresh
            </Button>
            <Badge className="text-xs font-mono">{engineState?.running ? "LIVE" : "IDLE"}</Badge>
          </div>
        </div>

        {engineState?.stats && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {Object.entries(engineState.stats).map(([key, value]) => (
              <div key={key} className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
                <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">
                  {key.replace(/_/g, " ")}
                </span>
                <span className="text-lg font-bold tabular-nums">{value}</span>
              </div>
            ))}
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <TechLevelCard level={techLevel} civName={selectedCiv} />
          </div>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1.5 text-xs">
                {stats && Object.entries(stats).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-muted-foreground">{key.replace(/_/g, " ")}</span>
                    <span className="font-mono font-bold tabular-nums">{value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <h2 className="text-sm font-semibold mb-3">Technology Graph ({techs.length} nodes, {edges.length} edges)</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            {techs.map((tech) => <TechNodeCard key={tech.id} tech={tech} />)}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3.5 w-3.5 text-purple-400" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Discoveries</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {discoveries.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No discoveries yet</p>
                ) : (
                  discoveries.map((d) => <DiscoveryRow key={d.id} disc={d} />)
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-3.5 w-3.5 text-blue-400" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Scientific Organizations</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {orgs.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No organizations yet</p>
                ) : (
                  orgs.map((o) => <OrgRow key={o.id} org={o} />)
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {timeline.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Technology Timeline</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {timeline.map((e) => <TimelineRow key={e.id} event={e} />)}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
