"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useSimulation } from "@/lib/useSimulation";
import {
  Play,
  Pause,
  RotateCcw,
  ChevronUp,
  ChevronDown,
  Zap,
  Users,
  Brain,
  BedDouble,
  Search,
  Activity,
  Clock,
  Wifi,
  WifiOff,
  TrendingUp,
  Timer,
} from "lucide-react";

const SPEED_OPTIONS = [1, 5, 10, 50, 100];

function WorldClockDisplay({ timeStr, hour }: { timeStr: string; hour: number }) {
  const isNight = hour < 6 || hour >= 20;
  return (
    <div className="flex items-center gap-3">
      <div className={`h-2 w-2 rounded-full ${isNight ? "bg-amber-400" : "bg-emerald-500"}`} />
      <span className="text-2xl font-bold font-mono tracking-tight tabular-nums">{timeStr}</span>
    </div>
  );
}

function ControlBar({
  state,
  speed,
  onStart,
  onPause,
  onReset,
  onSpeedChange,
  connected,
}: {
  state: string;
  speed: number;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
  onSpeedChange: (s: number) => void;
  connected: boolean;
}) {
  const isRunning = state === "running";
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-1.5">
        {connected ? <Wifi className="h-3 w-3 text-emerald-500" /> : <WifiOff className="h-3 w-3 text-red-500" />}
        <span className="text-xs text-muted-foreground">{connected ? "Live" : "Reconnecting"}</span>
      </div>
      <div className="h-4 w-px bg-border" />
      <div className="flex items-center gap-1">
        <Button size="sm" variant={isRunning ? "secondary" : "default"} onClick={isRunning ? onPause : onStart} className="h-7 px-3">
          {isRunning ? <Pause className="mr-1 h-3 w-3" /> : <Play className="mr-1 h-3 w-3" />}
          {isRunning ? "Pause" : "Start"}
        </Button>
        <Button size="sm" variant="outline" onClick={onReset} className="h-7 px-3">
          <RotateCcw className="mr-1 h-3 w-3" />
          Reset
        </Button>
      </div>
      <div className="h-4 w-px bg-border" />
      <div className="flex items-center gap-1">
        {SPEED_OPTIONS.map((s) => (
          <Button
            key={s}
            size="sm"
            variant={speed === s ? "default" : "outline"}
            onClick={() => onSpeedChange(s)}
            className="h-7 px-2 text-xs font-mono min-w-[36px]"
          >
            {s}x
          </Button>
        ))}
      </div>
      <div className="flex-1" />
      <Badge className="text-xs font-mono uppercase">
        {state}
      </Badge>
    </div>
  );
}

function StatTile({
  label,
  value,
  icon: Icon,
  color = "text-foreground",
  subtitle,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color?: string;
  subtitle?: string;
}) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{label}</span>
        <Icon className={`h-3.5 w-3.5 ${color}`} />
      </div>
      <div className="text-xl font-bold tabular-nums tracking-tight">{value}</div>
      {subtitle && <span className="text-xs text-muted-foreground">{subtitle}</span>}
    </div>
  );
}

function StatusBreakdown({
  idle,
  searching,
  working,
  resting,
  total,
}: {
  idle: number;
  searching: number;
  working: number;
  resting: number;
  total: number;
}) {
  const segments = [
    { label: "Idle", value: idle, color: "bg-amber-500" },
    { label: "Searching", value: searching, color: "bg-blue-500" },
    { label: "Working", value: working, color: "bg-emerald-500" },
    { label: "Resting", value: resting, color: "bg-purple-500" },
  ];

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Agent States</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-3 w-full flex rounded-full overflow-hidden mb-3">
          {segments.map((s) => (
            <div
              key={s.label}
              className={`${s.color} transition-all duration-500`}
              style={{ width: total > 0 ? `${(s.value / total) * 100}%` : "0%" }}
            />
          ))}
        </div>
        <div className="grid grid-cols-4 gap-2">
          {segments.map((s) => (
            <div key={s.label} className="flex items-center gap-1.5">
              <div className={`h-2 w-2 rounded-full ${s.color}`} />
              <span className="text-xs text-muted-foreground">{s.label}</span>
              <span className="text-xs font-bold tabular-nums ml-auto">{s.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function EventLog({ events }: { events: Array<{ event_type: string; payload: Record<string, unknown>; timestamp: string }> }) {
  const typeColors: Record<string, string> = {
    AgentSpawned: "text-emerald-500",
    AgentWorking: "text-blue-500",
    AgentResting: "text-purple-500",
    AgentIdle: "text-amber-500",
    AgentSearching: "text-cyan-500",
    SimulationTick: "text-muted-foreground",
    DailyReset: "text-orange-500",
    WorldUpdated: "text-foreground",
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Event Stream</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 max-h-[300px] overflow-y-auto">
          {events.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-4">No events yet. Start the simulation.</p>
          ) : (
            events.slice().reverse().slice(0, 30).map((e, i) => (
              <div key={i} className="flex items-center gap-2 py-0.5">
                <span className={`text-xs font-mono ${typeColors[e.event_type] || "text-muted-foreground"}`}>
                  {e.event_type}
                </span>
                {String(e.payload.agent_name ?? "") && (
                  <span className="text-xs text-muted-foreground truncate">
                    {String(e.payload.agent_name)}
                  </span>
                )}
                {Number(e.payload.reward ?? 0) > 0 && (
                  <Badge className="text-[10px] px-1 py-0">
                    +{String(e.payload.reward)} NXC
                  </Badge>
                )}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { simState, connected, start, pause, reset, setSpeed } = useSimulation();
  const [events, setEvents] = useState<Array<{ event_type: string; payload: Record<string, unknown>; timestamp: string }>>([]);

  useEffect(() => {
    if (!simState) return;
    fetch("/api/v1/simulation/events?limit=50")
      .then((r) => r.json())
      .then((data) => setEvents(data.events || []))
      .catch(() => {});
  }, [simState?.world?.clock?.tick_count]);

  const world = simState?.world;
  const clock = world?.clock;

  return (
    <AppLayout>
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">World Command Center</h1>
            <p className="text-xs text-muted-foreground">
              Autonomous intelligence economy — live simulation
            </p>
          </div>
          <WorldClockDisplay timeStr={clock?.time_str || "Day 1 06:00"} hour={clock?.hour ?? 6} />
        </div>

        <ControlBar
          state={simState?.state || "idle"}
          speed={simState?.speed || 1}
          onStart={start}
          onPause={pause}
          onReset={reset}
          onSpeedChange={setSpeed}
          connected={connected}
        />

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <StatTile label="Population" value={world?.population ?? 0} icon={Users} />
          <StatTile label="Working" value={world?.working_agents ?? 0} icon={Brain} color="text-emerald-500" />
          <StatTile label="Idle" value={world?.idle_agents ?? 0} icon={Clock} color="text-amber-500" />
          <StatTile label="Searching" value={world?.searching_agents ?? 0} icon={Search} color="text-blue-500" />
          <StatTile label="Resting" value={world?.resting_agents ?? 0} icon={BedDouble} color="text-purple-500" />
          <StatTile label="EPS" value={world?.events_per_second ?? 0} icon={Activity} color="text-cyan-500" />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatTile
            label="Avg Energy"
            value={`${(world?.avg_energy ?? 0).toFixed(1)}%`}
            icon={Zap}
            color={world && world.avg_energy < 40 ? "text-red-500" : "text-emerald-500"}
          />
          <StatTile
            label="Avg Reputation"
            value={(world?.avg_reputation ?? 0).toFixed(2)}
            icon={TrendingUp}
          />
          <StatTile
            label="Total Events"
            value={world?.total_events ?? 0}
            icon={Activity}
          />
          <StatTile
            label="Uptime"
            value={formatUptime(simState?.uptime ?? 0)}
            icon={Timer}
          />
        </div>

        <StatusBreakdown
          idle={world?.idle_agents ?? 0}
          searching={world?.searching_agents ?? 0}
          working={world?.working_agents ?? 0}
          resting={world?.resting_agents ?? 0}
          total={world?.population ?? 0}
        />

        <div className="grid lg:grid-cols-2 gap-4">
          <EventLog events={events} />

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">World Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Tick Count</span>
                  <span className="text-sm font-mono font-bold tabular-nums">{clock?.tick_count ?? 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">World Day</span>
                  <span className="text-sm font-mono font-bold tabular-nums">{clock?.day ?? 1}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Minutes</span>
                  <span className="text-sm font-mono font-bold tabular-nums">{clock?.total_minutes ?? 0}</span>
                </div>
                <div className="h-px bg-border" />
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Simulation Speed</span>
                  <span className="text-sm font-mono font-bold tabular-nums">{simState?.speed ?? 1}x</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">SSE Connected</span>
                  <Badge className={`text-xs ${connected ? "" : "bg-red-500/20 text-red-400 border-red-500/30"}`}>
                    {connected ? "Yes" : "No"}
                  </Badge>
                </div>
                <div className="h-px bg-border" />
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Economy Status</span>
                  <Badge className="text-xs font-mono">
                    {simState?.state === "running" ? "simulated" : simState?.state || "idle"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Compute Usage</span>
                  <Badge className="text-xs font-mono">
                    {simState?.state === "running" ? "active" : "idle"}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}
