const scopeSelect = document.getElementById('scope');
const listEl = document.getElementById('ticket-list');
const token = prompt('Enter your token (alice/bob/admin)');

async function loadTickets(){
  const params = new URLSearchParams({scope: scopeSelect.value});
  const resp = await fetch('/infra/my?' + params.toString(), {headers:{Authorization:`Bearer ${token}`}});
  const json = await resp.json();
  listEl.innerHTML = '';
  json.items.forEach(t => {
    const div = document.createElement('div');
    div.className = 'ticket';
    div.innerHTML = `<strong>#${t.ticket_id}</strong> - ${t.status} - ${t.category}/${t.subcategory}<br/>Assigned: ${t.assigned_to||'NA'} | Commitment: ${t.commitment_time||'NA'}<br/>Delayed: ${t.is_delayed_pick} | Invalid: ${t.is_invalid ? t.invalid_reason : ''}`;
    listEl.appendChild(div);
  });
}

document.getElementById('refresh-btn').addEventListener('click', loadTickets);
scopeSelect.addEventListener('change', loadTickets);
loadTickets();
