import React, { useState } from 'react';
import api from '../api/client';

const RaiseHiccup: React.FC = () => {
  const [hiccupType, setHiccupType] = useState('Person Related');
  const [raisedAgainst, setRaisedAgainst] = useState('');
  const [description, setDescription] = useState('');
  const [immediateEffect, setImmediateEffect] = useState('');
  const [sourceModule, setSourceModule] = useState('');
  const [confidential, setConfidential] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [resultId, setResultId] = useState<string>('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = new FormData();
    form.append('hiccup_type', hiccupType);
    form.append('raised_against', raisedAgainst);
    form.append('description', description);
    form.append('immediate_effect', immediateEffect);
    form.append('source_module', sourceModule);
    form.append('confidential_flag', String(confidential));
    if (file) form.append('attachment', file);
    const res = await api.post('/api/hiccups', form, { headers: { 'Content-Type': 'multipart/form-data' } });
    setResultId(res.data.hiccup_id);
  };

  return (
    <div>
      <h1>Raise Hiccup</h1>
      <form onSubmit={submit} className="card">
        <label>Type</label>
        <select value={hiccupType} onChange={(e) => setHiccupType(e.target.value)}>
          <option value="Person Related">Person Related</option>
          <option value="System Related">System Related</option>
        </select>
        <label>Raised Against</label>
        <input value={raisedAgainst} onChange={(e) => setRaisedAgainst(e.target.value)} placeholder="staff id or system tag" />
        <label>Description</label>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} required />
        <label>Immediate Effect</label>
        <textarea value={immediateEffect} onChange={(e) => setImmediateEffect(e.target.value)} />
        <label>Source Module</label>
        <input value={sourceModule} onChange={(e) => setSourceModule(e.target.value)} />
        <label>
          <input type="checkbox" checked={confidential} onChange={(e) => setConfidential(e.target.checked)} /> Confidential
        </label>
        <label>Attachment</label>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button type="submit">Submit</button>
      </form>
      {resultId && <p className="success">Hiccup created with ID: {resultId}</p>}
    </div>
  );
};

export default RaiseHiccup;
