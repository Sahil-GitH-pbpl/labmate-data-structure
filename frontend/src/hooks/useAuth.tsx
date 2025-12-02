import React, { createContext, useContext, useEffect, useState } from 'react';
import api from '../api/client';

interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthContextType>({ token: null, setToken: () => {} });

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(localStorage.getItem('hiccup_token'));

  const setToken = (value: string | null) => {
    setTokenState(value);
    if (value) {
      localStorage.setItem('hiccup_token', value);
    } else {
      localStorage.removeItem('hiccup_token');
    }
  };

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  return <AuthContext.Provider value={{ token, setToken }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
