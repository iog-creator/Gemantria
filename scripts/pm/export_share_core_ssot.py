import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SSOT = ROOT / "docs" / "SSOT"
SHARE = ROOT / "share"

EXPORTS = [
    (SSOT / "PM_HANDOFF_PROTOCOL.md", SHARE / "PM_HANDOFF_PROTOCOL.md"),
    (SSOT / "SHARE_FOLDER_ANALYSIS.md", SHARE / "SHARE_FOLDER_ANALYSIS.md"),
    (SSOT / "PHASE27A_IMPLEMENTATION_EVIDENCE.md", SHARE / "PHASE27A_IMPLEMENTATION_EVIDENCE.md"),
]


def copy_if_exists(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"[WARN] missing SSOT source: {src}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[OK] {src} -> {dst}")


def main() -> None:
    for src, dst in EXPORTS:
        copy_if_exists(src, dst)
    print("[DONE] core SSOT exports -> share/ complete (see [WARN] above if any).")


if __name__ == "__main__":
    main()
