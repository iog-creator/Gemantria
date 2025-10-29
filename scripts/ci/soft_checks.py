#!/usr/bin/env python3
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'share' / 'eval' / 'soft_checks'
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / 'soft_checks.log'

CMDS = [
    ('ruff', ['ruff', 'check', '.', '--quiet'], 'HINT: ruff.check'),
    ('mypy', ['mypy', '.'], 'HINT: mypy'),
    ('pytest', ['pytest', '-q'], 'HINT: pytest'),
]

def run(cmd):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, '', 'missing: ' + cmd[0]

results = []
for name, cmd, tag in CMDS:
    if shutil.which(cmd[0]) is None:
        print(tag + ' skipped (tool not installed)')
        results.append({'tool': name, 'rc': 127, 'stdout': '', 'stderr': 'not installed'})
        continue
    rc, out, err = run(cmd)
    print(tag + ' rc=' + str(rc))
    if out:
        print('HINT: ' + name + '.out.head=
' + '
'.join(out.splitlines()[:20]))
    if err:
        print('HINT: ' + name + '.err.head=
' + '
'.join(err.splitlines()[:20]))
    results.append({'tool': name, 'rc': rc, 'stdout': out[-4000:], 'stderr': err[-4000:]})

LOG.write_text(json.dumps(results, indent=2), encoding='utf-8')
print('HINT: soft_checks.log saved at ' + str(LOG))

if not os.environ.get('GEMATRIA_DSN'):
    print('HINT: env.GEMATRIA_DSN missing - DB-related checks were not executed (soft)')

sys.exit(0)
