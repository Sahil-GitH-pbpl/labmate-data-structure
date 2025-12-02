import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';

const MyHiccups: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.get('/api/hiccups').then((res) => setItems(res.data.items || []));
  }, []);

  return (
    <div>
      <h1>My Hiccups</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Against</th>
            <th>Overdue</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.hiccup_id}>
              <td>
                <Link to={`/hiccups/${item.hiccup_id}`}>{item.hiccup_id}</Link>
              </td>
              <td>{item.status}</td>
              <td>{item.raised_against}</td>
              <td>
                {item.is_response_overdue && '⚠️ Response'} {item.is_closure_overdue && '⏰ Closure'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MyHiccups;
