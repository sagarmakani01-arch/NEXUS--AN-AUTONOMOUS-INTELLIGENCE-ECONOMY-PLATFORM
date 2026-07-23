"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import {
  Clock,
  Play,
  Pause,
  FastForward,
  SkipForward,
  History,
  GitBranch,
  Search,
  BarChart3,
  Network,
  Camera,
  ChevronRight,
  Calendar,
  Zap,
  Target,
  MapPin,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface TemporalClock {
  clock_id: string;
  tick_count: number;
  year: number;
  day: number;
  hour: number;
  time_scale: number;
  paused: boolean;
  running: boolean;
  century: number;
  time_string: string;
}

interface TemporalEvent {
  id: string;
  event_type: string;
  title: string;
  description?: string;
  location?: string;
  impact_score: number;
  tick: number;
  year?: number;
}

interface TemporalSnapshot {
  id: string;
  tick: number;
  year: number;
  label: string;
  created_at?: string;
}

interface TemporalTimeline {
  id: string;
  name: string;
  branch_point_tick?: number;
  branch_point_year?: number;
  divergence_cause?: string;
  event_count: number;
  status: string;
}

interface TemporalAnalytics {
  summary: {
    total_events: number;
    years_span: number;
    events_per_year: number;
    first_event: { title: string; year: number };
    last_event: { title: string; year: number };
    unique_locations: number;
    unique_participants: number;
    average_impact_score: number;
  };
  event_distribution: {
    distribution: { type: string; count: number }[];
    total_events: number;
  };
  milestones: {
    milestones: TemporalEvent[];
    count: number;
  };
}

export default function TemporalPage() {
  const [clock, setClock] = useState<TemporalClock | null>(null);
  const [events, setEvents] = useState<TemporalEvent[]>([]);
  const [snapshots, setSnapshots] = useState<TemporalSnapshot[]>([]);
  const [branches, setBranches] = useState<TemporalTimeline[]>([]);
  const [analytics, setAnalytics] = useState<TemporalAnalytics | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<TemporalEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"timeline" | "events" | "branches" | "analytics" | "search">("timeline");
  const [branchName, setBranchName] = useState("");
  const [branchCause, setBranchCause] = useState("");

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  };

  useEffect(() => {
    loadTemporalState();
    const interval = setInterval(loadTemporalState, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadTemporalState = async () => {
    try {
      const [clockRes, eventsRes, snapshotsRes, branchesRes, analyticsRes] = await Promise.all([
        fetch(`${API}/api/v1/temporal/clock`, { headers: authHeaders() }),
        fetch(`${API}/api/v1/temporal/history/events?limit=50`, { headers: authHeaders() }),
        fetch(`${API}/api/v1/temporal/snapshots`, { headers: authHeaders() }),
        fetch(`${API}/api/v1/timelines`, { headers: authHeaders() }).catch(() => null),
        fetch(`${API}/api/v1/temporal/analytics`, { headers: authHeaders() }).catch(() => null),
      ]);

      if (clockRes.ok) {
        const data = await clockRes.json();
        setClock(data.clock);
      }
      if (eventsRes.ok) {
        const data = await eventsRes.json();
        setEvents(Array.isArray(data) ? data : []);
      }
      if (snapshotsRes.ok) {
        const data = await snapshotsRes.json();
        setSnapshots(Array.isArray(data) ? data : []);
      }
      if (branchesRes?.ok) {
        const data = await branchesRes.json();
        setBranches(Array.isArray(data) ? data : []);
      }
      if (analyticsRes?.ok) {
        const data = await analyticsRes.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error("Failed to load temporal state", err);
    } finally {
      setLoading(false);
    }
  };

  const advanceTime = async (ticks: number) => {
    try {
      await fetch(`${API}/api/v1/temporal/clock/advance?ticks=${ticks}`, { method: "POST", headers: authHeaders() });
      loadTemporalState();
    } catch (err) {
      console.error("Failed to advance time", err);
    }
  };

  const pauseResume = async () => {
    try {
      const endpoint = clock?.paused ? "resume" : "pause";
      await fetch(`${API}/api/v1/temporal/clock/${endpoint}`, { method: "POST", headers: authHeaders() });
      loadTemporalState();
    } catch (err) {
      console.error("Failed to pause/resume", err);
    }
  };

  const jumpToYear = async (year: number) => {
    try {
      await fetch(`${API}/api/v1/temporal/clock/jump?year=${year}`, { method: "POST", headers: authHeaders() });
      loadTemporalState();
    } catch (err) {
      console.error("Failed to jump", err);
    }
  };

  const createBranch = async () => {
    if (!branchName.trim()) return;
    try {
      await fetch(`${API}/api/v1/timelines/branch`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ name: branchName, divergence_cause: branchCause || undefined }),
      });
      setBranchName("");
      setBranchCause("");
      loadTemporalState();
    } catch (err) {
      console.error("Failed to create branch", err);
    }
  };

  const searchHistory = async () => {
    if (!searchQuery.trim()) return;
    try {
      const res = await fetch(`${API}/api/v1/temporal/explorer/search`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ query: searchQuery, limit: 30 }),
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error("Failed to search", err);
    }
  };

  const eventTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      agent_spawned: "bg-blue-500/20 text-blue-400",
      job_completed: "bg-green-500/20 text-green-400",
      goal_completed: "bg-purple-500/20 text-purple-400",
      skill_improved: "bg-yellow-500/20 text-yellow-400",
      daily_reset: "bg-gray-500/20 text-gray-400",
      simulation_started: "bg-cyan-500/20 text-cyan-400",
      civilization_created: "bg-amber-500/20 text-amber-400",
      technology_unlocked: "bg-emerald-500/20 text-emerald-400",
      research_started: "bg-indigo-500/20 text-indigo-400",
      law_created: "bg-rose-500/20 text-rose-400",
    };
    return colors[type] || "bg-secondary text-muted-foreground";
  };

  const formatYear = (year?: number) => year ? `Year ${year}` : "Unknown";

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading temporal engine...</div>
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
              <Clock className="h-8 w-8" />
              Time & History
            </h1>
            <p className="text-muted-foreground mt-1">
              Temporal simulation engine — replay history, branch timelines, explore causality
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={pauseResume}
              className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium hover:bg-secondary/80"
            >
              {clock?.paused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
              {clock?.paused ? "Resume" : "Pause"}
            </button>
            <button
              onClick={() => advanceTime(1)}
              className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium hover:bg-secondary/80"
            >
              <FastForward className="h-4 w-4" />
              +1 Tick
            </button>
            <button
              onClick={() => advanceTime(10)}
              className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium hover:bg-secondary/80"
            >
              <SkipForward className="h-4 w-4" />
              +10 Ticks
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Current Time</div>
            <div className="text-2xl font-bold mt-1">{clock?.time_string || "Not initialized"}</div>
            <div className="text-xs text-muted-foreground mt-1">Tick {clock?.tick_count || 0}</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Century</div>
            <div className="text-2xl font-bold mt-1">{clock?.century || 1}</div>
            <div className="text-xs text-muted-foreground mt-1">Time Scale: {clock?.time_scale || 1}x</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Total Events</div>
            <div className="text-2xl font-bold mt-1">{analytics?.summary?.total_events || events.length}</div>
            <div className="text-xs text-muted-foreground mt-1">{analytics?.summary?.years_span || 0} years span</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Snapshots</div>
            <div className="text-2xl font-bold mt-1">{snapshots.length}</div>
            <div className="text-xs text-muted-foreground mt-1">{branches.length} branches</div>
          </div>
        </div>

        <div className="flex gap-1 border-b">
          {(["timeline", "events", "branches", "analytics", "search"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-foreground text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab === "timeline" && <History className="h-4 w-4" />}
              {tab === "events" && <Calendar className="h-4 w-4" />}
              {tab === "branches" && <GitBranch className="h-4 w-4" />}
              {tab === "analytics" && <BarChart3 className="h-4 w-4" />}
              {tab === "search" && <Search className="h-4 w-4" />}
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {activeTab === "timeline" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Interactive Timeline</h3>
              {events.length === 0 ? (
                <p className="text-muted-foreground text-sm">No events recorded yet. Start the simulation to build history.</p>
              ) : (
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />
                  <div className="space-y-3">
                    {events.slice(0, 20).map((event, i) => (
                      <div key={event.id || i} className="flex items-start gap-3 pl-2">
                        <div className="relative z-10 mt-1 h-3 w-3 rounded-full bg-primary ring-2 ring-card" />
                        <div className="flex-1 rounded-md border p-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${eventTypeColor(event.event_type)}`}>
                                {event.event_type.replace(/_/g, " ")}
                              </span>
                              <span className="text-sm font-medium">{event.title}</span>
                            </div>
                            <span className="text-xs text-muted-foreground">{formatYear(event.year)}</span>
                          </div>
                          {event.description && (
                            <p className="text-xs text-muted-foreground mt-1">{event.description}</p>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                            {event.location && (
                              <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{event.location}</span>
                            )}
                            <span className="flex items-center gap-1"><Zap className="h-3 w-3" />Impact: {(event.impact_score * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "events" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Event Log</h3>
              {events.length === 0 ? (
                <p className="text-muted-foreground text-sm">No events recorded yet.</p>
              ) : (
                <div className="space-y-2">
                  {events.map((event, i) => (
                    <div key={event.id || i} className="flex items-center gap-3 rounded-md border p-3 hover:bg-secondary/50">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${eventTypeColor(event.event_type)}`}>
                        {event.event_type.replace(/_/g, " ")}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{event.title}</div>
                        {event.description && (
                          <div className="text-xs text-muted-foreground truncate">{event.description}</div>
                        )}
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-xs text-muted-foreground">{formatYear(event.year)}</div>
                        <div className="text-xs text-muted-foreground">Tick {event.tick}</div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-xs font-medium">{(event.impact_score * 100).toFixed(0)}%</div>
                        <div className="text-xs text-muted-foreground">impact</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "branches" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Create Alternate Timeline</h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={branchName}
                  onChange={(e) => setBranchName(e.target.value)}
                  placeholder="Branch name..."
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
                />
                <input
                  type="text"
                  value={branchCause}
                  onChange={(e) => setBranchCause(e.target.value)}
                  placeholder="What-if scenario..."
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
                />
                <button
                  onClick={createBranch}
                  disabled={!branchName.trim()}
                  className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  <GitBranch className="h-4 w-4" />
                  Branch
                </button>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Timeline Branches</h3>
              {branches.length === 0 ? (
                <p className="text-muted-foreground text-sm">No branches created yet. Create an alternate timeline to compare different futures.</p>
              ) : (
                <div className="space-y-2">
                  {branches.map((branch) => (
                    <div key={branch.id} className="flex items-center gap-3 rounded-md border p-3 hover:bg-secondary/50">
                      <GitBranch className="h-5 w-5 text-muted-foreground shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium">{branch.name}</div>
                        {branch.divergence_cause && (
                          <div className="text-xs text-muted-foreground">{branch.divergence_cause}</div>
                        )}
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-xs text-muted-foreground">Branched at Year {branch.branch_point_year || "?"}</div>
                        <div className="text-xs text-muted-foreground">{branch.event_count} events</div>
                      </div>
                      <span className="inline-flex items-center rounded-full bg-green-500/20 px-2 py-0.5 text-xs font-medium text-green-400 shrink-0">
                        {branch.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Snapshots</h3>
              {snapshots.length === 0 ? (
                <p className="text-muted-foreground text-sm">No snapshots captured yet. Snapshots are auto-created for replay and branching.</p>
              ) : (
                <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
                  {snapshots.map((snap) => (
                    <div key={snap.id} className="flex items-center gap-3 rounded-md border p-3">
                      <Camera className="h-5 text-muted-foreground shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{snap.label}</div>
                        <div className="text-xs text-muted-foreground">Year {snap.year}, Tick {snap.tick}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "analytics" && (
          <div className="space-y-4">
            {analytics ? (
              <>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                  <div className="rounded-lg border bg-card p-4">
                    <div className="text-sm text-muted-foreground">Years Span</div>
                    <div className="text-2xl font-bold">{analytics.summary.years_span}</div>
                  </div>
                  <div className="rounded-lg border bg-card p-4">
                    <div className="text-sm text-muted-foreground">Events/Year</div>
                    <div className="text-2xl font-bold">{analytics.summary.events_per_year.toFixed(1)}</div>
                  </div>
                  <div className="rounded-lg border bg-card p-4">
                    <div className="text-sm text-muted-foreground">Avg Impact</div>
                    <div className="text-2xl font-bold">{(analytics.summary.average_impact_score * 100).toFixed(0)}%</div>
                  </div>
                  <div className="rounded-lg border bg-card p-4">
                    <div className="text-sm text-muted-foreground">Participants</div>
                    <div className="text-2xl font-bold">{analytics.summary.unique_participants}</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="rounded-lg border bg-card p-4">
                    <h3 className="font-semibold mb-3">Event Distribution</h3>
                    <div className="space-y-2">
                      {analytics.event_distribution.distribution.slice(0, 8).map((item) => (
                        <div key={item.type} className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground w-32 truncate">{item.type.replace(/_/g, " ")}</span>
                          <div className="flex-1 h-4 bg-secondary rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary rounded-full"
                              style={{ width: `${(item.count / Math.max(...analytics.event_distribution.distribution.map(d => d.count))) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium w-8 text-right">{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-lg border bg-card p-4">
                    <h3 className="font-semibold mb-3">Key Milestones</h3>
                    {analytics.milestones.milestones.length === 0 ? (
                      <p className="text-muted-foreground text-sm">No milestones detected yet.</p>
                    ) : (
                      <div className="space-y-2">
                        {analytics.milestones.milestones.slice(0, 5).map((m, i) => (
                          <div key={m.id || i} className="flex items-center gap-2 rounded-md border p-2">
                            <Target className="h-4 text-amber-500 shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium truncate">{m.title}</div>
                              <div className="text-xs text-muted-foreground">{m.event_type.replace(/_/g, " ")} — {formatYear(m.year)}</div>
                            </div>
                            <span className="text-xs font-medium text-amber-400">{(m.impact_score * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="rounded-lg border bg-card p-8 text-center">
                <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-semibold mb-2">No Analytics Available</h3>
                <p className="text-sm text-muted-foreground">Analytics are generated as events accumulate. Start the simulation to build history.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "search" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-3">Search History</h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && searchHistory()}
                  placeholder="Search events by title, description, type..."
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
                />
                <button
                  onClick={searchHistory}
                  disabled={!searchQuery.trim()}
                  className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  <Search className="h-4 w-4" />
                  Search
                </button>
              </div>
            </div>

            {searchResults.length > 0 && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="font-semibold mb-3">Search Results ({searchResults.length})</h3>
                <div className="space-y-2">
                  {searchResults.map((event, i) => (
                    <div key={event.id || i} className="flex items-center gap-3 rounded-md border p-3 hover:bg-secondary/50">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${eventTypeColor(event.event_type)}`}>
                        {event.event_type.replace(/_/g, " ")}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium">{event.title}</div>
                        {event.description && (
                          <div className="text-xs text-muted-foreground">{event.description}</div>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">{formatYear(event.year)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
