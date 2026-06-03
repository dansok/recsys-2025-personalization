const healthEl = document.querySelector("#health");
const personaEl = document.querySelector("#persona");
const profileEl = document.querySelector("#profile");
const queryEl = document.querySelector("#query");
const searchEl = document.querySelector("#search");
const resultsEl = document.querySelector("#results");
const latencyEl = document.querySelector("#latency");

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderProfile(profile) {
  profileEl.innerHTML = `
    <dt>Client</dt><dd>${profile.client_id}</dd>
    <dt>Categories</dt><dd>${escapeHtml(profile.top_categories.join(", "))}</dd>
    <dt>Avg price</dt><dd>${profile.avg_price}</dd>
    <dt>History SKUs</dt><dd>${profile.history_sku_count}</dd>
    <dt>Val targets</dt><dd>${profile.validation_target_count}</dd>
    <dt>Recent tokens</dt><dd>${escapeHtml(profile.recent_query_tokens.join(" "))}</dd>
  `;
}

function renderResults(results) {
  if (!results.length) {
    resultsEl.innerHTML = `<div class="empty">No candidates matched this role/search combination.</div>`;
    return;
  }
  resultsEl.innerHTML = results.map((item, idx) => `
    <article class="result">
      <div class="rank">${idx + 1}</div>
      <div>
        <p class="result-title">SKU ${item.sku}</p>
        <p class="meta">Category ${item.category} · price bucket ${item.price} · ${item.was_validation_target ? "validation target" : "candidate"}</p>
        <p class="why">category match: ${item.explanation.category_match} · price affinity: ${item.explanation.price_affinity.toFixed(3)} · query overlap: ${item.explanation.query_name_overlap.toFixed(3)}</p>
      </div>
      <div class="score">${item.score.toFixed(3)}</div>
    </article>
  `).join("");
}

async function loadPersonas() {
  const health = await getJson("/health");
  healthEl.textContent = health.dataset_present ? "Dataset loaded" : "Dataset missing";
  healthEl.classList.toggle("ok", health.dataset_present);

  const payload = await getJson("/personas?limit=20");
  personaEl.innerHTML = payload.personas.map((persona) => `
    <option value="${persona.client_id}" data-category="${persona.top_category}">
      ${persona.name} · ${persona.summary}
    </option>
  `).join("");
  if (payload.personas.length) {
    queryEl.value = `category:${payload.personas[0].top_category}`;
    await runSearch();
  }
}

async function runSearch() {
  const clientId = personaEl.value;
  if (!clientId) return;
  const start = performance.now();
  resultsEl.innerHTML = `<div class="empty">Ranking products for selected role...</div>`;
  const params = new URLSearchParams({ client_id: clientId, q: queryEl.value, limit: "12" });
  const payload = await getJson(`/search?${params.toString()}`);
  renderProfile(payload.profile);
  renderResults(payload.results);
  latencyEl.textContent = `${Math.round(performance.now() - start)} ms`;
}

personaEl.addEventListener("change", async () => {
  const selected = personaEl.options[personaEl.selectedIndex];
  queryEl.value = `category:${selected.dataset.category}`;
  await runSearch();
});
searchEl.addEventListener("click", runSearch);
queryEl.addEventListener("keydown", async (event) => {
  if (event.key === "Enter") await runSearch();
});

loadPersonas().catch((error) => {
  healthEl.textContent = "API error";
  resultsEl.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
});
