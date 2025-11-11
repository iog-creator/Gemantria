/* Offline-safe live fetch: tries local dev server to regenerate JSON then reloads it. */
async function liveFetchCatalog() {
  const s = document.getElementById("status");
  const btn = document.getElementById("btn-live");
  if (btn) btn.disabled = true;
  try {
    s.textContent = "Regenerating catalog via dev server…";
    const r = await fetch("http://127.0.0.1:8777/export", { method: "POST" });
    const j = await r.json().catch(() => ({ ok: false }));
    if (j && j.ok) {
      s.textContent = "Regenerated. Reloading…";
    } else {
      s.textContent = "Dev server not running or exporter failed — staying on stub JSON.";
    }
  } catch (_) {
    s.textContent = "Dev server unreachable — staying on stub JSON.";
  } finally {
    // reload the catalog JSON with cache-busting; viewer page should have loadCatalog()
    if (typeof loadCatalog === "function") {
      await loadCatalog(true); // true => cache-bust
    }
    if (btn) btn.disabled = false;
  }
}

