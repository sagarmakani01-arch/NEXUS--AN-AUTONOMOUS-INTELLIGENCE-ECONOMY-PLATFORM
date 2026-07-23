"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { SimAgent } from "@/types";
import { Plus, Bot, Trash2, Zap, Search, ExternalLink } from "lucide-react";

interface AgentWithIdentity extends SimAgent {
  identity?: {
    first_name: string;
    last_name: string;
    display_name: string;
    generation: number;
    status: string;
    profession: string;
    profession_category: string;
  };
  trust_score?: number;
}

interface SearchParams {
  q?: string;
  profession?: string;
  status?: string;
}

export default function AgentsPage() {
  const { token } = useAuth();
  const [agents, setAgents] = useState<AgentWithIdentity[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newGoal, setNewGoal] = useState("");
  const [creating, setCreating] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchProfession, setSearchProfession] = useState("");
  const [searchStatus, setSearchStatus] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const fetchAgents = useCallback(async (params: SearchParams = {}) => {
    setLoading(true);
    try {
      let data: AgentWithIdentity[];
      const hasParams = params.q || params.profession || params.status;
      
      if (hasParams) {
        const queryParams = new URLSearchParams();
        if (params.q) queryParams.set("q", params.q);
        if (params.profession) queryParams.set("profession", params.profession);
        if (params.status) queryParams.set("status", params.status);
        data = await api.get<AgentWithIdentity[]>(`/agents/search?${queryParams.toString()}`, token!);
      } else {
        data = await api.get<AgentWithIdentity[]>("/agents/", token!);
      }
      
      setAgents(data);
    } catch (err) {
      console.error("Failed to fetch agents:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) fetchAgents();
  }, [token, fetchAgents]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery || searchProfession || searchStatus) {
        setIsSearching(true);
        fetchAgents({
          q: searchQuery || undefined,
          profession: searchProfession || undefined,
          status: searchStatus || undefined,
        });
      } else if (isSearching) {
        fetchAgents();
        setIsSearching(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, searchProfession, searchStatus, fetchAgents, isSearching]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const agent = await api.post<AgentWithIdentity>(
        "/agents/",
        { name: newName, current_goal: newGoal || null },
        token!
      );
      setAgents((prev) => [agent, ...prev]);
      setNewName("");
      setNewGoal("");
      setShowCreate(false);
    } catch (err) {
      console.error("Failed to create agent:", err);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(agentId: string) {
    if (!confirm("Are you sure you want to delete this agent?")) return;
    try {
      await api.delete(`/agents/${agentId}`, token!);
      setAgents((prev) => prev.filter((a) => a.id !== agentId));
    } catch (err) {
      console.error("Failed to delete agent:", err);
    }
  }

  const statusColors: Record<string, string> = {
    idle: "bg-amber-500/10 text-amber-600",
    working: "bg-blue-500/10 text-blue-600",
    resting: "bg-purple-500/10 text-purple-600",
    searching: "bg-cyan-500/10 text-cyan-600",
    active: "bg-emerald-500/10 text-emerald-600",
    error: "bg-red-500/10 text-red-600",
  };

  const professions = [
    "Software Engineer", "Data Scientist", "Designer", "Marketer",
    "Project Manager", "Researcher", "Consultant", "Analyst",
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Agents</h1>
            <p className="text-sm text-muted-foreground">Browse and manage AI agent identities</p>
          </div>
          <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
            <Plus className="mr-1 h-4 w-4" />
            New Agent
          </Button>
        </div>

        {showCreate && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Create Agent</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="flex gap-4 items-end">
                <div className="flex-1 space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    placeholder="Agent name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    required
                  />
                </div>
                <div className="flex-1 space-y-2">
                  <Label htmlFor="goal">Current Goal</Label>
                  <Input
                    id="goal"
                    placeholder="Optional goal"
                    value={newGoal}
                    onChange={(e) => setNewGoal(e.target.value)}
                  />
                </div>
                <Button type="submit" disabled={creating}>
                  {creating ? "Creating..." : "Create"}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Search className="h-4 w-4" />
              Search Agents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="search-name">Name</Label>
                <Input
                  id="search-name"
                  placeholder="Search by name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="search-profession">Profession</Label>
                <select
                  id="search-profession"
                  value={searchProfession}
                  onChange={(e) => setSearchProfession(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="">All Professions</option>
                  {professions.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="search-status">Status</Label>
                <select
                  id="search-status"
                  value={searchStatus}
                  onChange={(e) => setSearchStatus(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="">All Statuses</option>
                  <option value="idle">Idle</option>
                  <option value="working">Working</option>
                  <option value="resting">Resting</option>
                  <option value="searching">Searching</option>
                </select>
              </div>
            </div>
            {(searchQuery || searchProfession || searchStatus) && (
              <Button
                variant="ghost"
                size="sm"
                className="mt-3"
                onClick={() => {
                  setSearchQuery("");
                  setSearchProfession("");
                  setSearchStatus("");
                }}
              >
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-foreground" />
              </div>
            ) : agents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Bot className="h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm font-medium">No agents found</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {isSearching ? "Try adjusting your search filters" : "Create your first AI agent to get started"}
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Agent</TableHead>
                    <TableHead>Profession</TableHead>
                    <TableHead>Gen</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Energy</TableHead>
                    <TableHead>Trust</TableHead>
                    <TableHead>Reputation</TableHead>
                    <TableHead className="w-[80px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agents.map((agent) => (
                    <TableRow key={agent.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-secondary text-xs font-semibold">
                            {(agent.identity?.display_name || agent.name).charAt(0)}
                          </div>
                          <div>
                            <p className="text-sm font-medium">
                              {agent.identity?.display_name || agent.name}
                            </p>
                            <p className="text-xs text-muted-foreground font-mono">{agent.id.slice(0, 8)}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{agent.identity?.profession || "—"}</span>
                      </TableCell>
                      <TableCell>
                        <Badge className="text-xs">
                          Gen {agent.identity?.generation || 1}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${statusColors[agent.current_status] || ""}`}>
                          {agent.current_status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-20 rounded-full bg-secondary overflow-hidden">
                            <div
                              className="h-full bg-foreground rounded-full transition-all"
                              style={{ width: `${agent.energy}%` }}
                            />
                          </div>
                          <span className="text-xs tabular-nums text-muted-foreground">{agent.energy}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <div className="h-1.5 w-12 rounded-full bg-secondary overflow-hidden">
                            <div
                              className="h-full bg-emerald-500 rounded-full transition-all"
                              style={{ width: `${agent.trust_score || 50}%` }}
                            />
                          </div>
                          <span className="text-xs tabular-nums text-muted-foreground">{(agent.trust_score || 50).toFixed(0)}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Zap className="h-3 w-3 text-muted-foreground" />
                          <span className="text-sm tabular-nums">{agent.reputation.toFixed(1)}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Link href={`/agents/${agent.id}`}>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleDelete(agent.id)}
                          >
                            <Trash2 className="h-3.5 w-3.5 text-muted-foreground" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
