import glob
import re
import sys


def main() -> None:
    files = glob.glob(".cursor/rules/*.mdc")
    nums = []

    for f in files:
        m = re.search(r"/(\d{3})-", f)
        if m:
            nums.append(m.group(1))

    dup = sorted({n for n in nums if nums.count(n) > 1})
    if dup:
        print("[rules.numbering.check] duplicate rule numbers:", ", ".join(dup))
        sys.exit(1)

    for must in ("037", "038"):
        c = nums.count(must)
        if c != 1:
            print(f"[rules.numbering.check] expected exactly one {must}, found {c}")
            sys.exit(1)

    print("[rules.numbering.check] OK")


if __name__ == "__main__":
    main()
