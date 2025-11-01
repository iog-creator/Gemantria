## v0.9.0 — Post-merge hardening + evaluation suite

- **Post-merge hardening**: Added CODEOWNERS, RELEASES.md process, required checks badges
- **Branch protection**: Main branch now requires `ruff` + `ci/build` checks before merging
- **Advanced calibration**: `make eval.graph.calibrate.adv` target with OPS_CALIBRATION.md
- **Book smoke testing**: `make book.smoke` dry-run target with OPS_BOOK_SMOKE.md
- **Quality badges**: README now embeds live quality trend/status badges
- **Codex CLI integration**: Optional local CLI integration (CI-gated)
- **Ruff pinning**: CI workflows pin ruff==0.13.0 with version verification

## v0.8.1 — Phase-8 shipping UX (local-only)

- **Embed badges in HTML**: Status badges now render inline in `share/eval/index.html`
- **Strict packaging variant**: `eval.package.strict` fails fast if strict policy has FAILs
- **Release manifest**: `share/eval/release_manifest.json` lists all artifacts with size + SHA256
- **Manifest viewer**: Dashboard renders manifest summary + first 200 artifacts in expandable table
- **Download-all bundle**: `eval.bundle.all` creates deterministic tar.gz of entire eval directory
- **Integrity verifier**: `eval.verify.integrity` checks all artifacts against manifest hashes
- **Convenience launcher**: `eval.open` opens dashboard in browser
- **Governance hook**: `ops.verify` conditionally runs integrity verification when manifest exists

## v0.0.6 — Infra hardening

- CI workflow (doctor + docs/rules checks)
- Makefile `preflight` & `run.small`
- Standardized bootstrap/doctor flow for local runs
