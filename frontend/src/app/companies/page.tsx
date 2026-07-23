"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/app-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Company } from "@/types";
import { Plus, Building2 } from "lucide-react";

export default function CompaniesPage() {
  const { token } = useAuth();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newIndustry, setNewIndustry] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetchCompanies();
  }, [token]);

  async function fetchCompanies() {
    try {
      const data = await api.get<Company[]>("/companies/", token!);
      setCompanies(data);
    } catch (err) {
      console.error("Failed to fetch companies:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const company = await api.post<Company>(
        "/companies/",
        { name: newName, industry: newIndustry || null },
        token!
      );
      setCompanies((prev) => [company, ...prev]);
      setNewName("");
      setNewIndustry("");
      setShowCreate(false);
    } catch (err) {
      console.error("Failed to create company:", err);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(companyId: string) {
    if (!confirm("Delete this company?")) return;
    try {
      await api.delete(`/companies/${companyId}`, token!);
      setCompanies((prev) => prev.filter((c) => c.id !== companyId));
    } catch (err) {
      console.error("Failed to delete company:", err);
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Companies</h1>
            <p className="text-sm text-muted-foreground">Organizations in the economy</p>
          </div>
          <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
            <Plus className="mr-1 h-4 w-4" />
            New Company
          </Button>
        </div>

        {showCreate && (
          <Card>
            <CardContent className="pt-6">
              <form onSubmit={handleCreate} className="flex gap-4 items-end">
                <div className="flex-1 space-y-2">
                  <Label htmlFor="name">Company Name</Label>
                  <Input
                    id="name"
                    placeholder="Acme Corp"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    required
                  />
                </div>
                <div className="flex-1 space-y-2">
                  <Label htmlFor="industry">Industry</Label>
                  <Input
                    id="industry"
                    placeholder="Technology"
                    value={newIndustry}
                    onChange={(e) => setNewIndustry(e.target.value)}
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
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-foreground" />
              </div>
            ) : companies.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Building2 className="h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm font-medium">No companies yet</p>
                <p className="text-xs text-muted-foreground mt-1">Create a company to organize agents</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Company</TableHead>
                    <TableHead>Industry</TableHead>
                    <TableHead>Members</TableHead>
                    <TableHead>Treasury</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[50px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {companies.map((company) => (
                    <TableRow key={company.id}>
                      <TableCell>
                        <div>
                          <p className="text-sm font-medium">{company.name}</p>
                          {company.description && (
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {company.description}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">{company.industry || "—"}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm tabular-nums">{company.member_agent_ids?.length || 0}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm tabular-nums">{company.treasury_balance.toLocaleString()} NXC</span>
                      </TableCell>
                      <TableCell>
                        <Badge className="text-xs">{company.status}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleDelete(company.id)}
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
