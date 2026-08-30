"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { getMe, login as loginRequest, signup as signupRequest } from "@/lib/api/auth";
import { clearTokens, hasStoredSession } from "@/lib/auth/storage";
import type { User } from "@/lib/types";

type SessionContextValue = {
  user: User | null;
  status: "loading" | "ready";
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: {
    email: string;
    password: string;
    name: string;
    bio?: string;
  }) => Promise<void>;
  logout: () => void;
};

const SessionContext = createContext<SessionContextValue | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<"loading" | "ready">("loading");

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      if (!hasStoredSession()) {
        if (!cancelled) setStatus("ready");
        return;
      }
      try {
        const me = await getMe();
        if (!cancelled) setUser(me);
      } catch {
        clearTokens();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setStatus("ready");
      }
    }

    void hydrate();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    await loginRequest(email, password);
    setUser(await getMe());
  }, []);

  const signup = useCallback(
    async (payload: { email: string; password: string; name: string; bio?: string }) => {
      await signupRequest(payload);
      await loginRequest(payload.email, payload.password);
      setUser(await getMe());
    },
    [],
  );

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    window.location.assign("/login");
  }, []);

  const value = useMemo(
    () => ({ user, status, login, signup, logout }),
    [user, status, login, signup, logout],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return context;
}
