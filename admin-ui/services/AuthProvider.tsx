"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { authApi, setAccessToken } from "./api";

type AdminRole = "ADMIN" | "OWNER";

type AuthContextValue = {
  ready: boolean;
  authenticated: boolean;
  role: AdminRole | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function acceptedRole(value: unknown): AdminRole | null {
  return value === "ADMIN" || value === "OWNER" ? value : null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [role, setRole] = useState<AdminRole | null>(null);

  const applySession = useCallback((data: any) => {
    const token = data?.accessToken;
    const nextRole = acceptedRole(data?.role || data?.user?.role);

    if (!token || !nextRole) {
      setAccessToken(null);
      setRole(null);
      throw new Error("This account does not have ADMIN or OWNER access.");
    }

    setAccessToken(token);
    setRole(nextRole);
  }, []);

  useEffect(() => {
    let active = true;

    authApi
      .post("/auth/refresh", {})
      .then((response) => {
        if (active) applySession(response.data);
      })
      .catch(() => {
        if (active) {
          setAccessToken(null);
          setRole(null);
        }
      })
      .finally(() => {
        if (active) setReady(true);
      });

    return () => {
      active = false;
    };
  }, [applySession]);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await authApi.post("/auth/login", {
        email,
        password,
      });
      applySession(response.data);
      setReady(true);
    },
    [applySession]
  );

  const logout = useCallback(async () => {
    try {
      await authApi.post("/auth/logout", {});
    } finally {
      setAccessToken(null);
      setRole(null);
      setReady(true);
      if (typeof window !== "undefined") {
        window.location.assign("/login");
      }
    }
  }, []);

  const value = useMemo(
    () => ({
      ready,
      authenticated: role !== null,
      role,
      login,
      logout,
    }),
    [ready, role, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return context;
}

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const { ready, authenticated, role } = useAuth();
  const [path, setPath] = useState("");

  useEffect(() => {
    setPath(window.location.pathname);
  }, []);

  const isLoginPage = path === "/login";

  useEffect(() => {
    if (!ready || !path) return;

    if (!isLoginPage && (!authenticated || !role)) {
      window.location.replace("/login");
      return;
    }

    if (isLoginPage && authenticated) {
      window.location.replace("/");
    }
  }, [ready, path, isLoginPage, authenticated, role]);

  if (!path) return null;
  if (isLoginPage) return <>{children}</>;
  if (!ready || !authenticated || !role) {
    return (
      <div className="gb-auth-loading">
        <div className="gb-auth-spinner" />
        <p>Verifying secure admin session…</p>
      </div>
    );
  }

  return <>{children}</>;
}
