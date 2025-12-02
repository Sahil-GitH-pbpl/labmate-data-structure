import React, { useEffect, useState } from 'react';
import api from '../api/client';

const ManagementBoard: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState('Responded');

  useEffect(() => {
    api.get('/api/hiccups', { params: { status } }).then((res) => setItems(res.data.items || []));
  }, [status]);

  return (
    <div>
      <h1>Management Hiccups</h1>
      <label>Status Filter</label>
      <select value={status} onChange={(e) => setStatus(e.target.value)}>
        <option value="Responded">Responded</option>
        <option value="Under Review">Under Review</option>
        <option value="Open">Open</option>
      </select>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Dept</th>
            <th>Status</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {items.map((i) => (
            <tr key={i.hiccup_id}>
              <td>{i.hiccup_id}</td>
              <td>{i.raised_by_department}</td>
              <td>{i.status}</td>
              <td>{i.source_module}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ManagementBoard;
