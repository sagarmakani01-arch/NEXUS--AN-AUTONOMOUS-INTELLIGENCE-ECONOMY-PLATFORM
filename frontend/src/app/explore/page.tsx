"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Eye, Move, ZoomIn, ZoomOut, RotateCcw, MapPin, Building2, Users, Activity } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TILE_SIZE = 8;
const BUILDING_COLORS: Record<string, string> = {
  house: "#4a90d9", apartment: "#5a9fe6", factory: "#8b7355", lab: "#e8e8e8",
  office: "#6b5b45", university: "#00d4aa", government: "#d4c4a0", market: "#f0e0c0",
  park: "#90ee90", road: "#666",
};

interface Building {
  id: string; type: string; label: string; x: number; y: number; z: number;
  w: number; h: number; d: number; color: string; occupants: number;
}

interface Entity {
  id: string; name: string; x: number; z: number; activity: string;
}

export default function ExplorePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [camX, setCamX] = useState(0);
  const [camZ, setCamZ] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [entities, setEntities] = useState<Entity[]>([]);
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [regionInfo, setRegionInfo] = useState<string>("");
  const [mouseDown, setMouseDown] = useState(false);
  const [lastMouse, setLastMouse] = useState({ x: 0, y: 0 });

  const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (token) h["Authorization"] = `Bearer ${token}`;
    return h;
  };

  const loadRegion = useCallback(async (rx: number, rz: number) => {
    try {
      const res = await fetch(`${API}/api/v1/reality/regions/${rx}/${rz}`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setBuildings(data.buildings || []);
        setEntities(data.entities?.map((e: any) => ({ id: e.id, name: e.name || "Citizen", x: e.x, z: e.z, activity: e.activity })) || []);
        setRegionInfo(`Region (${rx}, ${rz}) — ${data.biome || "unknown"}`);
      }
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => {
    loadRegion(0, 0);
    const iv = setInterval(() => { if (camX === 0 && camZ === 0) loadRegion(0, 0); }, 5000);
    return () => clearInterval(iv);
  }, [loadRegion, camX, camZ]);

  const cameraControls = {
    left: () => { setCamX(c => c - 10); const rx = Math.floor((camX - 10) / 100); if (rx !== Math.floor(camX / 100)) loadRegion(rx, Math.floor(camZ / 100)); },
    right: () => { setCamX(c => c + 10); const rx = Math.floor((camX + 10) / 100); if (rx !== Math.floor(camX / 100)) loadRegion(rx, Math.floor(camZ / 100)); },
    up: () => { setCamZ(c => c - 10); const rz = Math.floor((camZ - 10) / 100); if (rz !== Math.floor(camZ / 100)) loadRegion(Math.floor(camX / 100), rz); },
    down: () => { setCamZ(c => c + 10); const rz = Math.floor((camZ + 10) / 100); if (rz !== Math.floor(camZ / 100)) loadRegion(Math.floor(camX / 100), rz); },
    zoomIn: () => setZoom(z => Math.min(3, z + 0.2)),
    zoomOut: () => setZoom(z => Math.max(0.3, z - 0.2)),
    reset: () => { setCamX(0); setCamZ(0); setZoom(1); loadRegion(0, 0); },
  };

  const isometricProject = (x: number, y: number, z: number, w: number, h: number, d: number) => {
    const sx = (x - z) * TILE_SIZE * zoom + 400;
    const sy = (x + z) * TILE_SIZE * 0.5 * zoom - y * TILE_SIZE * zoom + 100;
    const sw = (w + d) * TILE_SIZE * zoom;
    return { sx, sy, sw };
  };

  const drawScene = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#1a1a2e";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const gridSize = 20;
    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.lineWidth = 1;
    for (let i = -gridSize; i <= gridSize; i++) {
      const p = isometricProject(i * 5 + camX, 0, -gridSize * 5 + camZ, 0, 0, 0);
      const p2 = isometricProject(i * 5 + camX, 0, gridSize * 5 + camZ, 0, 0, 0);
      ctx.beginPath(); ctx.moveTo(p.sx, p.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke();
    }
    for (let i = -gridSize; i <= gridSize; i++) {
      const p = isometricProject(-gridSize * 5 + camX, 0, i * 5 + camZ, 0, 0, 0);
      const p2 = isometricProject(gridSize * 5 + camX, 0, i * 5 + camZ, 0, 0, 0);
      ctx.beginPath(); ctx.moveTo(p.sx, p.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke();
    }

    const sorted = [...buildings].sort((a, b) => (a.x + a.z) - (b.x + b.z));
    for (const b of sorted) {
      const { sx, sy } = isometricProject(b.x + camX, b.h / 2, b.z + camZ, b.w, b.h, b.d);
      const bw = (b.w + b.d) * TILE_SIZE * zoom * 0.5;
      const bh = b.h * TILE_SIZE * zoom * 0.8;

      ctx.fillStyle = b.color || BUILDING_COLORS[b.type] || "#4a90d9";
      ctx.fillRect(sx - bw / 2, sy - bh, bw, bh);

      ctx.strokeStyle = "rgba(255,255,255,0.3)";
      ctx.lineWidth = 1;
      ctx.strokeRect(sx - bw / 2, sy - bh, bw, bh);

      if (b.occupants > 0 && zoom > 0.8) {
        ctx.fillStyle = "rgba(255,255,255,0.6)";
        ctx.font = "8px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`${b.occupants}`, sx, sy - bh - 2);
      }
    }

    for (const e of entities) {
      const { sx, sy } = isometricProject(e.x + camX, 0.5, e.z + camZ, 0, 0, 0);
      const r = 3 * zoom;

      ctx.beginPath();
      ctx.arc(sx, sy, r, 0, Math.PI * 2);
      ctx.fillStyle = e.activity === "working" ? "#00ff88" : e.activity === "resting" ? "#ffaa00" : "#00ccff";
      ctx.fill();

      ctx.strokeStyle = "rgba(255,255,255,0.5)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    ctx.fillStyle = "rgba(255,255,255,0.3)";
    ctx.font = "10px monospace";
    ctx.textAlign = "left";
    ctx.fillText(`Region: ${regionInfo}`, 10, 20);
    ctx.fillText(`Buildings: ${buildings.length}`, 10, 35);
    ctx.fillText(`Citizens: ${entities.length}`, 10, 50);
    ctx.fillText(`Zoom: ${zoom.toFixed(1)}x`, 10, 65);
  }, [buildings, entities, camX, camZ, zoom, regionInfo]);

  useEffect(() => {
    drawScene();
    let anim: number;
    const animate = () => { drawScene(); anim = requestAnimationFrame(animate); };
    anim = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(anim);
  }, [drawScene]);

  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    setMouseDown(true);
    setLastMouse({ x: e.clientX, y: e.clientY });
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!mouseDown) return;
    const dx = e.clientX - lastMouse.x;
    const dy = e.clientY - lastMouse.y;
    setCamX(c => c - dx * 0.5);
    setCamZ(c => c - dy * 0.5);
    setLastMouse({ x: e.clientX, y: e.clientY });
  };

  const handleCanvasMouseUp = () => setMouseDown(false);

  const handleCanvasClick = (e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    for (const b of buildings) {
      const { sx, sy } = isometricProject(b.x + camX, b.h / 2, b.z + camZ, b.w, b.h, b.d);
      const bw = (b.w + b.d) * TILE_SIZE * zoom * 0.5;
      const bh = b.h * TILE_SIZE * zoom * 0.8;
      if (mx >= sx - bw / 2 && mx <= sx + bw / 2 && my >= sy - bh && my <= sy) {
        setSelectedBuilding(b);
        return;
      }
    }
    setSelectedBuilding(null);
  };

  return (
    <AppLayout>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Eye className="h-8 w-8" />
              3D Explorer
            </h1>
            <p className="text-muted-foreground mt-1">Immersive 3D view of the simulation world</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={cameraControls.left} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><Move className="h-4 w-4" /></button>
            <button onClick={cameraControls.up} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><Move className="h-4 w-4 rotate-90" /></button>
            <button onClick={cameraControls.down} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><Move className="h-4 w-4 -rotate-90" /></button>
            <button onClick={cameraControls.right} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><Move className="h-4 w-4 rotate-180" /></button>
            <button onClick={cameraControls.zoomIn} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><ZoomIn className="h-4 w-4" /></button>
            <button onClick={cameraControls.zoomOut} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><ZoomOut className="h-4 w-4" /></button>
            <button onClick={cameraControls.reset} className="rounded-md bg-secondary p-2 hover:bg-secondary/80"><RotateCcw className="h-4 w-4" /></button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
          <div className="lg:col-span-3 rounded-lg border bg-card overflow-hidden">
            <canvas
              ref={canvasRef}
              width={800}
              height={500}
              className="w-full h-[500px] cursor-grab active:cursor-grabbing"
              onMouseDown={handleCanvasMouseDown}
              onMouseMove={handleCanvasMouseMove}
              onMouseUp={handleCanvasMouseUp}
              onMouseLeave={handleCanvasMouseUp}
              onClick={handleCanvasClick}
            />
          </div>

          <div className="space-y-3">
            <div className="rounded-lg border bg-card p-3">
              <h3 className="font-semibold text-sm flex items-center gap-2 mb-2"><MapPin className="h-4 w-4" /> Location</h3>
              <div className="text-xs text-muted-foreground">{regionInfo || "No region loaded"}</div>
            </div>

            <div className="rounded-lg border bg-card p-3">
              <h3 className="font-semibold text-sm flex items-center gap-2 mb-2"><Building2 className="h-4 w-4" /> {selectedBuilding ? selectedBuilding.label || "Building" : "Select a Building"}</h3>
              {selectedBuilding ? (
                <div className="text-xs space-y-1">
                  <div><span className="text-muted-foreground">Type:</span> {selectedBuilding.type}</div>
                  <div><span className="text-muted-foreground">Style:</span> {selectedBuilding.color}</div>
                  <div><span className="text-muted-foreground">Occupants:</span> {selectedBuilding.occupants}</div>
                  <div><span className="text-muted-foreground">Position:</span> ({selectedBuilding.x.toFixed(0)}, {selectedBuilding.z.toFixed(0)})</div>
                </div>
              ) : (
                <div className="text-xs text-muted-foreground">Click a building to inspect</div>
              )}
            </div>

            <div className="rounded-lg border bg-card p-3">
              <h3 className="font-semibold text-sm flex items-center gap-2 mb-2"><Users className="h-4 w-4" /> Nearby Citizens</h3>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {entities.slice(0, 10).map((e) => (
                  <div key={e.id} className="flex items-center gap-2 text-xs">
                    <Activity className="h-3 w-3 text-muted-foreground" />
                    <span className="truncate">{e.name}</span>
                    <span className="text-muted-foreground ml-auto">{e.activity}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border bg-card p-3">
              <h3 className="font-semibold text-sm mb-2">Controls</h3>
              <div className="text-xs text-muted-foreground space-y-1">
                <div>Drag to pan · Click building to inspect</div>
                <div>Scroll to zoom · Arrow buttons to navigate</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
