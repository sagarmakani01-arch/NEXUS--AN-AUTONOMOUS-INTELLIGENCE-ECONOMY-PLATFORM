"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import {
  Globe2, Users, BookOpen, Lightbulb, Atom, Eye, History,
  Sparkles, TreePine, CloudSun, ScrollText, Star, BrainCircuit,
  AlertCircle, Sprout, Building, Factory, Rocket,
} from "lucide-react";
import type {
  GenesisCivilizationProfile, GenesisEngineState,
  GenesisCivilization, GenesisAgent, BeliefSystem, PhilosophyData,
  GenesisDiscovery, EraRecord, KnowledgeDomain, AwarenessStatus,
  CreatorInteractionData, HistoricalInterpretationData,
} from "@/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ERA_ICONS: Record<string, typeof Sprout> = {
  primitive: Sprout, settlement: Building, agricultural: TreePine,
  industrial: Factory, scientific: Atom, space: Rocket,
};

const AWARENESS_COLORS = ["bg-gray-500", "bg-blue-500", "bg-purple-500", "bg-amber-500", "bg-red-500"];

export default function GenesisPage() {
  const [state, setState] = useState<GenesisEngineState | null>(null);
  const [selectedCiv, setSelectedCiv] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "beliefs" | "discoveries" | "timeline" | "awareness" | "history">("overview");

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  };

  useEffect(() => { loadGenesis(); }, []);

  const loadGenesis = async () => {
    try {
      const r = await fetch(`${API}/api/v1/genesis/state`, { headers: authHeaders() });
      if (r.ok) {
        const data = await r.json();
        setState(data);
        const ids = Object.keys(data.civilizations || {});
        if (ids.length > 0 && !selectedCiv) setSelectedCiv(ids[0]);
      }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const profile: GenesisCivilizationProfile | null =
    selectedCiv && state?.civilizations ? (state.civilizations[selectedCiv] ?? null) : null;
  const civ = profile?.civilization;
  const agents = profile?.agents || [];
  const beliefs = profile?.beliefs || [];
  const philosophies = profile?.philosophies || [];
  const discoveries = profile?.discoveries || [];
  const eras = profile?.eras || [];
  const knowledge = profile?.knowledge_domains || [];
  const awareness = profile?.awareness;

  const [interactions, setInteractions] = useState<CreatorInteractionData[]>([]);
  const [interpretations, setInterpretations] = useState<HistoricalInterpretationData[]>([]);

  useEffect(() => {
    if (selectedCiv) {
      fetch(`${API}/api/v1/genesis/civilizations/${selectedCiv}/history`, { headers: authHeaders() })
        .then(r => r.json()).then(d => {
          setInteractions(d.interactions || []);
          setInterpretations(d.interpretations || []);
        }).catch(() => {});
    }
  }, [selectedCiv]);

  const triggerEvent = async (type?: string) => {
    if (!selectedCiv) return;
    await fetch(`${API}/api/v1/genesis/civilizations/${selectedCiv}/interact`, {
      method: "POST", headers: authHeaders(),
      body: JSON.stringify({ interaction_type: type }),
    });
    loadGenesis();
  };

  if (loading) {
    return <AppLayout><div className="flex items-center justify-center h-64"><div className="text-muted-foreground">Awakening the primordial world...</div></div></AppLayout>;
  }

  const EraIcon = civ ? (ERA_ICONS[civ.era] || Sprout) : Sprout;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Globe2 className="h-8 w-8" />
              Genesis & Creator Mythology
            </h1>
            <p className="text-muted-foreground mt-1">Observe primitive civilizations evolve, form beliefs, and discover their universe</p>
          </div>
        </div>

        {state && (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {Object.entries(state.civilizations || {}).map(([id, p]) => (
              <button key={id} onClick={() => { setSelectedCiv(id); setActiveTab("overview"); }}
                className={`rounded-lg border p-3 text-left transition-colors hover:bg-secondary/50 ${
                  selectedCiv === id ? "ring-2 ring-foreground" : ""
                }`}>
                <div className="flex items-center gap-2">
                  <EraIcon className="h-4 w-4" />
                  <span className="font-medium">{p.civilization.name}</span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {p.civilization.era} era · Year {p.civilization.current_year}
                </div>
                <div className="text-xs text-muted-foreground">
                  {p.civilization.population} citizens · Level {p.civilization.awareness_level} awareness
                </div>
              </button>
            ))}
          </div>
        )}

        {civ && (
          <>
            <div className="rounded-lg border bg-card p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <EraIcon className="h-8 w-8" />
                  <div>
                    <h2 className="text-xl font-bold">{civ.name}</h2>
                    <p className="text-sm text-muted-foreground">
                      {civ.era.charAt(0).toUpperCase() + civ.era.slice(1)} Era · Year {civ.current_year}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    AWARENESS_COLORS[civ.awareness_level] || "bg-gray-500"
                  }/20 text-${AWARENESS_COLORS[civ.awareness_level]?.replace("bg-", "") || "gray-400"}`}>
                    <BrainCircuit className="h-3 w-3" />
                    {awareness?.label || "Unaware"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <div className="rounded-md border p-2">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><Users className="h-3 w-3" /> Population</div>
                  <div className="text-lg font-bold">{civ.population}</div>
                </div>
                <div className="rounded-md border p-2">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><Lightbulb className="h-3 w-3" /> Technology</div>
                  <div className="text-lg font-bold">{(civ.technology_level * 100).toFixed(0)}%</div>
                </div>
                <div className="rounded-md border p-2">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><BookOpen className="h-3 w-3" /> Culture</div>
                  <div className="text-lg font-bold">{(civ.culture_level * 100).toFixed(0)}%</div>
                </div>
                <div className="rounded-md border p-2">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><Atom className="h-3 w-3" /> Science</div>
                  <div className="text-lg font-bold">{(civ.scientific_level * 100).toFixed(0)}%</div>
                </div>
              </div>

              {civ.origin_story && (
                <div className="mt-3 rounded-md bg-secondary/30 p-3 text-sm italic text-muted-foreground">
                  {civ.origin_story}
                </div>
              )}
            </div>

            <div className="flex gap-1 border-b overflow-x-auto">
              {(["overview", "beliefs", "discoveries", "timeline", "awareness", "history"] as const).map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === tab ? "border-foreground text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}>
                  {tab === "overview" && <Globe2 className="h-4 w-4" />}
                  {tab === "beliefs" && <BookOpen className="h-4 w-4" />}
                  {tab === "discoveries" && <Lightbulb className="h-4 w-4" />}
                  {tab === "timeline" && <History className="h-4 w-4" />}
                  {tab === "awareness" && <BrainCircuit className="h-4 w-4" />}
                  {tab === "history" && <ScrollText className="h-4 w-4" />}
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {activeTab === "overview" && (
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><Users className="h-4 w-4" /> Citizens ({agents.length})</h3>
                  <div className="space-y-2">
                    {agents.slice(0, 10).map((a) => (
                      <div key={a.id} className="flex items-center gap-2 rounded-md border p-2 text-sm">
                        <span className={`h-2 w-2 rounded-full ${a.status === "alive" ? "bg-green-400" : "bg-red-400"}`} />
                        <span className="font-medium">{a.name}</span>
                        <span className="text-xs text-muted-foreground">{a.role}</span>
                        <div className="ml-auto flex gap-2 text-xs text-muted-foreground">
                          <span>Intel: {(a.intelligence_level * 100).toFixed(0)}%</span>
                          <span>Survival: {(a.survival_skill * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><Atom className="h-4 w-4" /> Knowledge Domains</h3>
                  <div className="space-y-2">
                    {knowledge.map((k) => (
                      <div key={k.id} className="rounded-md border p-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium">{k.domain_name}</span>
                          <span className="text-xs text-muted-foreground">{(k.level * 100).toFixed(0)}%</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                          <div className="h-full rounded-full bg-blue-500 transition-all" style={{ width: `${k.level * 100}%` }} />
                        </div>
                        {k.understanding && (
                          <div className="text-xs text-muted-foreground mt-1 italic">{k.understanding}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><BookOpen className="h-4 w-4" /> Belief Systems</h3>
                  {beliefs.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No belief systems have emerged yet. The people have no explanation for their existence.</p>
                  ) : (
                    <div className="space-y-2">
                      {beliefs.map((b) => (
                        <div key={b.id} className="rounded-md border p-3">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{b.name}</span>
                            <span className={`text-xs px-1.5 py-0.5 rounded ${
                              b.belief_type === "spiritual" ? "bg-purple-500/20 text-purple-400" :
                              b.belief_type === "animistic" ? "bg-green-500/20 text-green-400" :
                              "bg-blue-500/20 text-blue-400"
                            }`}>{b.belief_type}</span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 italic">{b.origin_explanation}</p>
                          {b.creator_concept && (
                            <p className="text-xs text-muted-foreground mt-1">Creator: {b.creator_concept}</p>
                          )}
                          <div className="flex gap-2 mt-1 text-xs text-muted-foreground">
                            <span>{b.followers_count} followers</span>
                            <span>Influence: {(b.influence_level * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><Sparkles className="h-4 w-4" /> Creator Actions</h3>
                  <p className="text-sm text-muted-foreground mb-3">Interact with the civilization as an external force. Your actions will be interpreted through their belief systems.</p>
                  <div className="grid grid-cols-2 gap-2">
                    {["rainfall", "new_resource", "environmental_change", "revelation", "phenomenon"].map((type) => (
                      <button key={type} onClick={() => triggerEvent(type)}
                        className="flex items-center gap-2 rounded-md border p-2 text-sm hover:bg-secondary/50 transition-colors">
                        <CloudSun className="h-4 w-4 text-muted-foreground" />
                        {type.replace(/_/g, " ")}
                      </button>
                    ))}
                  </div>
                  {interactions.length > 0 && (
                    <div className="mt-3 space-y-1">
                      <span className="text-xs font-medium text-muted-foreground">Recent interactions:</span>
                      {interactions.slice(0, 3).map((i) => (
                        <div key={i.id} className="rounded-md bg-secondary/30 p-2 text-xs">
                          <span className="font-medium">{i.interaction_type}:</span> {i.civilization_interpretation}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "beliefs" && (
              <div className="space-y-4">
                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3">Belief Systems</h3>
                  {beliefs.length === 0 ? (
                    <p className="text-sm text-muted-foreground">The civilization has not yet developed any formal belief system. They experience the world without explanation.</p>
                  ) : (
                    <div className="space-y-4">
                      {beliefs.map((b) => (
                        <div key={b.id} className="rounded-lg border p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold">{b.name}</h4>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              b.status === "established" ? "bg-green-500/20 text-green-400" :
                              b.status === "emerging" ? "bg-yellow-500/20 text-yellow-400" :
                              "bg-gray-500/20 text-gray-400"
                            }`}>{b.status}</span>
                          </div>
                          <p className="text-sm italic mb-2">{b.origin_explanation}</p>

                          {b.creator_concept && (
                            <div className="mb-2">
                              <span className="text-xs font-medium text-muted-foreground">Creator Concept: </span>
                              <span className="text-sm">{b.creator_concept}</span>
                            </div>
                          )}

                          <div className="mb-2">
                            <span className="text-xs font-medium text-muted-foreground">Core Tenets:</span>
                            <ul className="list-disc list-inside text-sm mt-1">
                              {b.core_tenets.map((t, i) => <li key={i}>{t}</li>)}
                            </ul>
                          </div>

                          <div className="mb-2">
                            <span className="text-xs font-medium text-muted-foreground">Rituals:</span>
                            <ul className="list-disc list-inside text-sm mt-1">
                              {b.rituals.map((r, i) => <li key={i}>{r}</li>)}
                            </ul>
                          </div>

                          {Object.keys(b.natural_event_explanations).length > 0 && (
                            <div>
                              <span className="text-xs font-medium text-muted-foreground">Natural Explanations:</span>
                              <div className="grid grid-cols-2 gap-2 mt-1">
                                {Object.entries(b.natural_event_explanations).map(([evt, exp]) => (
                                  <div key={evt} className="rounded-md bg-secondary/30 p-2 text-xs">
                                    <span className="font-medium">{evt}:</span> {exp as string}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {philosophies.length > 0 && (
                  <div className="rounded-lg border bg-card p-4">
                    <h3 className="font-semibold mb-3">Philosophies</h3>
                    <div className="space-y-3">
                      {philosophies.map((p) => (
                        <div key={p.id} className="rounded-md border p-3">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{p.name}</span>
                            <span className="text-xs text-muted-foreground">{p.school_of_thought}</span>
                          </div>
                          <ul className="list-disc list-inside text-sm mt-1">
                            {p.core_ideas.map((idea, i) => <li key={i} className="text-muted-foreground">{idea}</li>)}
                          </ul>
                          <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                            <span>Influence: {(p.influence * 100).toFixed(0)}%</span>
                            <span>{p.followers} followers</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === "discoveries" && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><Lightbulb className="h-4 w-4" /> Discoveries & Knowledge ({discoveries.length})</h3>
                {discoveries.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No discoveries made yet. The civilization is still learning to survive.</p>
                ) : (
                  <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                    {discoveries.map((d) => (
                      <div key={d.id} className="rounded-md border p-3 hover:bg-secondary/30 transition-colors">
                        <div className="flex items-center gap-2">
                          <span className={`h-2 w-2 rounded-full ${
                            d.discovery_type === "scientific" ? "bg-blue-400" :
                            d.discovery_type === "technology" ? "bg-amber-400" :
                            "bg-green-400"
                          }`} />
                          <span className="text-sm font-medium">{d.title}</span>
                          <span className={`text-xs px-1.5 py-0.5 rounded ml-auto ${
                            d.discovery_type === "scientific" ? "bg-blue-500/20 text-blue-400" :
                            d.discovery_type === "technology" ? "bg-amber-500/20 text-amber-400" :
                            "bg-green-500/20 text-green-400"
                          }`}>{d.discovery_type}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{d.description}</p>
                        <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                          <span>Impact: {(d.impact_level * 100).toFixed(0)}%</span>
                          <span>Era: {d.era_recorded}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "timeline" && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><History className="h-4 w-4" /> Civilization Timeline</h3>
                {eras.length === 0 ? (
                  <p className="text-sm text-muted-foreground">The civilization has not yet recorded its history.</p>
                ) : (
                  <div className="space-y-4">
                    {eras.map((era, idx) => {
                      const EraIcon = ERA_ICONS[era.era_name] || Sprout;
                      return (
                        <div key={era.id} className="relative pl-8">
                          {idx < eras.length - 1 && (
                            <div className="absolute left-3.5 top-8 bottom-0 w-px bg-border" />
                          )}
                          <div className="absolute left-0 top-1 flex h-7 w-7 items-center justify-center rounded-full bg-secondary">
                            <EraIcon className="h-4 w-4" />
                          </div>
                          <div className="rounded-lg border p-3">
                            <div className="flex items-center justify-between">
                              <span className="font-bold">{era.era_name.charAt(0).toUpperCase() + era.era_name.slice(1)} Era</span>
                              <span className="text-xs text-muted-foreground">
                                Year {era.start_year}{era.end_year ? ` – ${era.end_year}` : " – present"}
                              </span>
                            </div>
                            <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                              <span>Population: {era.population_at_start}</span>
                              <span>Tech: {(era.technology_level * 100).toFixed(0)}%</span>
                              <span>Culture: {(era.culture_level * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {activeTab === "awareness" && (
              <div className="space-y-4">
                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><BrainCircuit className="h-4 w-4" /> Creator Awareness</h3>
                  {awareness && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className={`h-4 w-4 rounded-full ${AWARENESS_COLORS[awareness.level] || "bg-gray-500"}`} />
                        <div>
                          <div className="font-medium">Level {awareness.level}: {awareness.label}</div>
                          <div className="text-sm text-muted-foreground">{awareness.description}</div>
                        </div>
                      </div>
                      {awareness.has_discovered_simulation && (
                        <div className="rounded-md border border-red-500/30 bg-red-500/10 p-3">
                          <div className="flex items-center gap-2 font-medium text-red-400">
                            <AlertCircle className="h-4 w-4" /> Simulation Discovered
                          </div>
                          <p className="text-sm text-red-300/80 mt-1">
                            This civilization has discovered the simulated nature of their reality.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {awareness && awareness.records.length > 0 && (
                  <div className="rounded-lg border bg-card p-4">
                    <h3 className="font-semibold mb-3">Awareness Evolution</h3>
                    <div className="space-y-3">
                      {awareness.records.map((r) => (
                        <div key={r.id} className="rounded-md border p-3">
                          <div className="flex items-center gap-2">
                            <span className={`h-2 w-2 rounded-full ${AWARENESS_COLORS[r.awareness_level] || "bg-gray-500"}`} />
                            <span className="font-medium">Level {r.awareness_level}</span>
                            <span className="text-xs text-muted-foreground">
                              by {r.philosopher_responsible}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1 italic">{r.understanding_description}</p>
                          {r.evidence_collected.length > 0 && (
                            <div className="flex gap-1 mt-1 flex-wrap">
                              {r.evidence_collected.map((ev, i) => (
                                <span key={i} className="text-xs bg-secondary/50 px-1.5 py-0.5 rounded">{ev}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === "history" && (
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><CloudSun className="h-4 w-4" /> Creator Interactions</h3>
                  {interactions.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No creator interactions recorded. The civilization has not experienced external intervention.</p>
                  ) : (
                    <div className="space-y-2 max-h-80 overflow-y-auto">
                      {interactions.map((i) => (
                        <div key={i.id} className="rounded-md border p-2">
                          <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                            <CloudSun className="h-3 w-3" />
                            {i.interaction_type.replace(/_/g, " ")}
                            {i.triggered_by_creator && <span className="text-blue-400">(creator)</span>}
                          </div>
                          <p className="text-sm mt-0.5">{i.description}</p>
                          <p className="text-xs text-muted-foreground italic mt-0.5">
                            Interpretation: {i.civilization_interpretation}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="rounded-lg border bg-card p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><ScrollText className="h-4 w-4" /> Historical Interpretations</h3>
                  {interpretations.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No historical interpretations recorded. Events are experienced but not yet analyzed.</p>
                  ) : (
                    <div className="space-y-2 max-h-80 overflow-y-auto">
                      {interpretations.map((h) => (
                        <div key={h.id} className="rounded-md border p-2">
                          <div className="text-xs font-medium text-muted-foreground">{h.event_type.replace(/_/g, " ")}</div>
                          <p className="text-sm mt-0.5">{h.actual_event}</p>
                          <p className="text-xs text-muted-foreground italic mt-0.5">
                            They believe: {h.civilization_interpretation}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        {!civ && !loading && (
          <div className="rounded-lg border bg-card p-8 text-center">
            <Globe2 className="h-12 w-12 mx-auto text-muted-foreground" />
            <h3 className="text-lg font-medium mt-3">No Primordial Civilization</h3>
            <p className="text-sm text-muted-foreground mt-1">A civilization will be created automatically when the simulation starts.</p>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
