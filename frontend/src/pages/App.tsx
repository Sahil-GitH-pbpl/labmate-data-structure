import React from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const App: React.FC = () => {
  const { setToken } = useAuth();
  const navigate = useNavigate();

  const logout = () => {
    setToken(null);
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Hiccup System</h2>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/raise">Raise Hiccup</Link>
          <Link to="/my">My Hiccups</Link>
          <Link to="/assigned">Assigned</Link>
          <Link to="/management">Management</Link>
          <Link to="/reports">Reports</Link>
          <Link to="/settings">Settings</Link>
        </nav>
        <button onClick={logout} className="secondary">Logout</button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
};

export default App;
