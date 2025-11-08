# Cursor Browser QA — XRef Visualization

## Purpose

Use Cursor's **Browser** tool to visually validate the Cross-References UI (chips + side panel), and attach screenshots in the PR.

## Preconditions

- Branch: `webui/xrefs-chips` (or main after merge)
- Data: `ui/derived/xrefs_index.v1.json` present (1687 nodes / 5554 xrefs)
- Dev server: `ui` app runs (Vite)

## Steps (Cursor)

1) Open the repo in **Cursor**.

2) Start the UI:

   - Terminal: `cd ui && npm ci && npm run dev` (note the localhost URL it prints)

3) Open **Tools → Browser** in Cursor.

4) Navigate to: `http://localhost:5173` (or the printed dev URL)

   - Go to the **Cross-References** tab / demo page.

5) Visually verify:

   - Chips render (first 5 visible + "+N more")
   - Hover style changes
   - Click opens the **Side Panel**; close button works
   - Search filters noun cards (Hebrew / gematria)

6) Capture screenshots:

   - Main grid state
   - Chip hover
   - Side panel open

7) Attach screenshots in the PR as a comment:

   - Title: **Cursor Browser QA — XRef Visualization**
   - Include browser URL, steps, and ✅/⚠️ notes.

## Notes

- This QA is **manual**; see also the optional Playwright smoke below for a scripted snapshot.

