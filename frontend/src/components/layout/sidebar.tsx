"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import {
  LayoutDashboard,
  Bot,
  CheckSquare,
  Building2,
  Globe,
  Globe2,
  Heart,
  Cpu,
  Mountain,
  Clock,
  BrainCircuit,
  Puzzle,
  Eye,
  Shield,
  LogOut,
  ScrollText,
  Network,
  FlaskConical,
  Zap,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/genesis", label: "Genesis", icon: ScrollText },
  { href: "/world", label: "Living World", icon: Globe },
  { href: "/explore", label: "3D Explorer", icon: Eye },
  { href: "/planetary", label: "Planet", icon: Mountain },
  { href: "/federation", label: "Federation", icon: Globe2 },
  { href: "/culture", label: "Culture", icon: Heart },
  { href: "/technology", label: "Technology", icon: Cpu },
  { href: "/temporal", label: "Time & History", icon: Clock },
  { href: "/meta", label: "Meta Intelligence", icon: BrainCircuit },
  { href: "/platform", label: "Platform", icon: Puzzle },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/tasks", label: "Tasks", icon: CheckSquare },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/network", label: "Compute", icon: Network },
  { href: "/research", label: "Research", icon: FlaskConical },
  { href: "/admin", label: "Admin", icon: Shield },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-60 flex-col border-r bg-card">
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          <span className="text-base font-bold tracking-tight">NEXUS</span>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-3">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-xs font-semibold">
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.username}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
