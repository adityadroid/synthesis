import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, api, getAccessToken, clearTokens, setTokens } from "../api/client";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken();
      if (token) {
        try {
          const userData = await api.getCurrentUser();
          setUser(userData);
        } catch {
          clearTokens();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    console.log(email, password);
    const tokens = await api.login(email, password);
    setTokens(tokens.access_token, tokens.refresh_token);
    const userData = await api.getCurrentUser();
    setUser(userData);
  };

  const signup = async (email: string, password: string, fullName?: string) => {
    await api.signup(email, password, fullName);
    await login(email, password);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}