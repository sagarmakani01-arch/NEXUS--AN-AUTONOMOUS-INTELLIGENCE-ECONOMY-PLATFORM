"use client";

import { useAuth } from "@/lib/auth";

export function Header() {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center border-b bg-card/80 backdrop-blur-sm px-6">
      <div className="flex-1" />
      <div className="flex items-center gap-4">
        <span className="text-xs text-muted-foreground font-mono">
          {new Date().toLocaleDateString("en-US", {
            weekday: "short",
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </span>
      </div>
    </header>
  );
}
