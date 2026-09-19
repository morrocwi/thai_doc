#!/usr/bin/env python3
"""Create a minimal arXiv source ZIP and fail closed on unsafe input."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

IGNORE_EXT = {
    ".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk",
    ".synctex", ".xdv", ".pdf", ".preflight.txt",
}
IGNORE_NAMES = {".DS_Store"}
IGNORE_SUFFIXES = (".synctex.gz", ".preflight.txt")


def ignored(p: Path) -> bool:
    if p.name in IGNORE_NAMES:
        return True
    if p.suffix in IGNORE_EXT:
        return True
    if any(p.name.endswith(s) for s in IGNORE_SUFFIXES):
        return True
    if any(part.startswith(".") for part in p.parts):
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_dir")
    ap.add_argument("-o", "--output", default="arxiv-source.zip")
    args = ap.parse_args()

    root = Path(args.source_dir).resolve()
    out = Path(args.output).resolve()
    if not root.is_dir():
        print(f"FAIL source_dir is not a directory: {root}")
        return 2
    if root == out or root in out.parents:
        # Output inside source tree can accidentally package itself on reruns.
        print("FAIL output ZIP must be outside the source directory")
        return 2

    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if ignored(rel):
            continue
        files.append((p, rel))

    if not any(rel.suffix.lower() == ".tex" for _, rel in files):
        print("FAIL no .tex file would be included in arXiv source ZIP")
        return 2

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p, rel in files:
            z.write(p, rel)

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
