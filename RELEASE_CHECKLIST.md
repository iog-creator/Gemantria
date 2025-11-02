# Release Checklist — v0.1.0-rc1

- [ ] SSOT gates green: `ruff format --check . && ruff check .` and `make ops.verify`
- [ ] Smokes: `make ci.pipeline.smoke ci.exports.smoke ci.webui.smoke ci.quality.smoke`
- [ ] Quick-start verified: `make cli.quickstart`
- [ ] No duplicate scaffolds per Rule-054 (guard enforced)
- [ ] Tag created: `v0.1.0-rc1` and pushed
