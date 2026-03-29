"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

interface User {
  name: string;
  email: string;
  avatar: string;
}

interface AuthContextType {
  user: User | null;
  login: (name: string, email: string) => void;
  logout: () => void;
  updateProfile: (name: string, email: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Fake persistence check
    const stored = localStorage.getItem("saas_user");
    if (stored) {
      setUser(JSON.parse(stored));
    } else if (pathname !== "/login" && pathname !== "/register") {
      router.push("/login");
    }
  }, [pathname, router]);

  const login = (name: string, email: string) => {
    const newUser = { name, email, avatar: `https://api.dicebear.com/7.x/notionists/svg?seed=${name}` };
    setUser(newUser);
    localStorage.setItem("saas_user", JSON.stringify(newUser));
    router.push("/dashboard");
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("saas_user");
    // Handled by animation inside TopNav before calling this
    setTimeout(() => router.push("/login"), 300);
  };

  const updateProfile = (name: string, email: string) => {
    if (user) {
      const updated = { ...user, name, email, avatar: `https://api.dicebear.com/7.x/notionists/svg?seed=${name}` };
      setUser(updated);
      localStorage.setItem("saas_user", JSON.stringify(updated));
    }
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
