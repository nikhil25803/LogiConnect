"use client";
import { createContext, useState, useEffect, useContext } from "react";
import { useRouter } from "next/navigation";

interface AuthContextProps {
  token: string | null;
  userId: string | null;
  login: (token: string, userId: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextProps>({
  token: null,
  userId: null,
  login: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    const storedUserId = localStorage.getItem("userid");
    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUserId(storedUserId);
    }
  }, []);

  const login = (token: string, userId: string) => {
    setToken(token);
    setUserId(userId);
    localStorage.setItem("access_token", token);
    localStorage.setItem("userid", userId);
    router.push("/user-dashboard");
  };

  const logout = () => {
    setToken(null);
    setUserId(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("userid");
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ token, userId, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
