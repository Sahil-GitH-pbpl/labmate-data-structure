import React, { useEffect, useState } from 'react';
import api from '../api/client';

const Reports: React.FC = () => {
  const [daily, setDaily] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [monthly, setMonthly] = useState<any>(null);

  useEffect(() => {
    api.get('/api/reports/daily').then((res) => setDaily(res.data)).catch(() => {});
    api.get('/api/reports/trends').then((res) => setTrends(res.data || [])).catch(() => {});
    api.get('/api/reports/monthly').then((res) => setMonthly(res.data)).catch(() => {});
  }, []);

  return (
    <div>
      <h1>Reports & Dashboards</h1>
      {daily && (
        <div className="card">
          <h3>Daily Summary</h3>
          <p>Raised: {daily.raised}</p>
          <p>Responded: {daily.responded}</p>
          <p>Closed: {daily.closed}</p>
          <p>Escalated: {daily.escalated}</p>
        </div>
      )}

      <div className="card">
        <h3>Trend Alerts</h3>
        <ul>
          {trends.map((t) => (
            <li key={t.key}>
              {t.key}: {t.count} in {t.window_days}d
            </li>
          ))}
        </ul>
      </div>

      {monthly && (
        <div className="card">
          <h3>Monthly Digest</h3>
          <p>Total: {monthly.total}</p>
          <p>By Type: {monthly.by_type?.map((b: any) => `${b.type}: ${b.count}`).join(', ')}</p>
          <p>Root Causes: {monthly.by_root_cause?.map((b: any) => `${b.root_cause_category}: ${b.count}`).join(', ')}</p>
        </div>
      )}
    </div>
  );
};

export default Reports;
