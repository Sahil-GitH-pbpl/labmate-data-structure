import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import App from './pages/App';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import RaiseHiccup from './pages/RaiseHiccup';
import MyHiccups from './pages/MyHiccups';
import AssignedHiccups from './pages/AssignedHiccups';
import ManagementBoard from './pages/ManagementBoard';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import HiccupDetail from './pages/HiccupDetail';
import { AuthProvider, useAuth } from './hooks/useAuth';
import './styles.css';

const Protected: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <Protected>
                <App />
              </Protected>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="raise" element={<RaiseHiccup />} />
            <Route path="my" element={<MyHiccups />} />
            <Route path="assigned" element={<AssignedHiccups />} />
            <Route path="management" element={<ManagementBoard />} />
            <Route path="reports" element={<Reports />} />
            <Route path="settings" element={<Settings />} />
            <Route path="hiccups/:id" element={<HiccupDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
