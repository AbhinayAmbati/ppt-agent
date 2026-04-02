'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthResponse, LoginRequest, RegisterRequest } from '@/lib/types';
import { authAPI } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isInitializing: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth from localStorage on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        const storedUserId = localStorage.getItem('user_id');

        if (storedToken && storedUserId) {
          setToken(storedToken);
          try {
            const userData = await authAPI.getMe();
            setUser(userData);
          } catch (e) {
            console.error('Failed to fetch profile', e);
            setUser({ id: storedUserId, username: 'User', email: 'Not set', createdAt: '' });
          }
        }
      } catch (err) {
        console.error('Failed to initialize auth:', err);
      } finally {
        setIsInitializing(false);
      }
    };

    initAuth();
  }, []);

  const login = async (data: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const response: AuthResponse = await authAPI.login(data);

      // Store in localStorage first so API can use it immediately
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_id', String(response.user_id));
      
      setToken(response.access_token);
      try {
        const userData = await authAPI.getMe();
        setUser(userData);
      } catch (e) {
        setUser({ id: response.user_id, username: data.username, email: '', createdAt: new Date().toISOString() });
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authAPI.register(data);

      // Auto-login after successful registration
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_id', String(response.user_id));

      setToken(response.access_token);
      try {
        const userData = await authAPI.getMe();
        setUser(userData);
      } catch (e) {
        setUser({ id: response.user_id, username: data.username, email: data.email, createdAt: new Date().toISOString() });
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setError(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    // No need to call backend logout endpoint for now
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isInitializing,
        error,
        login,
        register,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
