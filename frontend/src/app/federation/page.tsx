"use client";

import { useEffect, useState, useRef } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Globe2,
  Users,
  Brain,
  TrendingUp,
  Handshake,
  ArrowRightLeft,
  MessageSquare,
  Activity,
  RefreshCw,
  Shield,
  Landmark,
  GitMerge,
  ArrowRight,
} from "lucide-react";
import type {
  Civilization,
  FederationDashboard,
  DiplomaticRelation,
  TradeAgreement,
  FederationMigration,
  CivilizationHistory,
  DiplomacyMap,
} from "@/types";

const API = "http://localhost:8000/api/v1/federation";

const GOV_COLORS: Record<string, string> = {
  democracy: "bg-blue-500/15 text-blue-400",
  technocracy: "bg-purple-500/15 text-purple-400",
  meritocracy: "bg-emerald-500/15 text-emerald-400",
  theocracy: "bg-amber-500/15 text-amber-400",
  republic: "bg-cyan-500/15 text-cyan-400",
};

const STATUS_COLORS: Record<string, string> = {
  ally: "bg-emerald-500/15 text-emerald-400",
  friendly: "bg-blue-500/15 text-blue-400",
  neutral: "bg-muted text-muted-foreground",
  tense: "bg-amber-500/15 text-amber-400",
  hostile: "bg-red-500/15 text-red-400",
};

const TRADE_COLORS: Record<string, string> = {
  resource: "bg-emerald-500/15 text-emerald-400",
  technology: "bg-purple-500/15 text-purple-400",
  knowledge: "bg-blue-500/15 text-blue-400",
  military: "bg-red-500/15 text-red-400",
  cultural: "bg-amber-500/15 text-amber-400",
  financial: "bg-cyan-500/15 text-cyan-400",
};

const TRUST_BAR: Record<string, string> = {
  low: "bg-red-500",
  medium: "bg-amber-500",
  high: "bg-emerald-500",
};

function trustLevel(trust: number): string {
  if (trust < 40) return "low";
  if (trust < 70) return "medium";
  return "high";
}

function StatTile({
  label,
  value,
  icon: Icon,
  color = "text-foreground",
}: {
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

function CivilizationCard({ civ }: { civ: Civilization }) {
  const govClass = GOV_COLORS[civ.government_type] || "bg-muted text-muted-foreground";
  return (
    <Card className="hover:border-foreground/20 transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-semibold">{civ.name}</CardTitle>
            <span className={`inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full font-medium ${govClass}`}>
              {civ.government_type}
            </span>
          </div>
          <Badge className={`text-[10px] px-1.5 py-0 ${civ.status === "thriving" ? "bg-emerald-500/15 text-emerald-400" : "bg-muted text-muted-foreground"}`}>
            {civ.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Population</span>
            <span className="font-mono font-bold tabular-nums">{civ.population.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Economy</span>
            <span className="font-mono font-bold tabular-nums">{civ.economic_power}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Technology</span>
            <span className="font-mono font-bold tabular-nums">{civ.technology_level}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Happiness</span>
            <span className="font-mono font-bold tabular-nums">{civ.happiness.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Military</span>
            <span className="font-mono font-bold tabular-nums">{civ.military_strength}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Reputation</span>
            <span className="font-mono font-bold tabular-nums">{civ.reputation.toFixed(1)}</span>
          </div>
        </div>
        {civ.priorities.length > 0 && (
          <div className="mt-2 pt-2 border-t">
            <div className="flex flex-wrap gap-1">
              {civ.priorities.map((p) => (
                <span key={p} className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DiplomacyEdge({ relation, civNames }: { relation: DiplomaticRelation; civNames: Record<string, string> }) {
  const statusClass = STATUS_COLORS[relation.status] || "bg-muted text-muted-foreground";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <span className="text-xs font-medium truncate max-w-[100px]">{civNames[relation.civilization_a_id] || relation.civilization_a_id.slice(0, 8)}</span>
      <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-xs font-medium truncate max-w-[100px]">{civNames[relation.civilization_b_id] || relation.civilization_b_id.slice(0, 8)}</span>
      <div className="flex-1" />
      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${statusClass}`}>{relation.status}</span>
      <div className="w-16 h-1.5 rounded-full bg-secondary overflow-hidden">
        <div className={`h-full rounded-full ${TRUST_BAR[trustLevel(relation.trust_score)]}`} style={{ width: `${relation.trust_score}%` }} />
      </div>
      <span className="text-[10px] font-mono text-muted-foreground w-6 text-right">{Math.round(relation.trust_score)}%</span>
    </div>
  );
}

function TradeRow({ trade, civNames }: { trade: TradeAgreement; civNames: Record<string, string> }) {
  const typeClass = TRADE_COLORS[trade.trade_type] || "bg-muted text-muted-foreground";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${typeClass}`}>{trade.trade_type}</span>
      <span className="text-xs font-medium truncate max-w-[80px]">{civNames[trade.civilization_a_id] || "???"}</span>
      <ArrowRightLeft className="h-3 w-3 text-muted-foreground shrink-0" />
      <span className="text-xs font-medium truncate max-w-[80px]">{civNames[trade.civilization_b_id] || "???"}</span>
      <div className="flex-1" />
      <span className="text-[10px] text-muted-foreground truncate max-w-[60px]">{trade.resource_offered}→{trade.resource_requested}</span>
      <span className="text-[10px] font-mono font-bold tabular-nums">{trade.total_volume}</span>
    </div>
  );
}

function MigrationRow({ migration, civNames }: { migration: FederationMigration; civNames: Record<string, string> }) {
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <span className="text-xs font-mono truncate max-w-[70px]">{migration.agent_id.slice(0, 8)}</span>
      <span className="text-xs text-muted-foreground">→</span>
      <span className="text-xs font-medium truncate max-w-[80px]">{civNames[migration.destination_civilization_id] || "???"}</span>
      <div className="flex-1" />
      <Badge className="text-[10px] px-1.5 py-0 bg-secondary text-muted-foreground">{migration.reason}</Badge>
      <span className="text-[10px] font-mono tabular-nums">{migration.skill_value.toFixed(1)}</span>
    </div>
  );
}

function HistoryRow({ event }: { event: CivilizationHistory }) {
  return (
    <div className="flex items-start gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <Activity className="h-3 w-3 text-muted-foreground mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium truncate">{event.title}</p>
        {event.description && <p className="text-[10px] text-muted-foreground truncate">{event.description}</p>}
      </div>
      <Badge className="text-[10px] px-1.5 py-0 bg-secondary text-muted-foreground shrink-0">{event.event_type}</Badge>
    </div>
  );
}

function DiplomacyDiagram({ map, civNames }: { map: DiplomacyMap | null; civNames: Record<string, string> }) {
  const svgRef = useRef<SVGSVGElement>(null);
  if (!map || map.nodes.length === 0) {
    return (
      <div className="h-[200px] flex items-center justify-center text-xs text-muted-foreground">
        No diplomacy data yet
      </div>
    );
  }

  const n = map.nodes.length;
  const cx = 150, cy = 90, r = 70;
  const positions: Record<string, { x: number; y: number }> = {};
  map.nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    positions[node.id] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });

  return (
    <svg ref={svgRef} viewBox="0 0 300 180" className="w-full h-[200px]">
      {map.edges.map((edge, i) => {
        const a = positions[edge.source];
        const b = positions[edge.target];
        if (!a || !b) return null;
        const strokeColor = STATUS_COLORS[edge.status]?.includes("emerald") ? "#22c55e"
          : STATUS_COLORS[edge.status]?.includes("blue") ? "#3b82f6"
          : STATUS_COLORS[edge.status]?.includes("amber") ? "#f59e0b"
          : STATUS_COLORS[edge.status]?.includes("red") ? "#ef4444"
          : "#6b7280";
        return (
          <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
            stroke={strokeColor} strokeWidth={1.5} strokeOpacity={0.6} />
        );
      })}
      {map.nodes.map((node) => {
        const p = positions[node.id];
        if (!p) return null;
        const popRadius = Math.max(8, Math.min(20, node.population / 100));
        return (
          <g key={node.id}>
            <circle cx={p.x} cy={p.y} r={popRadius} fill="#3b82f6" fillOpacity={0.2} stroke="#3b82f6" strokeWidth={1.5} />
            <text x={p.x} y={p.y + popRadius + 10} textAnchor="middle" fontSize={7} fill="#a1a1aa">
              {civNames[node.id] || node.id.slice(0, 6)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export default function FederationPage() {
  const [dashboard, setDashboard] = useState<FederationDashboard | null>(null);
  const [relations, setRelations] = useState<DiplomaticRelation[]>([]);
  const [trades, setTrades] = useState<TradeAgreement[]>([]);
  const [migrations, setMigrations] = useState<FederationMigration[]>([]);
  const [history, setHistory] = useState<CivilizationHistory[]>([]);
  const [diploMap, setDiploMap] = useState<DiplomacyMap | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [dashRes, relRes, tradeRes, migRes, histRes, mapRes] = await Promise.all([
        fetch(`${API}/dashboard`).then(r => r.json()),
        fetch(`${API}/diplomacy`).then(r => r.json()),
        fetch(`${API}/trade`).then(r => r.json()),
        fetch(`${API}/migration`).then(r => r.json()),
        fetch(`${API}/history/civ-1?limit=30`).then(r => r.json()),
        fetch(`${API}/diplomacy/map`).then(r => r.json()),
      ]);
      setDashboard(dashRes);
      setRelations(relRes);
      setTrades(tradeRes);
      setMigrations(migRes);
      setHistory(histRes);
      setDiploMap(mapRes);
    } catch { /* backend offline */ }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const iv = setInterval(fetchData, 3000);
    return () => clearInterval(iv);
  }, []);

  const civNames: Record<string, string> = {};
  dashboard?.civilizations?.forEach(c => { civNames[c.id] = c.name; });

  return (
    <AppLayout>
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Federation Overview</h1>
            <p className="text-xs text-muted-foreground">Multi-civilization diplomacy, trade & knowledge exchange</p>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={fetchData} className="h-7 px-3">
              <RefreshCw className="mr-1 h-3 w-3" />
              Refresh
            </Button>
            <Badge className="text-xs font-mono uppercase">
              {dashboard?.civilization_count ?? 0} civs
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <StatTile label="Civilizations" value={dashboard?.civilization_count ?? 0} icon={Globe2} color="text-blue-500" />
          <StatTile label="Total Population" value={(dashboard?.total_population ?? 0).toLocaleString()} icon={Users} />
          <StatTile label="Avg Technology" value={(dashboard?.average_technology ?? 0).toFixed(1)} icon={Brain} color="text-purple-500" />
          <StatTile label="Avg Economy" value={(dashboard?.average_economy ?? 0).toFixed(1)} icon={TrendingUp} color="text-emerald-500" />
          <StatTile label="Diplomatic Links" value={dashboard?.federation_stats?.diplomatic_relations ?? 0} icon={Handshake} color="text-amber-500" />
          <StatTile label="Active Trades" value={dashboard?.federation_stats?.trade_agreements ?? 0} icon={ArrowRightLeft} color="text-cyan-500" />
        </div>

        <div>
          <h2 className="text-sm font-semibold mb-3">Civilizations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {dashboard?.civilizations?.map((civ) => (
              <CivilizationCard key={civ.id} civ={civ} />
            ))}
            {(!dashboard?.civilizations || dashboard.civilizations.length === 0) && (
              <Card className="col-span-full">
                <CardContent className="py-8 text-center text-xs text-muted-foreground">
                  {loading ? "Loading civilizations..." : "No civilizations yet. Start the simulation to generate the universe."}
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Handshake className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Diplomacy Map</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <DiplomacyDiagram map={diploMap} civNames={civNames} />
              <div className="space-y-0.5 mt-2">
                {relations.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-2">No diplomatic relations yet</p>
                ) : (
                  relations.slice(0, 8).map((r) => (
                    <DiplomacyEdge key={r.id} relation={r} civNames={civNames} />
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <ArrowRightLeft className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Trade Agreements</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5">
                {trades.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-8">No trade agreements yet</p>
                ) : (
                  trades.slice(0, 10).map((t) => (
                    <TradeRow key={t.id} trade={t} civNames={civNames} />
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <GitMerge className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Recent Migrations</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5">
                {migrations.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-8">No migrations yet</p>
                ) : (
                  migrations.slice(0, 10).map((m) => (
                    <MigrationRow key={m.id} migration={m} civNames={civNames} />
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Federation History</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[300px] overflow-y-auto">
                {history.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-8">No history yet</p>
                ) : (
                  history.slice(0, 15).map((e) => (
                    <HistoryRow key={e.id} event={e} />
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {dashboard?.rankings && (
          <div className="grid md:grid-cols-3 gap-4">
            {(["technology", "economic", "population"] as const).map((key) => (
              <Card key={key}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    {key === "technology" ? "Technology Leaders" : key === "economic" ? "Economic Power" : "Population"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1.5">
                    {dashboard.rankings[key].map((entry, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <span className="text-xs font-mono text-muted-foreground w-4">{i + 1}.</span>
                        <span className="text-xs font-medium flex-1 truncate">{entry.name}</span>
                        <div className="w-16 h-1.5 rounded-full bg-secondary overflow-hidden">
                          <div className="h-full rounded-full bg-blue-500" style={{
                            width: `${Math.min(100, (entry.value / Math.max(...dashboard.rankings[key].map(e => e.value || 1))) * 100)}%`
                          }} />
                        </div>
                        <span className="text-[10px] font-mono font-bold tabular-nums">{entry.value.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
