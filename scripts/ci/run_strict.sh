#!/usr/bin/env bash

# HINT vs STRICT wrapper.

# STRICT if: STRICT_GUARDS=1  OR GITHUB_REF_TYPE=tag  OR current commit has an exact tag.

set -euo pipefail

strict=0

if [ "${STRICT_GUARDS:-0}" = "1" ]; then strict=1; fi

if [ "${GITHUB_REF_TYPE:-}" = "tag" ]; then strict=1; fi

if git describe --exact-match --tags >/dev/null 2>&1; then strict=1; fi

set +e

"$@"

rc=$?

set -e

if [ "$strict" = "1" ]; then exit "$rc"; else exit 0; fi

