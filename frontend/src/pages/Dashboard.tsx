import React, { useEffect, useState } from 'react';
import api from '../api/client';

interface HiccupDetail {
  hiccup_id: string;
  status: string;
  raised_against: string;
  is_response_overdue: boolean;
  is_closure_overdue: boolean;
}

const Dashboard: React.FC = () => {
  const [myHiccups, setMyHiccups] = useState<HiccupDetail[]>([]);

  useEffect(() => {
    api.get('/api/hiccups').then((res) => setMyHiccups(res.data.items || []));
  }, []);

  const counts = myHiccups.reduce(
    (acc, h) => {
      acc[h.status] = (acc[h.status] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const overdue = myHiccups.filter((h) => h.is_response_overdue || h.is_closure_overdue);

  return (
    <div>
      <h1>Dashboard</h1>
      <div className="grid">
        <div className="card">Open: {counts['Open'] || 0}</div>
        <div className="card">Responded: {counts['Responded'] || 0}</div>
        <div className="card">Closed: {counts['Closed'] || 0}</div>
      </div>
      <h2>Overdue</h2>
      <ul>
        {overdue.map((h) => (
          <li key={h.hiccup_id}>
            {h.hiccup_id} - {h.status} {h.is_response_overdue ? '⚠️ Awaiting Response' : ''}{' '}
            {h.is_closure_overdue ? '⏰ Closure Pending' : ''}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
