"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { SimulationState } from "@/types";

export function useSimulation() {
  const [simState, setSimState] = useState<SimulationState | null>(null);
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const es = new EventSource("/api/v1/simulation/stream");
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "world" || data.type === "state_change") {
          if (data.data?.world || data.data?.state) {
            setSimState(data.data as SimulationState);
          }
        }
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      setConnected(false);
      setTimeout(() => connect(), 3000);
    };

    es.onopen = () => {
      setConnected(true);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      eventSourceRef.current?.close();
    };
  }, [connect]);

  const start = useCallback(async () => {
    await fetch("/api/v1/simulation/start", { method: "POST" });
  }, []);

  const pause = useCallback(async () => {
    await fetch("/api/v1/simulation/pause", { method: "POST" });
  }, []);

  const reset = useCallback(async () => {
    await fetch("/api/v1/simulation/reset", { method: "POST" });
    setSimState(null);
  }, []);

  const setSpeed = useCallback(async (speed: number) => {
    await fetch(`/api/v1/simulation/speed?speed=${speed}`, { method: "POST" });
  }, []);

  return { simState, connected, start, pause, reset, setSpeed };
}
