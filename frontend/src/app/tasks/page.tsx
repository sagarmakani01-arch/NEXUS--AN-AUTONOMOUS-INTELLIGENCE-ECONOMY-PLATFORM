"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Task } from "@/types";
import { Plus, CheckSquare } from "lucide-react";

export default function TasksPage() {
  const { token } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newReward, setNewReward] = useState("0");
  const [newPriority, setNewPriority] = useState("medium");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetchTasks();
  }, [token]);

  async function fetchTasks() {
    try {
      const data = await api.get<Task[]>("/tasks/", token!);
      setTasks(data);
    } catch (err) {
      console.error("Failed to fetch tasks:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      const task = await api.post<Task>(
        "/tasks/",
        {
          title: newTitle,
          description: newDesc || null,
          reward: parseInt(newReward) || 0,
          priority: newPriority,
        },
        token!
      );
      setTasks((prev) => [task, ...prev]);
      setNewTitle("");
      setNewDesc("");
      setNewReward("0");
      setShowCreate(false);
    } catch (err) {
      console.error("Failed to create task:", err);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(taskId: string) {
    if (!confirm("Delete this task?")) return;
    try {
      await api.delete(`/tasks/${taskId}`, token!);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  }

  const priorityColors: Record<string, string> = {
    high: "bg-red-500/10 text-red-600",
    medium: "bg-amber-500/10 text-amber-600",
    low: "bg-emerald-500/10 text-emerald-600",
  };

  const statusColors: Record<string, string> = {
    open: "bg-blue-500/10 text-blue-600",
    in_progress: "bg-amber-500/10 text-amber-600",
    completed: "bg-emerald-500/10 text-emerald-600",
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Tasks</h1>
            <p className="text-sm text-muted-foreground">Manage tasks for your agents</p>
          </div>
          <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
            <Plus className="mr-1 h-4 w-4" />
            Post Task
          </Button>
        </div>

        {showCreate && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Post New Task</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      placeholder="Task title"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reward">Reward (NXC)</Label>
                    <Input
                      id="reward"
                      type="number"
                      placeholder="0"
                      value={newReward}
                      onChange={(e) => setNewReward(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="desc">Description</Label>
                  <Input
                    id="desc"
                    placeholder="Task description"
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                  />
                </div>
                <div className="flex items-center gap-4">
                  <div className="space-y-2">
                    <Label>Priority</Label>
                    <div className="flex gap-2">
                      {["low", "medium", "high"].map((p) => (
                        <Button
                          key={p}
                          type="button"
                          variant={newPriority === p ? "default" : "outline"}
                          size="sm"
                          onClick={() => setNewPriority(p)}
                        >
                          {p}
                        </Button>
                      ))}
                    </div>
                  </div>
                  <Button type="submit" disabled={creating} className="mt-auto">
                    {creating ? "Posting..." : "Post Task"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-foreground" />
              </div>
            ) : tasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <CheckSquare className="h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm font-medium">No tasks yet</p>
                <p className="text-xs text-muted-foreground mt-1">Post a task to assign work to your agents</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Reward</TableHead>
                    <TableHead>Skills</TableHead>
                    <TableHead className="w-[50px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <div>
                          <p className="text-sm font-medium">{task.title}</p>
                          {task.description && (
                            <p className="text-xs text-muted-foreground truncate max-w-[300px]">{task.description}</p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${statusColors[task.status] || ""}`}>{task.status}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${priorityColors[task.priority] || ""}`}>{task.priority}</Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm tabular-nums">{task.reward} NXC</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 flex-wrap">
                          {task.required_skills?.slice(0, 3).map((skill) => (
                            <Badge key={skill} className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleDelete(task.id)}
                        >
                          <span className="sr-only">Delete</span>
                          ×
                        </Button>
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
