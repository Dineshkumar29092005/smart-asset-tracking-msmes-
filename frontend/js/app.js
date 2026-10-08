// Dashboard logic: talks to the Flask backend through the /api endpoints.

const $ = (id) => document.getElementById(id);
let selectedAssetId = null;

// Escape text before putting it in HTML (prevents broken markup / injection)
function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Request failed: " + url);
  return res.json();
}

// ---------- Summary cards ----------
async function loadStats() {
  const s = await getJSON("/api/stats");
  $("stat-total").textContent = s.total;
  $("stat-available").textContent = s.available;
  $("stat-missing").textContent = s.missing;
  $("stat-alerts").textContent = s.alerts;
}

// ---------- Asset table + search ----------
function buildSearchURL() {
  const params = new URLSearchParams();
  ["q", "category", "zone", "status", "date"].forEach((key) => {
    const value = $(key).value.trim();
    if (value) params.set(key, value);
  });
  return "/api/assets/search?" + params.toString();
}

async function loadAssets() {
  const assets = await getJSON(buildSearchURL());
  const body = $("asset-rows");

  if (assets.length === 0) {
    body.innerHTML = '<tr><td colspan="7" class="empty">No assets found.</td></tr>';
    return;
  }

  body.innerHTML = assets.map((a) => `
    <tr data-id="${esc(a.asset_id)}" class="${a.asset_id === selectedAssetId ? "selected" : ""}">
      <td>${esc(a.asset_id)}</td>
      <td>${esc(a.asset_name)}</td>
      <td>${esc(a.category)}</td>
      <td>${esc(a.camera_id)}</td>
      <td>${esc(a.zone || "Unknown")}</td>
      <td>${esc(a.last_seen_time)}</td>
      <td><span class="badge ${esc(a.status).replace(" ", "-")}">${esc(a.status)}</span></td>
    </tr>`).join("");

  body.querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => {
      selectedAssetId = row.dataset.id;
      body.querySelectorAll("tr").forEach((r) => r.classList.remove("selected"));
      row.classList.add("selected");
      loadHistory(selectedAssetId);
    });
  });
}

// ---------- History ----------
async function loadHistory(assetId) {
  const items = await getJSON(`/api/assets/${encodeURIComponent(assetId)}/history`);
  if (items.length === 0) {
    $("history").innerHTML = '<p class="empty">No history yet.</p>';
    return;
  }
  $("history").innerHTML = items.map((h) => `
    <div class="list-item">
      <div><strong>${esc(h.zone || "Unknown")}</strong><small>${esc(h.camera_id)}</small></div>
      <div>${esc(h.seen_time)}</div>
    </div>`).join("");
}

// ---------- Alerts ----------
async function loadAlerts() {
  const alerts = await getJSON("/api/alerts");
  if (alerts.length === 0) {
    $("alerts").innerHTML = '<p class="empty">No alerts. All good!</p>';
    return;
  }
  $("alerts").innerHTML = alerts.map((al) => `
    <div class="list-item ${al.resolved ? "resolved" : ""}">
      <div>
        <strong>${esc(al.alert_type)}: ${esc(al.asset_name || al.asset_id)}</strong>
        <small>${esc(al.created_at)}</small>
      </div>
      ${al.resolved ? "<span>Resolved</span>"
        : `<button data-alert="${al.alert_id}">Resolve</button>`}
    </div>`).join("");

  $("alerts").querySelectorAll("button[data-alert]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await fetch(`/api/alerts/${btn.dataset.alert}/resolve`, { method: "POST" });
      refreshAll();
    });
  });
}

// ---------- Wiring ----------
function refreshAll() {
  loadStats().catch(console.error);
  loadAssets().catch(console.error);
  loadAlerts().catch(console.error);
}

let timer;
["q", "category", "zone", "status", "date"].forEach((id) => {
  $(id).addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(loadAssets, 250); // small delay while typing
  });
});

$("clear").addEventListener("click", () => {
  ["q", "category", "zone", "status", "date"].forEach((id) => ($(id).value = ""));
  loadAssets();
});

refreshAll();
setInterval(refreshAll, 10000); // auto-refresh every 10 seconds
