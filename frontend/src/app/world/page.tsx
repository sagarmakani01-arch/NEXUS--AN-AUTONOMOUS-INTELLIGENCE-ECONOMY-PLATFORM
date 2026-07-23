"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type {
  WorldFullState, WorldMapState, WorldTimeState, WorldCitizen,
  WorldBuilding, WorldEvent, WorldZone, WorldRoad,
} from "@/types";

const API = "http://localhost:8000/api/v1/world";
const TICK_MS = 500;
const STATUS_COLORS: Record<string, string> = {
  walking: "#facc15", working: "#3b82f6", resting: "#6b7280",
  shopping: "#f97316", meeting: "#8b5cf6", researching: "#7c3aed",
  studying: "#06b6d4", exploring: "#22c55e", commuting: "#f59e0b",
  socializing: "#ec4899", idle: "#9ca3af",
};

interface Camera { x: number; y: number; zoom: number; }
interface InspectorTarget { type: "citizen" | "building"; id: string; data: Record<string, unknown>; }

export default function WorldPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [world, setWorld] = useState<WorldFullState | null>(null);
  const [map, setMap] = useState<WorldMapState | null>(null);
  const [time, setTime] = useState<WorldTimeState | null>(null);
  const [citizens, setCitizens] = useState<WorldCitizen[]>([]);
  const [events, setEvents] = useState<WorldEvent[]>([]);
  const [camera, setCamera] = useState<Camera>({ x: 0, y: 0, zoom: 2.0 });
  const [followId, setFollowId] = useState<string | null>(null);
  const [inspector, setInspector] = useState<InspectorTarget | null>(null);
  const [selectedOverlay, setSelectedOverlay] = useState<string>("none");
  const [observerMode, setObserverMode] = useState<string>("city");
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const camStart = useRef({ x: 0, y: 0 });
  const animFrame = useRef<number>(0);
  const lastFetch = useRef(0);

  const fetchWorld = useCallback(async () => {
    try {
      const now = Date.now();
      if (now - lastFetch.current < TICK_MS) return;
      lastFetch.current = now;
      const [mapRes, timeRes, citRes, evRes] = await Promise.all([
        fetch(`${API}/map`).then(r => r.json()),
        fetch(`${API}/time`).then(r => r.json()),
        fetch(`${API}/citizens?visible_only=false`).then(r => r.json()),
        fetch(`${API}/events?limit=30`).then(r => r.json()),
      ]);
      setMap(mapRes);
      setTime(timeRes);
      setCitizens(citRes);
      setEvents(evRes);
      setWorld({ map: mapRes, time: timeRes, citizen_count: citRes.length, event_count: evRes.length });
    } catch { /* backend offline */ }
  }, []);

  useEffect(() => {
    fetchWorld();
    const iv = setInterval(fetchWorld, TICK_MS);
    return () => clearInterval(iv);
  }, [fetchWorld]);

  useEffect(() => {
    if (followId) {
      const c = citizens.find(c => c.agent_id === followId);
      if (c) setCamera(prev => ({ ...prev, x: c.x - 50, y: c.y - 50 }));
    }
  }, [followId, citizens]);

  const worldToScreen = useCallback((wx: number, wy: number) => {
    const tile = map?.tile_size ?? 32;
    return { x: (wx * tile - camera.x * tile) * camera.zoom, y: (wy * tile - camera.y * tile) * camera.zoom };
  }, [camera, map]);

  const screenToWorld = useCallback((sx: number, sy: number) => {
    const tile = map?.tile_size ?? 32;
    return { x: sx / (camera.zoom * tile) + camera.x, y: sy / (camera.zoom * tile) + camera.y };
  }, [camera, map]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const draw = () => {
      const W = canvas.width;
      const H = canvas.height;
      const hour = time?.hour ?? 12;
      const nightFactor = hour >= 20 || hour < 6 ? 0.3 : hour >= 18 ? 0.6 + (hour - 18) * 0.15 : hour <= 6 ? 0.3 + hour * 0.1 : 1;

      ctx.fillStyle = `rgb(${Math.floor(34 * nightFactor)},${Math.floor(40 * nightFactor)},${Math.floor(54 * nightFactor)})`;
      ctx.fillRect(0, 0, W, H);

      if (!map) { animFrame.current = requestAnimationFrame(draw); return; }

      const renderZone = (z: WorldZone) => {
        const p1 = worldToScreen(z.x, z.y);
        const p2 = worldToScreen(z.x + z.width, z.y + z.height);
        const w = p2.x - p1.x;
        const h = p2.y - p1.y;
        if (p2.x < 0 || p1.x > W || p2.y < 0 || p1.y > H) return;
        ctx.globalAlpha = 0.15 * nightFactor;
        ctx.fillStyle = z.color;
        ctx.fillRect(p1.x, p1.y, w, h);
        ctx.globalAlpha = 0.4;
        ctx.strokeStyle = z.color;
        ctx.lineWidth = 1;
        ctx.strokeRect(p1.x, p1.y, w, h);
        if (camera.zoom > 1.0) {
          ctx.globalAlpha = 0.5;
          ctx.fillStyle = z.color;
          ctx.font = `${Math.max(8, 10 / camera.zoom * 2)}px sans-serif`;
          ctx.fillText(z.label, p1.x + 4, p1.y + 14);
        }
        ctx.globalAlpha = 1;
      };

      const renderRoad = (r: WorldRoad) => {
        const p1 = worldToScreen(r.x1, r.y1);
        const p2 = worldToScreen(r.x2, r.y2);
        if (Math.max(p1.x, p2.x) < 0 || Math.min(p1.x, p2.x) > W) return;
        if (Math.max(p1.y, p2.y) < 0 || Math.min(p1.y, p2.y) > H) return;
        ctx.strokeStyle = `rgba(100,116,139,${0.6 * nightFactor})`;
        ctx.lineWidth = r.width * camera.zoom * 0.5;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      };

      const renderBuilding = (b: WorldBuilding) => {
        const p1 = worldToScreen(b.x, b.y);
        const p2 = worldToScreen(b.x + b.width, b.y + b.height);
        const w = p2.x - p1.x;
        const h = p2.y - p1.y;
        if (p2.x < 0 || p1.x > W || p2.y < 0 || p1.y > H) return;
        ctx.globalAlpha = nightFactor;
        ctx.fillStyle = b.color;
        ctx.fillRect(p1.x, p1.y, w, h);
        ctx.strokeStyle = "rgba(0,0,0,0.3)";
        ctx.lineWidth = 1;
        ctx.strokeRect(p1.x, p1.y, w, h);
        if (camera.zoom > 1.2) {
          ctx.fillStyle = "#fff";
          ctx.font = `bold ${Math.max(7, 9 / camera.zoom * 2)}px sans-serif`;
          ctx.textAlign = "center";
          ctx.fillText(b.name, p1.x + w / 2, p1.y + h / 2 + 3);
          ctx.textAlign = "start";
        }
        if (b.visitor_count > 0 && camera.zoom > 1.5) {
          ctx.fillStyle = "#fbbf24";
          ctx.beginPath();
          ctx.arc(p1.x + w - 4, p1.y + 4, 3, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
      };

      const renderCitizen = (c: WorldCitizen) => {
        const p = worldToScreen(c.x, c.y);
        if (p.x < -10 || p.x > W + 10 || p.y < -10 || p.y > H + 10) return;
        const color = STATUS_COLORS[c.status] || "#9ca3af";
        const size = Math.max(3, 4 * camera.zoom);
        ctx.globalAlpha = nightFactor;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
        if (followId === c.agent_id) {
          ctx.strokeStyle = "#fff";
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(p.x, p.y, size + 3, 0, Math.PI * 2);
          ctx.stroke();
        }
        if (camera.zoom > 2.0) {
          ctx.fillStyle = "#fff";
          ctx.font = `${Math.max(6, 8 / camera.zoom * 2)}px sans-serif`;
          ctx.fillText(c.agent_id.slice(0, 6), p.x + size + 2, p.y - 2);
        }
        if (c.destination && camera.zoom > 1.8) {
          ctx.globalAlpha = 0.4;
          ctx.strokeStyle = color;
          ctx.lineWidth = 0.5;
          ctx.setLineDash([2, 2]);
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          const destCitizen = citizens.find(cc => cc.building_id === c.building_id && cc.agent_id !== c.agent_id);
          if (destCitizen) {
            const dp = worldToScreen(destCitizen.x, destCitizen.y);
            ctx.lineTo(dp.x, dp.y);
          }
          ctx.stroke();
          ctx.setLineDash([]);
        }
        ctx.globalAlpha = 1;
      };

      map.zones.forEach(renderZone);
      map.roads.forEach(renderRoad);
      map.buildings.forEach(renderBuilding);
      citizens.forEach(renderCitizen);

      events.slice(-5).forEach((ev, i) => {
        const p = worldToScreen(ev.x, ev.y);
        ctx.globalAlpha = 0.8 - i * 0.15;
        ctx.fillStyle = ev.type.includes("Economic") ? "#f59e0b" : ev.type.includes("Research") ? "#7c3aed" : "#3b82f6";
        ctx.font = `bold ${Math.max(8, 10 / camera.zoom * 2)}px sans-serif`;
        ctx.fillText(ev.description.slice(0, 40), p.x, p.y - 10 - i * 12);
        ctx.globalAlpha = 1;
      });

      if (selectedOverlay === "population") {
        const cellSize = 10;
        for (let gx = 0; gx < map.width; gx += cellSize) {
          for (let gy = 0; gy < map.height; gy += cellSize) {
            const count = citizens.filter(c =>
              Math.floor(c.x / cellSize) === Math.floor(gx / cellSize) &&
              Math.floor(c.y / cellSize) === Math.floor(gy / cellSize)
            ).length;
            if (count > 0) {
              const p1 = worldToScreen(gx, gy);
              const p2 = worldToScreen(gx + cellSize, gy + cellSize);
              ctx.globalAlpha = Math.min(0.5, count * 0.05);
              ctx.fillStyle = count > 10 ? "#ef4444" : count > 5 ? "#f59e0b" : "#22c55e";
              ctx.fillRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y);
              ctx.globalAlpha = 1;
            }
          }
        }
      }

      animFrame.current = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animFrame.current);
  }, [map, citizens, camera, time, events, worldToScreen, followId, selectedOverlay]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setCamera(prev => ({
      ...prev,
      zoom: Math.max(0.3, Math.min(5, prev.zoom * delta)),
    }));
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true);
    dragStart.current = { x: e.clientX, y: e.clientY };
    camStart.current = { x: camera.x, y: camera.y };
  }, [camera]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    const dx = (e.clientX - dragStart.current.x) / (camera.zoom * (map?.tile_size ?? 32));
    const dy = (e.clientY - dragStart.current.y) / (camera.zoom * (map?.tile_size ?? 32));
    setCamera(prev => ({ ...prev, x: camStart.current.x - dx, y: camStart.current.y - dy }));
  }, [isDragging, camera.zoom, map]);

  const handleMouseUp = useCallback(() => setIsDragging(false), []);

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (isDragging) return;
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const sx = e.clientX - rect.left;
    const sy = e.clientY - rect.top;
    const world = screenToWorld(sx, sy);

    let closest: InspectorTarget | null = null;
    let minDist = 5;
    for (const c of citizens) {
      const d = Math.sqrt((c.x - world.x) ** 2 + (c.y - world.y) ** 2);
      if (d < minDist) { minDist = d; closest = { type: "citizen", id: c.agent_id, data: c as unknown as Record<string, unknown> }; }
    }
    for (const b of map?.buildings ?? []) {
      const bx = b.x + b.width / 2;
      const by = b.y + b.height / 2;
      const d = Math.sqrt((bx - world.x) ** 2 + (by - world.y) ** 2);
      if (d < 8) { closest = { type: "building", id: b.id, data: b as unknown as Record<string, unknown> }; break; }
    }
    setInspector(closest);
  }, [isDragging, screenToWorld, citizens, map]);

  const togglePause = async () => {
    if (time?.paused) await fetch(`${API}/time/resume`, { method: "POST" });
    else await fetch(`${API}/time/pause`, { method: "POST" });
  };
  const setSpeed = async (s: number) => { await fetch(`${API}/time/speed?speed=${s}`, { method: "POST" }); };

  const timeDisplay = time ? `${String(time.hour).padStart(2, "0")}:${String(time.minute).padStart(2, "0")} Day ${time.day}` : "--:--";

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      <div className="flex-1 relative">
        <canvas
          ref={canvasRef}
          width={typeof window !== "undefined" ? window.innerWidth - 380 : 1200}
          height={typeof window !== "undefined" ? window.innerHeight : 800}
          className="w-full h-full cursor-grab active:cursor-grabbing"
          onWheel={handleWheel}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onClick={handleCanvasClick}
        />

        <div className="absolute top-4 left-4 flex gap-2 items-center">
          <Card className="bg-gray-900/90 border-gray-700">
            <CardContent className="p-2 flex items-center gap-3">
              <span className="text-sm font-mono">{timeDisplay}</span>
              <Button size="sm" variant={time?.paused ? "default" : "outline"} onClick={togglePause}
                className="h-6 px-2 text-xs">
                {time?.paused ? "Play" : "Pause"}
              </Button>
              {[1, 5, 20, 100].map(s => (
                <Button key={s} size="sm" variant={time?.speed === s ? "default" : "outline"}
                  onClick={() => setSpeed(s)} className="h-6 px-2 text-xs">
                  {s}x
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <Card className="bg-gray-900/90 border-gray-700">
            <CardContent className="p-2 flex flex-col gap-1">
              <span className="text-xs text-gray-400">Zoom: {(camera.zoom * 100).toFixed(0)}%</span>
              <div className="flex gap-1">
                <Button size="sm" className="h-5 px-1 text-xs" onClick={() => setCamera(p => ({ ...p, zoom: Math.min(5, p.zoom * 1.3) }))}>+</Button>
                <Button size="sm" className="h-5 px-1 text-xs" onClick={() => setCamera(p => ({ ...p, zoom: Math.max(0.3, p.zoom / 1.3) }))}>-</Button>
                <Button size="sm" className="h-5 px-1 text-xs" onClick={() => setCamera({ x: 0, y: 0, zoom: 2 })}>Reset</Button>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900/90 border-gray-700">
            <CardContent className="p-2 flex flex-col gap-1">
              <span className="text-xs text-gray-400">Overlay</span>
              {["none", "population", "economic"].map(o => (
                <Button key={o} size="sm" variant={selectedOverlay === o ? "default" : "outline"}
                  onClick={() => setSelectedOverlay(o)} className="h-5 px-2 text-xs capitalize">
                  {o}
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="absolute bottom-4 left-4">
          <Card className="bg-gray-900/90 border-gray-700 max-w-xs">
            <CardContent className="p-2">
              <div className="flex flex-wrap gap-1">
                {Object.entries(STATUS_COLORS).slice(0, 6).map(([s, c]) => (
                  <div key={s} className="flex items-center gap-1 text-xs">
                    <span className="w-2 h-2 rounded-full" style={{ background: c }} />
                    <span className="text-gray-400">{s}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="w-[380px] bg-gray-900 border-l border-gray-700 flex flex-col overflow-hidden">
        <div className="p-3 border-b border-gray-700">
          <CardTitle className="text-sm">World Inspector</CardTitle>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {inspector ? (
            inspector.type === "citizen" ? (
              <CitizenInspector agentId={inspector.id} data={inspector.data as unknown as WorldCitizen}
                onFollow={() => setFollowId(inspector.id)} onUnfollow={() => setFollowId(null)}
                isFollowing={followId === inspector.id} />
            ) : (
              <BuildingInspector data={inspector.data as unknown as WorldBuilding} />
            )
          ) : (
            <div className="text-sm text-gray-400 space-y-3">
              <p>Click a citizen or building to inspect.</p>
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Citizens: {citizens.length}</p>
                <p className="text-xs text-gray-500">Buildings: {map?.buildings.length ?? 0}</p>
                <p className="text-xs text-gray-500">Events: {events.length}</p>
              </div>
            </div>
          )}

          {events.length > 0 && (
            <div className="space-y-1">
              <h3 className="text-xs font-semibold text-gray-400">Recent Events</h3>
              {events.slice(-5).reverse().map((ev, i) => (
                <div key={i} className="text-xs text-gray-300 border-l-2 border-gray-600 pl-2 py-1">
                  {ev.description}
                </div>
              ))}
            </div>
          )}

          <div className="space-y-1">
            <h3 className="text-xs font-semibold text-gray-400">Observer Mode</h3>
            <div className="flex flex-wrap gap-1">
              {["city", "economic", "research", "cinematic"].map(m => (
                <Button key={m} size="sm" variant={observerMode === m ? "default" : "outline"}
                  onClick={() => setObserverMode(m)} className="h-5 px-2 text-xs capitalize">
                  {m}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CitizenInspector({ agentId, data, onFollow, onUnfollow, isFollowing }: {
  agentId: string; data: WorldCitizen; onFollow: () => void; onUnfollow: () => void; isFollowing: boolean;
}) {
  const statusColor = STATUS_COLORS[data.status] || "#9ca3af";
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold">{agentId.slice(0, 8)}</h3>
        <Button size="sm" variant={isFollowing ? "default" : "outline"} onClick={isFollowing ? onUnfollow : onFollow}
          className="h-5 px-2 text-xs">
          {isFollowing ? "Unfollow" : "Follow"}
        </Button>
      </div>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between"><span className="text-gray-400">Status</span>
          <Badge className="text-xs" style={{ background: statusColor }}>{data.status}</Badge></div>
        <div className="flex justify-between"><span className="text-gray-400">Position</span>
          <span>{data.x.toFixed(1)}, {data.y.toFixed(1)}</span></div>
        {data.destination && <div className="flex justify-between"><span className="text-gray-400">Destination</span>
          <span>{data.destination}</span></div>}
        {data.thought && <div className="mt-2 p-2 bg-gray-800 rounded text-xs italic text-gray-300">"{data.thought}"</div>}
      </div>
    </div>
  );
}

function BuildingInspector({ data }: { data: WorldBuilding }) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-bold">{data.name}</h3>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between"><span className="text-gray-400">Type</span><span className="capitalize">{data.type}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Zone</span><span className="capitalize">{data.zone}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Employees</span><span>{data.employee_count}/{data.capacity}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Visitors</span><span>{data.visitor_count}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Activity</span><span>{data.activity}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Position</span><span>{data.x}, {data.y}</span></div>
      </div>
    </div>
  );
}
