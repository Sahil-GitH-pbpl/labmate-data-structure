import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../hooks/useAuth';

const LoginPage: React.FC = () => {
  const [userId, setUserId] = useState<number>(2);
  const [name, setName] = useState<string>('Demo User');
  const [role, setRole] = useState<string>('staff');
  const [departmentId, setDepartmentId] = useState<number>(1);
  const navigate = useNavigate();
  const { setToken } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await api.post('/api/auth/token', { user_id: userId, name, role, department_id: departmentId });
    setToken(res.data.access_token);
    navigate('/');
  };

  return (
    <div className="login-page">
      <h1>Login Stub</h1>
      <form onSubmit={handleLogin} className="card">
        <label>User ID</label>
        <input type="number" value={userId} onChange={(e) => setUserId(parseInt(e.target.value))} />
        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} />
        <label>Role</label>
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="staff">Staff</option>
          <option value="hod">HOD</option>
          <option value="management">Management</option>
          <option value="admin">System Admin</option>
        </select>
        <label>Department ID</label>
        <input type="number" value={departmentId} onChange={(e) => setDepartmentId(parseInt(e.target.value))} />
        <button type="submit">Generate Token</button>
      </form>
    </div>
  );
};

export default LoginPage;
