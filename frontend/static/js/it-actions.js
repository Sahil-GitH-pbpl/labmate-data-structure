const token = prompt('Enter IT/Admin token (bob/admin)');
const statusOptions = ["New","Assigned","In Progress","On Hold","Resolved"];
const categoryOptions = ["","Hardware","Software","Office Infra","Other"];

function fillSelect(select, options){
  options.forEach(opt => {
    const el=document.createElement('option');
    el.value=opt; el.textContent=opt||'All';
    select.appendChild(el);
  });
}

fillSelect(document.getElementById('filter-status'), [''].concat(statusOptions));
fillSelect(document.getElementById('filter-category'), categoryOptions);

async function loadTickets(page=1){
  const params = new URLSearchParams({page});
  const status = document.getElementById('filter-status').value;
  const category = document.getElementById('filter-category').value;
  const dept = document.getElementById('filter-dept').value;
  const q = document.getElementById('filter-q').value;
  if(status) params.append('status', status);
  if(category) params.append('category', category);
  if(dept) params.append('department', dept);
  if(q) params.append('q', q);
  const resp = await fetch('/infra/all?' + params.toString(), {headers:{Authorization:`Bearer ${token}`}});
  const json = await resp.json();
  const tbody = document.querySelector('#tickets-table tbody');
  tbody.innerHTML='';
  json.items.forEach(t => {
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${t.ticket_id}</td><td>${t.category}/${t.subcategory}</td><td>${t.department}</td><td title="${t.description}">${t.description.slice(0,40)}</td><td>${t.status}</td><td>${t.assigned_to||''}</td><td>${t.commitment_time||''}</td><td><button data-id="${t.ticket_id}" class="pick btn">Pick</button><button data-id="${t.ticket_id}" class="update btn">Update</button><button data-id="${t.ticket_id}" class="resolve btn">Resolve</button><button data-id="${t.ticket_id}" class="invalid btn">Invalid</button></td>`;
    tbody.appendChild(tr);
  });
}

async function pickTicket(id){
  const commitment = prompt('Commitment time (YYYY-MM-DDTHH:MM) in local timezone');
  const assigned = prompt('Assign to (leave blank for self)') || null;
  const resp = await fetch(`/infra/pick/${id}`, {method:'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body:JSON.stringify({commitment_time:commitment, assigned_to:assigned})});
  if(resp.ok) loadTickets(); else alert('Failed to pick');
}

async function addUpdate(id){
  const note = prompt('Update note');
  const statusChange = prompt('New status (optional)');
  const body = {note, status: statusChange||null};
  const resp = await fetch(`/infra/update/${id}`, {method:'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body:JSON.stringify(body)});
  if(resp.ok) loadTickets(); else alert('Failed');
}

async function resolve(id){
  const note = prompt('Resolution note');
  const resp = await fetch(`/infra/resolve/${id}`, {method:'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body:JSON.stringify({note})});
  if(resp.ok) loadTickets(); else alert('Failed');
}

async function markInvalid(id){
  const reason = prompt('Reason to mark invalid');
  const resp = await fetch(`/infra/invalid/${id}`, {method:'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body:JSON.stringify({invalid_reason:reason})});
  if(resp.ok) loadTickets(); else alert('Failed');
}

document.getElementById('filter-btn').addEventListener('click', ()=> loadTickets());

document.querySelector('#tickets-table').addEventListener('click', (e)=>{
  if(e.target.classList.contains('pick')) pickTicket(e.target.dataset.id);
  if(e.target.classList.contains('update')) addUpdate(e.target.dataset.id);
  if(e.target.classList.contains('resolve')) resolve(e.target.dataset.id);
  if(e.target.classList.contains('invalid')) markInvalid(e.target.dataset.id);
});

loadTickets();
