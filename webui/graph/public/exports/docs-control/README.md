# Docs Control Panel Exports

This directory contains JSON exports for the Doc Control Panel UI.

## Source

Files are automatically synced from `share/exports/docs-control/` during the build process via `npm run sync-doc-exports`.

## Generation

To regenerate these files, run:

```bash
pmagent docs dashboard-refresh
```

Then rebuild the webui:

```bash
cd webui/graph
npm run build
```

## Files

- `summary.json` - Overview statistics
- `canonical.json` - Canonical documents list
- `archive-candidates.json` - Archive candidate groups
- `unreviewed-batch.json` - Unreviewed documents batch
- `orphans.json` - Orphaned files/directories
- `archive-dryrun.json` - Archive dry-run results

## Serving

These files are served statically at `/exports/docs-control/*.json` when the web UI is running.

