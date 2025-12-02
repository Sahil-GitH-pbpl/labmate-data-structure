import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';

const AssignedHiccups: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.get('/api/hiccups').then((res) => setItems(res.data.items || []));
  }, []);

  return (
    <div>
      <h1>Assigned Hiccups</h1>
      <ul>
        {items.map((item) => (
          <li key={item.hiccup_id}>
            <Link to={`/hiccups/${item.hiccup_id}`}>{item.hiccup_id}</Link> - {item.status}
            {item.is_response_overdue && <span className="badge">Overdue</span>}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AssignedHiccups;
