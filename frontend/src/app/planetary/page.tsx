"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Globe2,
  Mountain,
  Cloud,
  Droplets,
  TreePine,
  Factory,
  Building2,
  Users,
  TrendingUp,
  RefreshCw,
  Map,
  AlertTriangle,
  Leaf,
  Layers3,
} from "lucide-react";
import type {
  PlanetData, PlanetRegion, NaturalResource, SettlementData,
  EnvironmentalEventData, SustainabilityData, PlanetaryEngineState, PlanetaryStats,
} from "@/types";

const API = "http://localhost:8000/api/v1/planetary";

const TERRAIN_COLORS: Record<string, string> = {
  mountains: "bg-gray-500/15 text-gray-400",
  plains: "bg-emerald-500/15 text-emerald-400",
  forests: "bg-green-500/15 text-green-400",
  deserts: "bg-amber-500/15 text-amber-400",
  coastline: "bg-blue-500/15 text-blue-400",
  lakes: "bg-cyan-500/15 text-cyan-400",
  urban: "bg-purple-500/15 text-purple-400",
  wetlands: "bg-teal-500/15 text-teal-400",
};

const RESOURCE_ICONS: Record<string, React.ElementType> = {
  metals: Mountain, water: Droplets, energy: Factory,
  construction_materials: Building2, rare_minerals: Layers3,
  fertile_soil: Leaf, timber: TreePine,
};

function StatTile({ label, value, icon: Icon, color = "text-foreground" }: {
  label: string; value: string | number; icon: React.ElementType; color?: string;
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

function PlanetCard({ planet }: { planet: PlanetData }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold">{planet.name}</CardTitle>
          <Badge className="text-[10px] px-1.5 py-0 bg-secondary text-muted-foreground">{planet.status}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          <div className="flex justify-between"><span className="text-muted-foreground">Regions</span><span className="font-mono font-bold">{planet.region_count}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Avg Temp</span><span className="font-mono font-bold">{planet.average_temperature.toFixed(1)}°C</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Rainfall</span><span className="font-mono font-bold">{planet.average_rainfall.toFixed(0)}mm</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Env Health</span><span className="font-mono font-bold">{planet.environmental_health.toFixed(0)}%</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Resource Rich</span><span className="font-mono font-bold">{planet.resource_richness.toFixed(0)}%</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Age</span><span className="font-mono font-bold">{planet.age_years.toFixed(0)}y</span></div>
        </div>
      </CardContent>
    </Card>
  );
}

function RegionCard({ region }: { region: PlanetRegion }) {
  const terrainClass = TERRAIN_COLORS[region.terrain_type] || "bg-muted text-muted-foreground";
  return (
    <div className="p-2 rounded border bg-card hover:border-foreground/20 transition-colors">
      <div className="flex items-start justify-between mb-1">
        <span className="text-xs font-medium truncate">{region.name}</span>
        <Badge className={`text-[10px] px-1 py-0 ${terrainClass}`}>{region.terrain_type}</Badge>
      </div>
      <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
        <span>{region.climate_zone}</span>
        <span>Hab {region.habitability.toFixed(0)}%</span>
        {region.water_nearby && <Droplets className="h-2.5 w-2.5 text-blue-400" />}
        {region.fertile && <Leaf className="h-2.5 w-2.5 text-green-400" />}
      </div>
    </div>
  );
}

function ResourceRow({ resource }: { resource: NaturalResource }) {
  const Icon = RESOURCE_ICONS[resource.resource_type] || Layers3;
  const pct = resource.max_quantity > 0 ? (resource.quantity / resource.max_quantity) * 100 : 0;
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <Icon className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-xs font-medium flex-1 truncate">{resource.name}</span>
      <Badge className={`text-[10px] px-1 py-0 ${resource.renewable ? "bg-green-500/15 text-green-400" : "bg-muted text-muted-foreground"}`}>
        {resource.renewable ? "renew" : "finite"}
      </Badge>
      <div className="w-16 h-1.5 rounded-full bg-secondary overflow-hidden">
        <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] font-mono tabular-nums">{resource.quantity.toFixed(0)}</span>
    </div>
  );
}

function SettlementRow({ settlement }: { settlement: SettlementData }) {
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <Building2 className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-xs font-medium flex-1 truncate">{settlement.name}</span>
      <Badge className={`text-[10px] px-1 py-0 ${settlement.status === "growing" ? "bg-emerald-500/15 text-emerald-400" : "bg-muted text-muted-foreground"}`}>
        {settlement.status}
      </Badge>
      <span className="text-[10px] font-mono tabular-nums">{settlement.population}</span>
    </div>
  );
}

function EventRow({ event }: { event: EnvironmentalEventData }) {
  const sevClass = event.severity > 5 ? "text-red-400" : event.severity > 2 ? "text-amber-400" : "text-muted-foreground";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <AlertTriangle className={`h-3 w-3 shrink-0 ${sevClass}`} />
      <span className="text-xs font-medium flex-1 truncate">{event.title}</span>
      <Badge className="text-[10px] px-1 py-0 bg-secondary text-muted-foreground">{event.event_type}</Badge>
      <span className={`text-[10px] font-mono ${sevClass}`}>{event.severity.toFixed(1)}</span>
    </div>
  );
}

function SustainabilityCard({ data, civName }: { data: SustainabilityData | null; civName: string }) {
  if (!data) return null;
  const dims = [
    { key: "environmental_health", label: "Env Health", color: "bg-green-500" },
    { key: "renewable_usage_pct", label: "Renewable %", color: "bg-emerald-500" },
    { key: "infrastructure_efficiency", label: "Infra Eff", color: "bg-blue-500" },
    { key: "sustainability_score", label: "Sustainability", color: "bg-cyan-500" },
  ] as const;
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{civName} Sustainability</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {dims.map((d) => (
            <div key={d.key} className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-24 truncate">{d.label}</span>
              <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
                <div className={`h-full rounded-full ${d.color}`} style={{ width: `${(data as unknown as Record<string, number>)[d.key]}%` }} />
              </div>
              <span className="text-[10px] font-mono tabular-nums w-8 text-right">{(data as unknown as Record<string, number>)[d.key].toFixed(0)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function PlanetaryPage() {
  const [selectedCiv, setSelectedCiv] = useState<string>("aetheria");
  const [planet, setPlanet] = useState<PlanetData | null>(null);
  const [regions, setRegions] = useState<PlanetRegion[]>([]);
  const [resources, setResources] = useState<NaturalResource[]>([]);
  const [settlements, setSettlements] = useState<SettlementData[]>([]);
  const [events, setEvents] = useState<EnvironmentalEventData[]>([]);
  const [sustainability, setSustainability] = useState<SustainabilityData | null>(null);
  const [engineState, setEngineState] = useState<PlanetaryEngineState | null>(null);
  const [stats, setStats] = useState<PlanetaryStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [planetsRes, statsRes, engRes] = await Promise.all([
        fetch(`${API}/planets`).then(r => r.json()),
        fetch(`${API}/stats`).then(r => r.json()),
        fetch(`${API}/engine/state`).then(r => r.json()),
      ]);
      const planetList = Array.isArray(planetsRes) ? planetsRes : [];
      setStats(statsRes);
      setEngineState(engRes);

      if (planetList.length > 0) {
        const p = planetList[0];
        setPlanet(p);
        const [regRes, resRes, settRes, evRes, susRes] = await Promise.all([
          fetch(`${API}/regions/${p.id}`).then(r => r.json()),
          fetch(`${API}/resources/${p.id}`).then(r => r.json()),
          fetch(`${API}/settlements/${p.id}?civilization_id=${selectedCiv}`).then(r => r.json()),
          fetch(`${API}/events/${p.id}?limit=20`).then(r => r.json()),
          fetch(`${API}/sustainability/${p.id}?civilization_id=${selectedCiv}`).then(r => r.json()),
        ]);
        setRegions(Array.isArray(regRes) ? regRes : []);
        setResources(Array.isArray(resRes) ? resRes : []);
        setSettlements(Array.isArray(settRes) ? settRes : []);
        setEvents(Array.isArray(evRes) ? evRes : []);
        setSustainability(Array.isArray(susRes) && susRes.length > 0 ? susRes[0] : null);
      }
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
            <h1 className="text-lg font-semibold tracking-tight">Planetary Simulation</h1>
            <p className="text-xs text-muted-foreground">Geography, climate, resources, and environmental dynamics</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {["aetheria", "synthara", "quantos"].map((civ) => (
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
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-3">
            {Object.entries(engineState.stats).map(([key, value]) => (
              <div key={key} className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
                <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{key.replace(/_/g, " ")}</span>
                <span className="text-lg font-bold tabular-nums">{value}</span>
              </div>
            ))}
          </div>
        )}

        {planet && <PlanetCard planet={planet} />}

        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            <div>
              <h2 className="text-sm font-semibold mb-3">Regions ({regions.length})</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {regions.map((r) => <RegionCard key={r.id} region={r} />)}
              </div>
            </div>

            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Layers3 className="h-3.5 w-3.5 text-muted-foreground" />
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Natural Resources</CardTitle>
                  <Badge className="text-[10px] ml-auto">{resources.length}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                  {resources.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-4">No resources yet</p>
                  ) : (
                    resources.slice(0, 20).map((r) => <ResourceRow key={r.id} resource={r} />)
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <SustainabilityCard data={sustainability} civName={selectedCiv} />

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
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Settlements</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[200px] overflow-y-auto">
                {settlements.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No settlements yet</p>
                ) : (
                  settlements.map((s) => <SettlementRow key={s.id} settlement={s} />)
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Environmental Events</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[200px] overflow-y-auto">
                {events.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No events yet</p>
                ) : (
                  events.map((e) => <EventRow key={e.id} event={e} />)
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
