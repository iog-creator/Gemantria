# LM Indicator Widget Contract (SSOT)

Canonical machine signal: `share/atlas/control_plane/lm_indicator.json`

## Contract (props)

- status: offline | healthy | degraded

- reason: db_off | no_calls | high_error_rate | ok

- label: short human-readable status line

- color: grey | green | yellow | red

- icon: name from shared icon set

- tooltip_lines: [...short lines...]

- metrics:

    - successRate: number|null

    - errorRate: number|null

    - totalCalls: integer|null

    - dbOff: boolean

    - topErrorReason: string|null

    - windowDays: integer

    - generatedAt: timestamp

## Adapter Rules

- Hermetic (file only)

- Fail-closed (offline-safe if missing/invalid)

- Zero heuristics; classification is upstream

