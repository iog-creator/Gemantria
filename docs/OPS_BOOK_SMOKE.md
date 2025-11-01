# Book Pipeline — Local Smoke

Run a deterministic dry-run:

```bash
make book.smoke
```

Acceptance: no unhandled exceptions; clear service gates; no CI writes to `share/**`.
