"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Heart,
  Scale,
  BookOpen,
  Building2,
  Users,
  Brain,
  Clock,
  RefreshCw,
  Shield,
  Lightbulb,
  Globe2,
  TrendingUp,
} from "lucide-react";
import type {
  CulturalIdentity,
  ValueSystem,
  Institution,
  Tradition,
  CivilizationCommunity,
  CollectiveMemory,
  SocialDynamics,
  ReputationEntry,
  CivilizationIdentityScore,
  CultureEngineState,
} from "@/types";

const API = "http://localhost:8000/api/v1/culture";

const CIVS = ["aetheria", "synthara", "quantos"];

const VALUE_LABELS: Record<string, string> = {
  innovation: "Innovation",
  cooperation: "Cooperation",
  competition: "Competition",
  education: "Education",
  efficiency: "Efficiency",
  sustainability: "Sustainability",
  exploration: "Exploration",
  security: "Security",
  transparency: "Transparency",
};

const VALUE_COLORS: Record<string, string> = {
  innovation: "text-purple-400",
  cooperation: "text-blue-400",
  competition: "text-red-400",
  education: "text-emerald-400",
  efficiency: "text-amber-400",
  sustainability: "text-green-400",
  exploration: "text-cyan-400",
  security: "text-orange-400",
  transparency: "text-pink-400",
};

const INST_COLORS: Record<string, string> = {
  academy: "bg-blue-500/15 text-blue-400",
  scientific_council: "bg-purple-500/15 text-purple-400",
  professional_association: "bg-emerald-500/15 text-emerald-400",
  standards_committee: "bg-amber-500/15 text-amber-400",
  historical_archive: "bg-cyan-500/15 text-cyan-400",
  council_of_elders: "bg-rose-500/15 text-rose-400",
  research_institute: "bg-violet-500/15 text-violet-400",
  cultural_foundation: "bg-fuchsia-500/15 text-fuchsia-400",
  education_board: "bg-teal-500/15 text-teal-400",
  trade_guild: "bg-yellow-500/15 text-yellow-400",
  innovation_lab: "bg-indigo-500/15 text-indigo-400",
  library: "bg-sky-500/15 text-sky-400",
};

function ValueBar({ name, value }: { name: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`text-xs font-medium w-24 truncate ${VALUE_COLORS[name] || "text-muted-foreground"}`}>
        {VALUE_LABELS[name] || name}
      </span>
      <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
        <div className="h-full rounded-full bg-current opacity-60" style={{ width: `${value}%` }} />
      </div>
      <span className="text-[10px] font-mono tabular-nums w-8 text-right">{value.toFixed(0)}</span>
    </div>
  );
}

function IdentityCard({ identity, civName }: { identity: CulturalIdentity | null; civName: string }) {
  if (!identity) return null;
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{civName} Identity</CardTitle>
          <Badge className="text-[10px] px-1.5 py-0 bg-secondary text-muted-foreground">
            {identity.identity_strength.toFixed(0)}% strength
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {identity.social_norms.length > 0 && (
          <div className="mb-2">
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Norms</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {identity.social_norms.map((n) => (
                <span key={n} className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">{n}</span>
              ))}
            </div>
          </div>
        )}
        {identity.long_term_goals.length > 0 && (
          <div className="mb-2">
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Goals</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {identity.long_term_goals.map((g) => (
                <span key={g} className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400">{g}</span>
              ))}
            </div>
          </div>
        )}
        {identity.historical_symbols.length > 0 && (
          <div>
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Symbols</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {identity.historical_symbols.map((s) => (
                <span key={s} className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">{s}</span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function IdentityScoreCard({ score, civName }: { score: CivilizationIdentityScore | null; civName: string }) {
  if (!score) return null;
  const dims = [
    { key: "knowledge_orientation", label: "Knowledge", color: "bg-blue-500" },
    { key: "innovation_orientation", label: "Innovation", color: "bg-purple-500" },
    { key: "economic_stability", label: "Economy", color: "bg-emerald-500" },
    { key: "social_cohesion", label: "Cohesion", color: "bg-amber-500" },
    { key: "institutional_strength", label: "Institutions", color: "bg-cyan-500" },
    { key: "adaptability", label: "Adaptability", color: "bg-rose-500" },
  ] as const;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{civName} Identity Score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {dims.map((d) => (
            <div key={d.key} className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-20 truncate">{d.label}</span>
              <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
                <div className={`h-full rounded-full ${d.color}`} style={{ width: `${(score as unknown as Record<string, number>)[d.key]}%` }} />
              </div>
              <span className="text-[10px] font-mono tabular-nums w-8 text-right">{(score as unknown as Record<string, number>)[d.key].toFixed(0)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function DynamicsCard({ dynamics, civName }: { dynamics: SocialDynamics | null; civName: string }) {
  if (!dynamics) return null;
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{civName} Social Dynamics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Collaboration</span>
            <span className="font-mono font-bold">{dynamics.collaboration_score.toFixed(1)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Competition</span>
            <span className="font-mono font-bold">{dynamics.competition_score.toFixed(1)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Trust</span>
            <span className="font-mono font-bold">{dynamics.trust_level.toFixed(1)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Knowledge Sharing</span>
            <span className="font-mono font-bold">{dynamics.knowledge_sharing_score.toFixed(1)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function InstitutionRow({ inst }: { inst: Institution }) {
  const colorClass = INST_COLORS[inst.institution_type] || "bg-muted text-muted-foreground";
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${colorClass}`}>{inst.institution_type}</span>
      <span className="text-xs font-medium flex-1 truncate">{inst.name}</span>
      <span className="text-[10px] font-mono tabular-nums">{inst.membership_count}</span>
      <div className="w-12 h-1.5 rounded-full bg-secondary overflow-hidden">
        <div className="h-full rounded-full bg-blue-500" style={{ width: `${inst.strength}%` }} />
      </div>
    </div>
  );
}

function CommunityRow({ comm }: { comm: CivilizationCommunity }) {
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-muted-foreground">{comm.community_type}</span>
      <span className="text-xs font-medium flex-1 truncate">{comm.name}</span>
      <span className="text-[10px] font-mono tabular-nums">{comm.member_count}</span>
      {comm.growth_rate > 0 && (
        <span className="text-[10px] font-mono text-emerald-400">+{comm.growth_rate.toFixed(1)}%</span>
      )}
    </div>
  );
}

function MemoryRow({ mem }: { mem: CollectiveMemory }) {
  return (
    <div className="flex items-start gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <Clock className="h-3 w-3 text-muted-foreground mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium truncate">{mem.title}</p>
        {mem.description && <p className="text-[10px] text-muted-foreground truncate">{mem.description}</p>}
      </div>
      <Badge className="text-[10px] px-1.5 py-0 bg-secondary text-muted-foreground shrink-0">{mem.event_type}</Badge>
    </div>
  );
}

function ReputationRow({ entry }: { entry: ReputationEntry }) {
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/50 transition-colors">
      <span className="text-[10px] font-mono truncate max-w-[70px]">{entry.entity_id.slice(0, 8)}</span>
      <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">{entry.entity_type}</span>
      <div className="flex-1" />
      <span className="text-[10px] font-mono font-bold tabular-nums">{entry.influence_score.toFixed(1)}</span>
      <span className="text-[10px] text-muted-foreground">{entry.contribution_count}x</span>
    </div>
  );
}

export default function CulturePage() {
  const [selectedCiv, setSelectedCiv] = useState<string>("aetheria");
  const [identity, setIdentity] = useState<CulturalIdentity | null>(null);
  const [values, setValues] = useState<ValueSystem | null>(null);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [traditions, setTraditions] = useState<Tradition[]>([]);
  const [communities, setCommunities] = useState<CivilizationCommunity[]>([]);
  const [memories, setMemories] = useState<CollectiveMemory[]>([]);
  const [dynamics, setDynamics] = useState<SocialDynamics | null>(null);
  const [reputation, setReputation] = useState<ReputationEntry[]>([]);
  const [identityScore, setIdentityScore] = useState<CivilizationIdentityScore | null>(null);
  const [engineState, setEngineState] = useState<CultureEngineState | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [identRes, valRes, instRes, tradRes, commRes, memRes, dynRes, repRes, scoreRes, engRes] = await Promise.all([
        fetch(`${API}/identity/${selectedCiv}`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/values/${selectedCiv}`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/institutions?civ_id=${selectedCiv}`).then(r => r.json()),
        fetch(`${API}/traditions?civ_id=${selectedCiv}`).then(r => r.json()),
        fetch(`${API}/communities?civ_id=${selectedCiv}`).then(r => r.json()),
        fetch(`${API}/memory/${selectedCiv}?limit=20`).then(r => r.json()),
        fetch(`${API}/dynamics/${selectedCiv}`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/reputation/${selectedCiv}?limit=15`).then(r => r.json()),
        fetch(`${API}/evolution/${selectedCiv}`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/engine/state`).then(r => r.json()),
      ]);
      setIdentity(identRes);
      setValues(valRes);
      setInstitutions(Array.isArray(instRes) ? instRes : []);
      setTraditions(Array.isArray(tradRes) ? tradRes : []);
      setCommunities(Array.isArray(commRes) ? commRes : []);
      setMemories(Array.isArray(memRes) ? memRes : []);
      setDynamics(dynRes);
      setReputation(Array.isArray(repRes) ? repRes : []);
      setIdentityScore(scoreRes);
      setEngineState(engRes);
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
            <h1 className="text-lg font-semibold tracking-tight">Culture & Social Evolution</h1>
            <p className="text-xs text-muted-foreground">Values, traditions, institutions, and collective identity</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {CIVS.map((civ) => (
                <Button
                  key={civ}
                  size="sm"
                  variant={selectedCiv === civ ? "default" : "outline"}
                  onClick={() => setSelectedCiv(civ)}
                  className="h-7 px-3 text-xs capitalize"
                >
                  {civ}
                </Button>
              ))}
            </div>
            <Button size="sm" variant="outline" onClick={fetchData} className="h-7 px-3">
              <RefreshCw className="mr-1 h-3 w-3" />
              Refresh
            </Button>
            <Badge className="text-xs font-mono">
              {engineState?.running ? "LIVE" : "IDLE"}
            </Badge>
          </div>
        </div>

        {engineState?.stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
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
          <div className="lg:col-span-2 space-y-4">
            {identity && <IdentityCard identity={identity} civName={selectedCiv} />}

            {values && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Core Values</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(VALUE_LABELS).map(([key]) => (
                      <ValueBar key={key} name={key} value={(values as unknown as Record<string, number>)[key] || 50} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="space-y-4">
            <IdentityScoreCard score={identityScore} civName={selectedCiv} />
            <DynamicsCard dynamics={dynamics} civName={selectedCiv} />
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Institutions</CardTitle>
                <Badge className="text-[10px] ml-auto">{institutions.length}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {institutions.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No institutions yet</p>
                ) : (
                  institutions.map((i) => <InstitutionRow key={i.id} inst={i} />)
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Users className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Communities</CardTitle>
                <Badge className="text-[10px] ml-auto">{communities.length}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {communities.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No communities yet</p>
                ) : (
                  communities.map((c) => <CommunityRow key={c.id} comm={c} />)
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Collective Memory</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {memories.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No memories yet</p>
                ) : (
                  memories.map((m) => <MemoryRow key={m.id} mem={m} />)
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Reputation & Influence</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-0.5 max-h-[250px] overflow-y-auto">
                {reputation.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No reputation data yet</p>
                ) : (
                  reputation.map((r) => <ReputationRow key={r.id} entry={r} />)
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {traditions.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <BookOpen className="h-3.5 w-3.5 text-muted-foreground" />
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Traditions</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {traditions.map((t) => (
                  <div key={t.id} className="p-2 rounded border bg-card">
                    <p className="text-xs font-medium truncate">{t.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className="text-[10px] px-1 py-0 bg-secondary text-muted-foreground">{t.frequency}</Badge>
                      <span className="text-[10px] font-mono text-muted-foreground">{t.impact_score.toFixed(0)}pts</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
