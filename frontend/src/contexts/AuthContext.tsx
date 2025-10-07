import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/router';
import Cookies from 'js-cookie';
import api from '@/lib/api';
import { User, LoginCredentials, RegisterData, AuthResponse } from '@/types/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Check if user is logged in on mount
  useEffect(() => {
    const initAuth = async () => {
      const accessToken = Cookies.get('access_token');
      if (accessToken) {
        try {
          await refreshUser();
        } catch (error) {
          console.error('Failed to fetch user:', error);
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await api.post<AuthResponse>('/auth/login/', credentials);
      const { user, access, refresh } = response.data;

      // Store tokens in cookies
      Cookies.set('access_token', access, { expires: 1 }); // 1 day
      Cookies.set('refresh_token', refresh, { expires: 7 }); // 7 days

      setUser(user);
      // Don't redirect here - let the calling component handle it
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const response = await api.post<{ user: User; message: string }>('/auth/register/', data);
      const { user } = response.data;

      // After registration, log them in
      await login({ email: data.email, password: data.password });
    } catch (error: any) {
      const errorData = error.response?.data;
      if (errorData) {
        // Extract first error message
        const firstError = Object.values(errorData)[0];
        throw new Error(Array.isArray(firstError) ? firstError[0] : String(firstError));
      }
      throw new Error('Registration failed');
    }
  };

  const logout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    setUser(null);
    router.push('/login');
  };

  const refreshUser = async () => {
    try {
      const response = await api.get<User>('/auth/user/');
      setUser(response.data);
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
