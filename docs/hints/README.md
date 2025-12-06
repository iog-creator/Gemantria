# Gemantria Hints System

This directory contains diagnostic hints for common errors and configuration issues.

## Active Hints

- **HINT-ENV-001**: [venv not activated](./HINT-ENV-001-venv-not-activated.md)
  - **Trigger**: GEMATRIA_DSN empty, ModuleNotFoundError
  - **Fix**: Activate .venv and set PYTHONPATH

- **HINT-DB-001**: [DSN mandatory](./HINT-DB-001-dsn-mandatory.md)  
  - **Trigger**: Agent proceeds without required DSN
  - **Fix**: STOP immediately, configure DSN in .env
  - **Severity**: CRITICAL - Governance violation

## Usage

When a script or agent encounters an error:
1. Check symptoms against hint triggers
2. Follow exact fix steps in the hint document
3. Verify fix using verification commands
4. Resume work only after fix is confirmed

## Adding New Hints

Format: `HINT-<CATEGORY>-<NUMBER>-<short-name>.md`

Categories:
- `ENV` - Environment/setup issues
- `DB` - Database connection/schema issues
- `DEP` - Dependency/package issues
- `CONFIG` - Configuration errors

Each hint must include:
- Problem Detection (symptoms, root cause)
- Exact Fix (commands, configuration)
- Why It Matters (governance rules, impact)
- Related Documentation (links)
