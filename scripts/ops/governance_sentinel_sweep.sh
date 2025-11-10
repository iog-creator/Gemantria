#!/usr/bin/env bash
set -euo pipefail

gov_files=(AGENTS.md RULES_INDEX.md)

# 1) Remove stray sentinels from NON-governance files
mapfile -t all_with_sentinel < <(rg -l 'alwaysapply\.sentinel' --hidden --glob '!**/.git/**' 2>/dev/null || true)
for f in "${all_with_sentinel[@]}"; do
  if [[ ! " ${gov_files[*]} " =~ " $(basename "$f") " ]]; then
    tmp="$(mktemp)"
    grep -v -E 'alwaysapply\.sentinel' "$f" > "$tmp" || true
    mv "$tmp" "$f"
    echo "Removed sentinels from: $f"
  fi
done

# 2) Normalize governance docs: remove all, insert one canonical after first H1 (or EOF)
for f in "${gov_files[@]}"; do
  [[ -f "$f" ]] || continue
  
  # Remove all existing sentinels
  tmp="$(mktemp)"
  grep -v -E 'alwaysapply\.sentinel' "$f" > "$tmp" || true
  mv "$tmp" "$f"
  
  # Insert one canonical sentinel after first H1 (or at EOF if no H1)
  tmp="$(mktemp)"
  awk -v canon="$canon" '
    BEGIN{ins=0}
    {
      if(!ins && $0 ~ /^# /){ print; print canon; ins=1; next }
      print
    }
    END{ if(!ins) print canon }
  ' "$f" > "$tmp"
  mv "$tmp" "$f"
  
  echo "Normalized: $f (one canonical sentinel)"
done

echo "Governance sentinel sweep complete"

