import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/client';

const HiccupDetail: React.FC = () => {
  const { id } = useParams();
  const [detail, setDetail] = useState<any | null>(null);
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState('Under Review');
  const [closureNotes, setClosureNotes] = useState('');
  const [rootCause, setRootCause] = useState('');
  const [correctiveAction, setCorrectiveAction] = useState('');
  const [followupStatus, setFollowupStatus] = useState('Resolved');
  const [followupComment, setFollowupComment] = useState('');

  const load = async () => {
    if (!id) return;
    const res = await api.get(`/api/hiccups/${id}`);
    setDetail(res.data);
  };

  useEffect(() => {
    load();
  }, [id]);

  const submitResponse = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.patch(`/api/hiccups/${id}/respond`, { response_text: response });
    setResponse('');
    load();
  };

  const changeStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.patch(`/api/hiccups/${id}/status`, {
      status,
      closure_notes: closureNotes,
      root_cause: rootCause,
      corrective_action: correctiveAction,
    });
    load();
  };

  const sendFollowup = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.patch(`/api/hiccups/${id}/followup`, {
      followup_status: followupStatus,
      followup_comment: followupComment,
    });
    load();
  };

  if (!detail) return <div>Loading...</div>;

  return (
    <div>
      <h1>Hiccup {detail.hiccup_id}</h1>
      <div className="card">
        <p>Status: {detail.status}</p>
        <p>Type: {detail.hiccup_type}</p>
        <p>Raised Against: {detail.raised_against}</p>
        <p>Description: {detail.description}</p>
        <p>Root Cause: {detail.root_cause}</p>
        <p>Corrective Action: {detail.corrective_action}</p>
        <p>Followup: {detail.followup_status}</p>
      </div>

      <h3>Audit Trail</h3>
      <ul>
        {detail.audit_log?.map((a: any, idx: number) => (
          <li key={idx}>
            {a.timestamp}: {a.action} by {a.performed_by} {a.remarks}
          </li>
        ))}
      </ul>

      <div className="grid">
        <form onSubmit={submitResponse} className="card">
          <h3>Respond</h3>
          <textarea value={response} onChange={(e) => setResponse(e.target.value)} />
          <button type="submit">Submit Response</button>
        </form>

        <form onSubmit={changeStatus} className="card">
          <h3>Management Actions</h3>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="Under Review">Under Review</option>
            <option value="Closed">Closed</option>
            <option value="Escalated to NC">Escalated to NC</option>
          </select>
          <textarea placeholder="Closure Notes" value={closureNotes} onChange={(e) => setClosureNotes(e.target.value)} />
          <textarea placeholder="Root Cause" value={rootCause} onChange={(e) => setRootCause(e.target.value)} />
          <textarea placeholder="Corrective Action" value={correctiveAction} onChange={(e) => setCorrectiveAction(e.target.value)} />
          <button type="submit">Update Status</button>
        </form>

        <form onSubmit={sendFollowup} className="card">
          <h3>Followup</h3>
          <select value={followupStatus} onChange={(e) => setFollowupStatus(e.target.value)}>
            <option value="Resolved">Resolved</option>
            <option value="Unresolved">Unresolved</option>
          </select>
          <textarea value={followupComment} onChange={(e) => setFollowupComment(e.target.value)} />
          <button type="submit">Submit Followup</button>
        </form>
      </div>
    </div>
  );
};

export default HiccupDetail;
