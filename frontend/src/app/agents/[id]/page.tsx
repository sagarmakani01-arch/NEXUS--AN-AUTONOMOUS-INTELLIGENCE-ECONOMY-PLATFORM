"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AgentProfile as AgentProfileType } from "@/types";
import { ArrowLeft, Bot, Brain, Target, BookOpen, Users, Clock, Zap, Shield, Lightbulb, ListChecks, Wallet, TrendingUp, Coins, PieChart } from "lucide-react";

export default function AgentProfilePage() {
  const { token } = useAuth();
  const params = useParams();
  const router = useRouter();
  const agentId = params.id as string;
  
  const [profile, setProfile] = useState<AgentProfileType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !agentId) return;
    fetchProfile();
  }, [token, agentId]);

  async function fetchProfile() {
    try {
      setLoading(true);
      const data = await api.get<AgentProfileType>(`/agents/${agentId}`, token!);
      setProfile(data);
    } catch (err) {
      console.error("Failed to fetch agent profile:", err);
      setError("Failed to load agent profile");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center py-24">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-border border-t-foreground" />
        </div>
      </AppLayout>
    );
  }

  if (error || !profile) {
    return (
      <AppLayout>
        <div className="space-y-6">
          <Button variant="ghost" size="sm" onClick={() => router.push("/agents")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Agents
          </Button>
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Bot className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-sm font-medium">{error || "Agent not found"}</p>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    );
  }

  const statusColors: Record<string, string> = {
    idle: "bg-amber-500/10 text-amber-600",
    working: "bg-blue-500/10 text-blue-600",
    resting: "bg-purple-500/10 text-purple-600",
    searching: "bg-cyan-500/10 text-cyan-600",
  };

  const getPersonalityBar = (value: number) => {
    if (value >= 70) return "bg-emerald-500";
    if (value >= 40) return "bg-amber-500";
    return "bg-red-500";
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => router.push("/agents")}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">
                {profile.identity?.display_name || profile.name}
              </h1>
              <p className="text-sm text-muted-foreground">
                {profile.identity?.profession} • Generation {profile.identity?.generation}
              </p>
            </div>
          </div>
          <Badge className={`text-xs ${statusColors[profile.current_status] || ""}`}>
            {profile.current_status}
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <Zap className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Energy</p>
                  <p className="text-lg font-semibold">{profile.energy.toFixed(0)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <Shield className="h-5 w-5 text-emerald-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Trust Score</p>
                  <p className="text-lg font-semibold">{profile.trust_score.toFixed(0)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <Zap className="h-5 w-5 text-amber-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Reputation</p>
                  <p className="text-lg font-semibold">{profile.reputation.toFixed(1)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <Target className="h-5 w-5 text-purple-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Wallet</p>
                  <p className="text-lg font-semibold">{profile.wallet_balance.toFixed(0)} NXC</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Brain className="h-4 w-4" />
                  Personality Profile
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {profile.personality && (
                  <>
                    <div className="space-y-3">
                      {Object.entries(profile.personality)
                        .filter(([key]) => !["traits", "communication_style", "work_style"].includes(key))
                        .map(([trait, value]) => (
                          <div key={trait} className="space-y-1">
                            <div className="flex items-center justify-between text-sm">
                              <span className="capitalize">{trait.replace(/_/g, " ")}</span>
                              <span className="text-muted-foreground">{value}%</span>
                            </div>
                            <div className="h-2 rounded-full bg-secondary overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all ${getPersonalityBar(value as number)}`}
                                style={{ width: `${value}%` }}
                              />
                            </div>
                          </div>
                        ))}
                    </div>
                    {profile.personality.traits && profile.personality.traits.length > 0 && (
                      <div className="pt-2 border-t">
                        <p className="text-xs text-muted-foreground mb-2">Key Traits</p>
                        <div className="flex flex-wrap gap-2">
                          {profile.personality.traits.map((trait, i) => (
                            <Badge key={i} className="text-xs">
                              {trait}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Communication Style</p>
                        <p className="text-sm">{profile.personality.communication_style}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Work Style</p>
                        <p className="text-sm">{profile.personality.work_style}</p>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  Current Goal
                </CardTitle>
              </CardHeader>
              <CardContent>
                {profile.goal ? (
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium">{profile.goal.title}</p>
                      <p className="text-xs text-muted-foreground capitalize">{profile.goal.category}</p>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span>Progress</span>
                        <span className="text-muted-foreground">
                          {profile.goal.progress} / {profile.goal.target}
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-secondary overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full transition-all"
                          style={{ width: `${(profile.goal.progress / profile.goal.target) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No active goal</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BookOpen className="h-4 w-4" />
                  Skills
                </CardTitle>
              </CardHeader>
              <CardContent>
                {profile.skills && profile.skills.length > 0 ? (
                  <div className="space-y-3">
                    {profile.skills.map((skill, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-md bg-secondary flex items-center justify-center text-xs font-medium">
                            L{skill.level}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{skill.skill_name}</p>
                            <p className="text-xs text-muted-foreground">
                              {skill.experience} / {skill.max_experience} XP
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 rounded-full bg-secondary overflow-hidden">
                            <div
                              className="h-full bg-emerald-500 rounded-full transition-all"
                              style={{ width: `${skill.learning_progress}%` }}
                            />
                          </div>
                          {skill.certified && (
                            <Badge className="text-xs">Certified</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No skills learned yet</p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Relationships
                </CardTitle>
              </CardHeader>
              <CardContent>
                {profile.relationships && profile.relationships.length > 0 ? (
                  <div className="space-y-3">
                    {profile.relationships.map((rel, i) => (
                      <div key={i} className="p-3 rounded-lg bg-secondary/50">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="text-sm font-medium">{rel.other_name}</p>
                            <p className="text-xs text-muted-foreground">{rel.other_profession}</p>
                          </div>
                          <Badge className="text-xs">
                            {rel.strength >= 70 ? "Strong" : rel.strength >= 40 ? "Moderate" : "Weak"}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div>
                            <p className="text-muted-foreground">Trust</p>
                            <p className="font-medium">{rel.trust}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Respect</p>
                            <p className="font-medium">{rel.respect}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Strength</p>
                            <p className="font-medium">{rel.strength}</p>
                          </div>
                        </div>
                        <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                          <span>{rel.collaboration_count} collabs</span>
                          <span>{rel.conflict_count} conflicts</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No relationships yet</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                {profile.timeline && profile.timeline.length > 0 ? (
                  <div className="space-y-3">
                    {profile.timeline.slice(0, 10).map((event, i) => (
                      <div key={i} className="flex gap-3">
                        <div className="flex flex-col items-center">
                          <div className="h-2 w-2 rounded-full bg-foreground" />
                          {i < profile.timeline.length - 1 && <div className="w-px h-full bg-border" />}
                        </div>
                        <div className="pb-4">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium">{event.title}</p>
                            <Badge className="text-xs">Day {event.day}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">{event.description}</p>
                          <p className="text-xs text-muted-foreground capitalize mt-1">{event.event_type}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No timeline events</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Lightbulb className="h-4 w-4" />
              Cognitive Reasoning
            </CardTitle>
          </CardHeader>
          <CardContent>
            {profile.reasoning ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <p className="text-xs text-muted-foreground">Status</p>
                    <Badge className={`mt-1 text-xs ${
                      profile.reasoning.reasoning_status === "idle" ? "bg-emerald-500/10 text-emerald-600" :
                      profile.reasoning.reasoning_status === "reasoning" ? "bg-blue-500/10 text-blue-600" :
                      profile.reasoning.reasoning_status === "queued" ? "bg-amber-500/10 text-amber-600" :
                      "bg-secondary"
                    }`}>
                      {profile.reasoning.reasoning_status}
                    </Badge>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <p className="text-xs text-muted-foreground">Total Decisions</p>
                    <p className="text-lg font-semibold">{profile.reasoning.total_decisions}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <p className="text-xs text-muted-foreground">Reflections</p>
                    <p className="text-lg font-semibold">{profile.reasoning.total_reflections}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <p className="text-xs text-muted-foreground">Provider</p>
                    <p className="text-sm font-medium">{profile.reasoning.provider_used}</p>
                  </div>
                </div>

                {profile.reasoning.current_decision && (
                  <div className="p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium">Latest Decision</p>
                      <div className="flex items-center gap-2">
                        <Badge className={`text-xs ${
                          profile.reasoning.current_decision.risk_level === "low" ? "bg-emerald-500/10 text-emerald-600" :
                          profile.reasoning.current_decision.risk_level === "high" ? "bg-red-500/10 text-red-600" :
                          "bg-amber-500/10 text-amber-600"
                        }`}>
                          {profile.reasoning.current_decision.risk_level} risk
                        </Badge>
                        <Badge className="text-xs">
                          {Math.round(profile.reasoning.current_decision.confidence * 100)}% confidence
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm">{profile.reasoning.current_decision.decision}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {profile.reasoning.current_decision.reasoning_summary}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>Cost: {profile.reasoning.current_decision.estimated_cost.toFixed(0)} NXC</span>
                      <span>Reward: {profile.reasoning.current_decision.estimated_reward.toFixed(0)} NXC</span>
                      <span>Time: {profile.reasoning.current_decision.reasoning_duration_ms.toFixed(0)}ms</span>
                    </div>
                  </div>
                )}

                {profile.reasoning.current_plan && (
                  <div className="p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium flex items-center gap-2">
                        <ListChecks className="h-4 w-4" />
                        Active Plan
                      </p>
                      <Badge className={`text-xs ${
                        profile.reasoning.current_plan.status === "completed" ? "bg-emerald-500/10 text-emerald-600" :
                        profile.reasoning.current_plan.status === "active" ? "bg-blue-500/10 text-blue-600" :
                        "bg-secondary"
                      }`}>
                        {profile.reasoning.current_plan.status}
                      </Badge>
                    </div>
                    <p className="text-sm font-medium">{profile.reasoning.current_plan.goal}</p>
                    <div className="mt-2 space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span>Progress</span>
                        <span className="text-muted-foreground">{profile.reasoning.current_plan.progress.toFixed(0)}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full transition-all"
                          style={{ width: `${profile.reasoning.current_plan.progress}%` }}
                        />
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-muted-foreground">
                      {profile.reasoning.current_plan.milestones.filter((m: { completed: boolean }) => m.completed).length} / {profile.reasoning.current_plan.milestones.length} milestones completed
                    </div>
                  </div>
                )}

                {profile.reasoning.last_reasoning_duration_ms > 0 && (
                  <div className="text-xs text-muted-foreground">
                    Last reasoning: {profile.reasoning.last_reasoning_duration_ms.toFixed(0)}ms
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No reasoning data yet. Start the simulation to enable cognitive reasoning.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Wallet className="h-4 w-4" />
              Financial Resources
            </CardTitle>
          </CardHeader>
          <CardContent>
            {profile.resources && profile.resources.wallet ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <div className="flex items-center gap-2 mb-1">
                      <Coins className="h-4 w-4 text-amber-500" />
                      <p className="text-xs text-muted-foreground">Balance</p>
                    </div>
                    <p className="text-lg font-semibold">{profile.resources.wallet.wallet_balance.toFixed(0)} NXC</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <div className="flex items-center gap-2 mb-1">
                      <Brain className="h-4 w-4 text-blue-500" />
                      <p className="text-xs text-muted-foreground">Compute</p>
                    </div>
                    <p className="text-lg font-semibold">{profile.resources.compute.compute_credits}</p>
                    <p className="text-xs text-muted-foreground">credits</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp className="h-4 w-4 text-emerald-500" />
                      <p className="text-xs text-muted-foreground">Net Worth</p>
                    </div>
                    <p className="text-lg font-semibold">{profile.resources.wallet.net_worth.toFixed(0)} NXC</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50">
                    <div className="flex items-center gap-2 mb-1">
                      <Shield className={`h-4 w-4 ${
                        profile.resources.wallet.financial_health === "excellent" ? "text-emerald-500" :
                        profile.resources.wallet.financial_health === "good" ? "text-blue-500" :
                        profile.resources.wallet.financial_health === "fair" ? "text-amber-500" :
                        "text-red-500"
                      }`} />
                      <p className="text-xs text-muted-foreground">Health</p>
                    </div>
                    <Badge className={`text-xs ${
                      profile.resources.wallet.financial_health === "excellent" ? "bg-emerald-500/10 text-emerald-600" :
                      profile.resources.wallet.financial_health === "good" ? "bg-blue-500/10 text-blue-600" :
                      profile.resources.wallet.financial_health === "fair" ? "bg-amber-500/10 text-amber-600" :
                      "bg-red-500/10 text-red-600"
                    }`}>
                      {profile.resources.wallet.financial_health}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg border">
                    <p className="text-sm font-medium mb-2">Earnings Summary</p>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Total Earned</span>
                        <span className="text-emerald-600">{profile.resources.wallet.total_earned.toFixed(0)} NXC</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Total Spent</span>
                        <span className="text-red-600">{profile.resources.wallet.total_spent.toFixed(0)} NXC</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Reserved</span>
                        <span>{profile.resources.wallet.reserved_balance.toFixed(0)} NXC</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Assets Value</span>
                        <span>{profile.resources.wallet.asset_value.toFixed(0)} NXC</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-lg border">
                    <p className="text-sm font-medium mb-2">Today&apos;s Activity</p>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Income</span>
                        <span className="text-emerald-600">+{profile.resources.daily.income.toFixed(0)} NXC</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Expenses</span>
                        <span className="text-red-600">-{profile.resources.daily.expenses.toFixed(0)} NXC</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Net</span>
                        <span className={profile.resources.daily.net >= 0 ? "text-emerald-600" : "text-red-600"}>
                          {profile.resources.daily.net >= 0 ? "+" : ""}{profile.resources.daily.net.toFixed(0)} NXC
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Compute Used</span>
                        <span>{profile.resources.daily.compute_used}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg border">
                  <p className="text-sm font-medium mb-2">Resource Allocation</p>
                  <div className="flex h-3 rounded-full overflow-hidden bg-secondary">
                    <div
                      className="bg-amber-500 transition-all"
                      style={{ width: `${profile.resources.allocation.cash_allocation}%` }}
                      title={`Cash: ${profile.resources.allocation.cash_allocation}%`}
                    />
                    <div
                      className="bg-blue-500 transition-all"
                      style={{ width: `${profile.resources.allocation.asset_allocation}%` }}
                      title={`Assets: ${profile.resources.allocation.asset_allocation}%`}
                    />
                    <div
                      className="bg-purple-500 transition-all"
                      style={{ width: `${profile.resources.allocation.compute_allocation}%` }}
                      title={`Compute: ${profile.resources.allocation.compute_allocation}%`}
                    />
                  </div>
                  <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-amber-500" /> Cash {profile.resources.allocation.cash_allocation}%
                    </span>
                    <span className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-blue-500" /> Assets {profile.resources.allocation.asset_allocation}%
                    </span>
                    <span className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-purple-500" /> Compute {profile.resources.allocation.compute_allocation}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No financial data yet. Start the simulation to initialize wallets.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Recent Memories
            </CardTitle>
          </CardHeader>
          <CardContent>
            {profile.memories && profile.memories.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {profile.memories.map((memory, i) => (
                  <div key={i} className="p-3 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className="text-xs">{memory.category}</Badge>
                      <Badge 
                        
                        className={`text-xs ${
                          memory.importance === "high" ? "bg-red-500/10" : 
                          memory.importance === "medium" ? "bg-amber-500/10" : 
                          "bg-secondary"
                        }`}
                      >
                        {memory.importance}
                      </Badge>
                    </div>
                    <p className="text-sm font-medium">{memory.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{memory.description}</p>
                    {memory.related_agent_id && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Related: {memory.related_agent_id.slice(0, 8)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No memories yet</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
