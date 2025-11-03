#!/usr/bin/env python3

import argparse, json, os, pathlib, time, urllib.request

from urllib.error import URLError


def http_get_timed(url: str, timeout: float = 5.0):
    t0 = time.perf_counter()
    e = None
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            _ = r.read(256 * 1024)  # read up to 256KB to simulate light paint
        ok = True
    except URLError as exc:
        ok, e = False, str(exc)
    dt = (time.perf_counter() - t0) * 1000.0
    return {"ok": ok, "ms": round(dt, 2), "err": (e if not ok else None)}


def file_read_timed(path: pathlib.Path):
    t0 = time.perf_counter()
    try:
        b = path.read_bytes()
        ok = True
    except FileNotFoundError:
        ok, b = False, b""
    dt = (time.perf_counter() - t0) * 1000.0
    return {"ok": ok, "ms": round(dt, 2), "bytes": len(b)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.getenv("UI_URL", ""))
    ap.add_argument("--index", default="webui/public/index.html")
    ap.add_argument("--out", default="var/ui/perf.json")
    args = ap.parse_args()

    res = {"ts": time.time(), "mode": "http" if args.url else "file"}
    pathlib.Path("var/ui").mkdir(parents=True, exist_ok=True)

    if args.url:
        res["target"] = args.url
        res["probe"] = http_get_timed(args.url)
    else:
        p = pathlib.Path(args.index)
        res["target"] = str(p)
        res["probe"] = file_read_timed(p)

    pathlib.Path(args.out).write_text(json.dumps(res, indent=2))
    print(json.dumps(res))


if __name__ == "__main__":
    main()
