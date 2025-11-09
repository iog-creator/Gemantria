#!/usr/bin/env python3

import argparse, sys

TPL = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {text}">
  <linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".1" stop-opacity=".1"/><stop offset=".9" stop-opacity=".3"/><stop offset="1" stop-opacity=".5"/></linearGradient>
  <mask id="m"><rect width="{w}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{rw}" height="20" fill="{color}"/>
    <rect width="{w}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{lx}" y="15">{label}</text>
    <text x="{rx}" y="15">{text}</text>
  </g>
</svg>"""

def badge(label: str, text: str):
    color = "#e05d44" if text.lower()=="fail" else "#4c1"
    lw = max(60, 6*len(label))    # crude text fit
    rw = max(50, 7*len(text))
    w  = lw + rw
    return TPL.format(w=w,lw=lw,rw=rw,lx=lw/2,rx=lw+rw/2,label=label,text=text,color=color)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--status", required=True)  # PASS or FAIL
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    svg = badge(args.label, args.status)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(args.out)
