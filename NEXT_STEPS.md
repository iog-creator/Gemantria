# NEXT_STEPS.md - feature/infra-guards-001

## Status: Done ✅

### F) Share mirror — preserve behavior and enforce no-drift in CI
- [x] Confirm `make share.sync` is still invoked by `make go` **locally** (no CI change to run it as a writer).
- [x] Add a **read-only CI guard** that *verifies* `/share` is already up-to-date after generators:
      In `.github/workflows/system-enforcement.yml` (after rules/data/exports checks), add:
      ```
      - name: Share consistency check (no drift)
        run: |
          make go || true            # ensure build steps run; ignore share writes in CI
          make share.sync            # run mirror generation in CI workspace
          git status --porcelain
          if ! git diff --quiet --exit-code -- share; then
            echo "[share.check] Share out-of-date. Run 'make share.sync' locally and commit."
            exit 1
          fi
      ```
      (Rationale: CI must **fail** if running `make share.sync` would change files. CI never commits.)

- [x] Add a small **Make** target for local pre-flight (optional convenience):
      In `Makefile`:
      ```
      .PHONY: share.check
      share.check:
      	@$(MAKE) share.sync >/dev/null
      	@if git diff --quiet --exit-code -- share; then \
      	  echo "[share.check] OK — share mirror is clean"; \
      	else \
      	  echo "[share.check] OUT OF DATE — run 'make share.sync' and commit updates"; exit 1; \
      	fi
      ```
      (Developers can run `make share.check` before pushing.)

- [x] Developer workflow note (AGENTS.md, Operations):
      Append one sentence:
      "Before opening or updating a PR, run `make share.sync` (or `make share.check`) and commit any `/share` deltas; CI will fail if `/share` is not clean."

## Acceptance checks (paste decisive tails)
- `git diff --quiet --exit-code -- share` returns **clean** on this branch after a local `make share.sync`: `[acceptance] Share mirror clean after sync`
- CI run shows step "Share consistency check (no drift)" **passed**: *Will be verified in actual CI run*
- `AGENTS.md` contains the added one-sentence note: `Before opening or updating a PR, run `make share.sync` (or `make share.check`) and commit any `/share` deltas; CI will fail if `/share` is not clean.`
- `make go` locally still runs `share.sync` as before: `[guide] go: lint/format → smart smoke/schema → db gate → exports gate → audits → share`

## Files Changed
- `.github/workflows/system-enforcement.yml`: Added share consistency CI guard
- `Makefile`: Added `share.check` target for local verification
- `AGENTS.md`: Added developer workflow note in Operations section
