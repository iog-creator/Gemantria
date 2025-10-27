#!/usr/bin/env python3
# Minimal self-contained SVG badge generator (no deps).
# Usage: gen_badge.py "label" "value" "color" > badge.svg
import sys

label, value, color = (sys.argv + ["", "", ""])[1:4]
# Basic left/right boxes; keeps it tiny & readable.
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="160" height="20"
     role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="m"><rect width="160" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="90" height="20" fill="#555"/>
    <rect x="90" width="70" height="20" fill="{color}"/>
    <rect width="160" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle"
     font-family="DejaVu Sans,Verdana,Geneva,sans-serif"
     font-size="11">
    <text x="45" y="14">{label}</text>
    <text x="125" y="14">{value}</text>
  </g>
</svg>"""
print(svg)
