import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { jwtDecode } from "jwt-decode";
import { toast } from "sonner";
import { axiosClient, apiUrl } from "@/lib/api";

type UserPreferences = {
  reading_style: string;
  language: string;
  theme: string;
  experience_level: string;
  belief_system: string;
  tarot_tradition: string;
  cultural_background: string;
  reading_frequency: string;
};

export type User = {
  _id?: string;
  id?: string;
  email: string;
  name: string;
  avatar_url?: string;
  preferences?: UserPreferences;
  role: string;
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [isLoading, setIsLoading] = useState(true);

  const fetchProfile = async (currentToken: string) => {
    try {
      // Setup temporary auth header just to fetch profile
      const response = await axiosClient.get(apiUrl("/api/v1/users/me"), {
        headers: { Authorization: `Bearer ${currentToken}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error("Failed to fetch user profile", error);
      logout();
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          const decoded: any = jwtDecode(storedToken);
          // Check expiry
          if (decoded.exp * 1000 < Date.now()) {
            throw new Error("Token expired");
          }
          setToken(storedToken);
          await fetchProfile(storedToken);
        } catch (error) {
          console.error("Token invalid or expired", error);
          logout();
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  useEffect(() => {
    const handleAuthExpired = () => {
      logout();
      toast.error("Phiên đăng nhập đã hết hạn", {
        description: "Vui lòng đăng nhập lại để tiếp tục sử dụng.",
        duration: 5000,
      });
    };
    window.addEventListener("auth-expired", handleAuthExpired);
    return () => window.removeEventListener("auth-expired", handleAuthExpired);
  }, []);

  const login = async (newToken: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    await fetchProfile(newToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  const updatePreferences = async (newPrefs: Partial<UserPreferences>) => {
    if (!token || !user) return;
    try {
      const resp = await axiosClient.put(apiUrl("/api/v1/users/me/preferences"), newPrefs, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser({
        ...user,
        preferences: resp.data
      });
    } catch (error) {
      console.error("Failed to update preferences", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, updatePreferences }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
