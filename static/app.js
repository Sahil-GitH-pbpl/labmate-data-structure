const centers = ["10", "11", "13", "15", "19"];
const centerBtns = document.getElementById("centerBtns");
const status = document.getElementById("status");
const pidInput = document.getElementById("pid");
const applyBtn = document.getElementById("applyBtn");
const tableHead = document.querySelector("#dataTable thead");
const tableBody = document.querySelector("#dataTable tbody");
let currentCenter = "10";
const AUTO_INCREMENT_DELAY_MS = 1000;
const API_RETRY_DELAY_MS = 1500;
let isRunning = false;
let stopRequested = false;

const columnOrder = [
  { key: "patientid", label: "Patient ID" },
  { key: "patientname", label: "Name" },
  { key: "mobileno", label: "Mobile No" },
  { key: "gender", label: "Gender" },
  { key: "reportstatus", label: "Status" },
  { key: "age", label: "Age" },
  { key: "bdate", label: "B/Date" },
  { key: "address", label: "Address" },
  { key: "doctor", label: "Doctor" },
  { key: "doctormobile", label: "Dctr Mob" },
  { key: "panel", label: "Panel" },
  { key: "ordertest", label: "Order Test" },
  { key: "pdffile", label: "Report" },
  { key: "whatsapp", label: "Wtap" },
  { key: "message", label: "Msg" },
];

const wrapColumns = new Set(["message"]);
const truncateColumns = new Set(["address", "ordertest"]);
const nowrapColumns = new Set([
  "patientid",
  "patientname",
  "mobileno",
  "gender",
  "reportstatus",
  "doctormobile",
  "panel",
]);

centers.forEach((c) => {
  const btn = document.createElement("button");
  btn.textContent = "Center " + c;
  btn.classList.add("secondary");
  btn.dataset.center = c;
  btn.addEventListener("click", () => loadCenter(c));
  centerBtns.appendChild(btn);
});

function setActive(center) {
  currentCenter = center;
  document.querySelectorAll("#centerBtns button").forEach((b) => {
    b.classList.toggle("active", b.dataset.center === center);
  });
}

async function loadCenter(center) {
  setActive(center);
  status.textContent = "Loading center " + center + "...";
  try {
    const res = await fetch(`/api/center/${center}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Failed to load");
    renderTable(data.rows || []);
    status.textContent = `Showing ${data.rows.length} rows from center ${center}.`;
  } catch (err) {
    status.textContent = err.message;
  }
}

function renderTable(rows) {
  if (!rows.length) {
    tableHead.innerHTML = "<tr><th>No data</th></tr>";
    tableBody.innerHTML = "";
    return;
  }

  // Keep preferred order, then append any extra fields.
  const presentCols = columnOrder.filter((c) => Object.prototype.hasOwnProperty.call(rows[0], c.key));
  const extras = Object.keys(rows[0]).filter(
    (k) => k !== "created_at" && !presentCols.find((c) => c.key === k)
  );
  const cols = [...presentCols, ...extras.map((k) => ({ key: k, label: k }))];

  tableHead.innerHTML =
    "<tr>" +
    cols
      .map((c) => {
        const classes = [
          nowrapColumns.has(c.key) ? "nowrap" : "",
          wrapColumns.has(c.key) ? "wrap" : "",
          truncateColumns.has(c.key) ? "truncate" : "",
          `col-${c.key}`,
        ]
          .filter(Boolean)
          .join(" ");
        return `<th class="${classes}">${c.label}</th>`;
      })
      .join("") +
    "</tr>";
  tableBody.innerHTML = rows
    .map(
      (r) =>
        "<tr>" +
        cols
          .map(
            (c) => {
              const classes = [
                nowrapColumns.has(c.key) ? "nowrap" : "",
                wrapColumns.has(c.key) ? "wrap" : "",
                truncateColumns.has(c.key) ? "truncate" : "",
                `col-${c.key}`,
              ]
                .filter(Boolean)
                .join(" ");
              return `<td class="${classes}">${formatCell(c.key, r[c.key])}</td>`;
            }
          )
          .join("") +
        "</tr>"
    )
    .join("");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (ch) => {
    switch (ch) {
      case "&":
        return "&amp;";
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case '"':
        return "&quot;";
      case "'":
        return "&#39;";
      default:
        return ch;
    }
  });
}

function formatCell(key, value) {
  if (value === null || value === undefined || value === "") return "-";
  if (key === "age") {
    const raw = String(value);
    const match = raw.match(/(\d{1,3})/);
    if (match) return `${match[1]} Y`;
  }
  if (key === "pdffile" && typeof value === "string" && value.startsWith("http")) {
    return `<a class="link-btn" href="${value}" target="_blank" rel="noopener noreferrer">View</a>`;
  }
  if (truncateColumns.has(key)) {
    const safe = escapeHtml(value);
    return `<span class="truncate-pill" title="${safe}">${safe}</span>`;
  }
  return value;
}

function setRunningState(running) {
  isRunning = running;
  applyBtn.textContent = running ? "Stop" : "Apply";
  pidInput.disabled = running;
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchAndSaveOnce(pid) {
  try {
    const res = await fetch("/api/fetch-patient", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patientid: pid }),
    });
    let data = null;
    try {
      data = await res.json();
    } catch (err) {
      data = null;
    }

    if (res.ok && data && data.ok) {
      return { status: "ok", table: data.table };
    }

    const message = (data && data.error) ? data.error : `Request failed (${res.status})`;
    if (res.status === 404) return { status: "no-record", message };
    if (res.status === 502) return { status: "retry", message };
    if (res.status === 409) return { status: "invalid-sequence", message };
    return { status: "fatal", message };
  } catch (err) {
    return { status: "retry", message: err.message || "Network error" };
  }
}

async function runAutoFetch(startId) {
  let currentId = BigInt(startId);
  stopRequested = false;
  setRunningState(true);
  try {
    while (!stopRequested) {
      const idStr = currentId.toString();
      status.textContent = `Fetching ${idStr}...`;

      const result = await fetchAndSaveOnce(idStr);
      if (result.status === "ok") {
        status.textContent = `Saved ${idStr} to ${result.table}. Next in ${AUTO_INCREMENT_DELAY_MS / 1000}s...`;
        loadCenter(result.table.replace("center", ""));
        currentId += 1n;
        pidInput.value = currentId.toString();
        await delay(AUTO_INCREMENT_DELAY_MS);
        continue;
      }

      if (result.status === "retry") {
        status.textContent = `${result.message} Retrying in ${API_RETRY_DELAY_MS / 1000}s...`;
        await delay(API_RETRY_DELAY_MS);
        continue;
      }

      if (result.status === "no-record") {
        status.textContent = `No record for ${idStr}.`;
        alert("this is last id for fetch the data now");
        break;
      }

      if (result.status === "invalid-sequence") {
        status.textContent = result.message || "Invalid patient ID sequence.";
        alert(result.message || "Invalid patient ID sequence.");
        break;
      }

      status.textContent = result.message || "Stopped due to error.";
      break;
    }
  } finally {
    setRunningState(false);
  }
}

function startOrStopAutoFetch() {
  if (isRunning) {
    stopRequested = true;
    status.textContent = "Stopping...";
    return;
  }

  const pid = pidInput.value.trim();
  if (!pid) {
    status.textContent = "Enter a patient ID.";
    return;
  }
  if (!/^\d+$/.test(pid)) {
    status.textContent = "Patient ID must be numeric.";
    return;
  }
  runAutoFetch(pid);
}

applyBtn.addEventListener("click", startOrStopAutoFetch);
pidInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") startOrStopAutoFetch();
});

loadCenter(currentCenter);
