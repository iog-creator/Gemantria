(function () {
  const d = document;
  const $ = (sel) => d.querySelector(sel);
  const app = $("#app") || d.body;

  function el(tag, attrs = {}, ...kids) {
    const n = d.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => (k === "class" ? (n.className = v) : n.setAttribute(k, v)));
    kids.flat().forEach((k) => n.appendChild(typeof k === "string" ? d.createTextNode(k) : k));
    return n;
  }

  async function loadCatalog() {
    const out = $("#out") || app.appendChild(el("div", { id: "out" }));
    out.innerHTML = "Loading catalog…";
    try {
      const res = await fetch("data/mcp_catalog.json", { cache: "no-store" });
      if (!res.ok) throw new Error("fetch failed: " + res.status);
      const j = await res.json();
      const tbl = el(
        "table",
        { id: "catalogTable", border: "1", cellpadding: "6", style: "border-collapse:collapse;margin:8px 0;max-width:900px;" },
        el(
          "thead",
          {},
          el(
            "tr",
            {},
            el("th", {}, "Endpoint"),
            el("th", {}, "Inputs"),
            el("th", {}, "max_k"),
            el("th", {}, "version")
          )
        ),
        el(
          "tbody",
          {},
          (j.endpoints || []).map((e) =>
            el(
              "tr",
              {},
              el("td", {}, e.name || ""),
              el("td", {}, Array.isArray(e.spec?.inputs) ? e.spec.inputs.join(", ") : ""),
              el("td", {}, String(e.spec?.max_k ?? "")),
              el("td", {}, String(e.spec?.version ?? ""))
            )
          )
        )
      );
      const raw = el("pre", { id: "raw", style: "background:#111;color:#eee;padding:8px;overflow:auto;max-width:900px;" }, JSON.stringify(j, null, 2));
      out.innerHTML = "";
      out.appendChild(tbl);
      out.appendChild(raw);
      $("#status").textContent = `Loaded ${(j.endpoints || []).length} endpoints`;
    } catch (err) {
      out.innerHTML = "";
      out.appendChild(el("div", { style: "color:#c00;" }, "Failed to load catalog (offline-safe fallback still available)."));
      out.appendChild(el("pre", {}, String(err)));
      $("#status").textContent = "Load failed";
    }
  }

  // Wire button
  d.addEventListener("DOMContentLoaded", () => {
    const btn = $("#reloadBtn");
    if (btn) btn.addEventListener("click", loadCatalog);
    // Auto-load once on open for convenience
    loadCatalog();
  });
})();

