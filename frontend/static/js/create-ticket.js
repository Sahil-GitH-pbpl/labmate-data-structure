const categoryMap = {
  "Hardware": ["Desktop", "Laptop", "Printer"],
  "Software": ["OS", "Office", "Other"],
  "Office Infra": ["Chair", "Desk", "AC"],
  "Other": ["Misc"]
};

const categorySelect = document.getElementById('category');
const subcategorySelect = document.getElementById('subcategory');
const form = document.getElementById('create-ticket-form');
const messageEl = document.getElementById('form-message');

function populateCategories() {
  Object.keys(categoryMap).forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat; opt.textContent = cat;
    categorySelect.appendChild(opt);
  });
  updateSubcategories();
}

function updateSubcategories() {
  subcategorySelect.innerHTML = '';
  (categoryMap[categorySelect.value] || []).forEach(sub => {
    const opt = document.createElement('option');
    opt.value = sub; opt.textContent = sub;
    subcategorySelect.appendChild(opt);
  });
}

categorySelect.addEventListener('change', updateSubcategories);
populateCategories();

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(form);
  const token = prompt('Enter your token (alice/bob/admin)');
  try {
    const resp = await fetch('/infra/create', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: data
    });
    const json = await resp.json();
    if (!resp.ok) throw new Error(json.detail || 'Failed');
    messageEl.textContent = `Created ticket #${json.ticket_id}`;
    messageEl.className = 'success';
  } catch (err) {
    messageEl.textContent = err.message;
    messageEl.className = 'error';
  }
});
