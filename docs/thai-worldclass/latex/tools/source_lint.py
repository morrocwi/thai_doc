#!/usr/bin/env python3
"""Fail-closed portability lint for arXiv-bound XeLaTeX source.

Accepts either a source directory or a main .tex file. A file target lints the
main file plus sibling .sty files so the command shown in SKILL.md is valid.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


def collect_sources(root: Path) -> list[Path]:
    if root.is_file():
        files = [root] if root.suffix.lower() in {".tex", ".sty"} else []
        files += sorted(p for p in root.parent.glob("*.sty") if p != root)
        return files
    if root.is_dir():
        return sorted(list(root.rglob("*.tex")) + list(root.rglob("*.sty")))
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="source directory or main .tex file")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    texfiles = collect_sources(root)
    if not texfiles:
        print(f"SOURCE LINT FAIL: no .tex/.sty source found at {root}")
        return 2

    fatal: list[str] = []
    warn: list[str] = []
    docclass = 0

    for p in texfiles:
        s = p.read_text(encoding="utf-8", errors="replace")
        docclass += len(re.findall(r"\\documentclass\b", s))
        label = str(p.relative_to(root.parent if root.is_file() else root))

        if re.search(r"\\(?:write18|ShellEscape)\b", s, re.I):
            fatal.append(f"{label}: shell escape primitive found")
        if re.search(r"\\includesvg\b|\\includegraphics(?:\[[^]]*\])?\{[^}]+\.svg\}", s, re.I):
            fatal.append(f"{label}: SVG/on-the-fly conversion found; use final PDF/PNG asset")
        if re.search(r"\\includegraphics(?:\[[^]]*\])?\{/", s):
            fatal.append(f"{label}: absolute figure path found")
        if re.search(r"\\usepackage(?:\[[^]]*\])?\{minted\}", s):
            warn.append(f"{label}: minted usually needs shell escape; prefer listings/verbatim for portable arXiv builds")
        if re.search(r"\\includegraphics(?:\[[^]]*\])?\{[^}]+\.eps\}", s, re.I):
            warn.append(f"{label}: EPS figure found; XeLaTeX portability is safer with final PDF/PNG/JPG")

    if docclass == 0:
        fatal.append("no top-level \\documentclass found in linted source")

    if fatal:
        print("SOURCE LINT FAIL:")
        for x in sorted(set(fatal)):
            print(" -", x)
        return 2

    if warn:
        print("SOURCE LINT WARN:")
        for x in sorted(set(warn)):
            print(" -", x)

    print(f"SOURCE LINT PASS: {len(texfiles)} source file(s); no known arXiv portability blockers found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
