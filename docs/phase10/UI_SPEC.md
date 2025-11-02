# Gemantria UI Integration Spec (Hermetic, Contract-First)

Status: **authoritative** spec for any UI delivered back.  
CI policy: **No Node in CI.** UI runs locally only. Data contract is file-based.

---

## 1) Data Contract

**Input**: `/tmp/p9-ingest-envelope.json` (built via `make ingest.local.envelope`)  
Schema (draft): `docs/phase9/ingest_envelope.schema.draft.json`.

TypeScript shape:

```ts
export type Envelope = {
  meta: {
    version: string;
    source: string;
    snapshot_path: string;
    seed: number;
    created_at?: string; // ISO8601
  };
  nodes: Array<{ id: string; label: string; type?: string; attrs?: Record<string, unknown> }>;
  edges: Array<{ src: string; dst: string; rel_type: string; weight?: number }>;
};
```

**Performance budget**: smooth to ~5k nodes / ~20k edges; if higher, use sampling/pagination.

---

## 2) Loading Modes (pick at least one)

* **A) File Picker / Drag-Drop (recommended, zero infra)**

  Let the user choose the JSON file (or drag-drop). Parse in-browser.

* **B) Dev-Served File (optional)**

  Copy the envelope into your dev server's static root and fetch it:

  ```
  # Example (operator)
  OUT_FILE=/tmp/p9-ingest-envelope.json make ingest.local.envelope
  cp /tmp/p9-ingest-envelope.json ui/public/envelope.json
  # UI fetches /envelope.json at dev-time
  ```

  Do not hardwire absolute `/tmp/...` in fetch; use `/envelope.json`.

* **C) HTTP Adapter (future, not used today)**

  GET `/api/envelope` → Envelope (we'll provide later). Keep adapter boundary.

---

## 3) Adapter Boundary

Define a provider interface and implement a **FileProvider** (and optionally a DevHTTPProvider). Do not import `fetch` directly in views.

```ts
export interface EnvelopeProvider { load(): Promise<Envelope>; }

export class FileProvider implements EnvelopeProvider {
  constructor(private fileHandle?: File) {}
  async load(): Promise<Envelope> { /* use FileReader from picker/drag-drop */ }
}

export class DevHTTPProvider implements EnvelopeProvider {
  constructor(private url = "/envelope.json") {}
  async load(): Promise<Envelope> { return fetch(this.url).then(r => r.json()); }
}
```

---

## 4) Minimal Features (MVP)

* **Meta panel**: render `meta` verbatim.
* **Counts panel**: show nodes/edges (+ optional density).
* **Graph preview**: pan/zoom, label tooltip; optional color by `type`.
* **Temporal strip**: visualize `meta.created_at` (single point ok).
* **Filters**: label text filter; `type` multi-select; `rel_type` multi-select; weight slider (0..1).
* **Exports (local)**: filtered `{nodes,edges}` JSON to `ui/out/` (gitignored).

---

## 5) Events (UI → Host)

* `envelopeLoaded`: `{ nodeCount, edgeCount, meta }`
* `filterChanged`: `{ text?, types?, relTypes?, minWeight? }`
* `selectionChanged`: `{ nodeIds: string[], edgeIds: string[] }`
* `exportCompleted`: `{ path, nodes, edges }`

Use your framework's event bus or a simple callback registry.

---

## 6) Layout (suggested)

```
ui/
  src/
    lib/               # providers, parsing, metrics
    types/             # Envelope types
    components/        # Meta, Counts, Graph, Temporal, Toolbar
    app/               # App shell
  public/              # (optional) envelope.json for dev fetch
  out/                 # exports (gitignored)
```

---

## 7) Error & UX Baseline

* Parse errors are inline; app stays responsive; "Load another file" action.
* Empty arrays are valid; missing optional fields treated as empty.
* Progressive rendering for large files; counts render first.
* A11y: keyboard pan/zoom; focus management; WCAG AA contrast.

---

## 8) Acceptance (hand-back)

* [ ] Loads via file picker (and/or `/envelope.json`) with **no network/DB**.
* [ ] Renders meta + counts deterministically with our sample envelope.
* [ ] Graph preview + temporal strip render without errors.
* [ ] Filters update counts/preview under 100ms for 5k/20k budget.
* [ ] Exports to `ui/out/` (gitignored).
* [ ] Adapter boundary present (`EnvelopeProvider`).
* [ ] No CI changes; no lockfiles/`node_modules` committed.
