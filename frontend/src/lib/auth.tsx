"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { User, TokenResponse } from "@/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("nexus_token");
    const savedUser = localStorage.getItem("nexus_user");
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.post<TokenResponse>("/auth/login", { email, password });
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("nexus_token", data.access_token);
    localStorage.setItem("nexus_user", JSON.stringify(data.user));
  }, []);

  const register = useCallback(async (email: string, username: string, password: string, fullName?: string) => {
    const data = await api.post<TokenResponse>("/auth/register", {
      email,
      username,
      password,
      full_name: fullName || null,
    });
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("nexus_token", data.access_token);
    localStorage.setItem("nexus_user", JSON.stringify(data.user));
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("nexus_token");
    localStorage.removeItem("nexus_user");
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
