#!/usr/bin/env python3
"""
verify_aick_tex.py -- mechanical structural check on a .tex file produced
by aick_generate.py. Does not compile the document; checks textual
structure/ordering invariants that must hold for aick-thai-preprint.cls
to render correctly.

Checks:
  1. \\documentclass{aick-thai-preprint} is present.
  2. \\AICKMakeFrontMatter appears before the first \\section{...}.
  3. \\AICKMethodologyPage appears before the first \\section{...}.
  4. \\begin{document} / \\end{document} counts are balanced (exactly one
     of each, begin before end).
  5. \\begin{AICKReferences} / \\end{AICKReferences} counts are balanced
     (if references were given at all, i.e. either both present once, or
     neither present).

Usage:
    python3 verify_aick_tex.py <file.tex>
Exits 0 and prints PASS lines if every check passes; exits 1 and prints
FAIL lines (with the reason) otherwise.
"""
from __future__ import annotations

import re
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <file.tex>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()

    ok = True

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        status = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        print(f"[{status}] {label}" + (f" -- {detail}" if detail and not cond else ""))

    check(
        "documentclass{aick-thai-preprint} present",
        r"\documentclass{aick-thai-preprint}" in text,
    )

    frontmatter_pos = text.find(r"\AICKMakeFrontMatter")
    methodology_pos = text.find(r"\AICKMethodologyPage")
    first_section_match = re.search(r"\\section\{", text)
    first_section_pos = first_section_match.start() if first_section_match else -1

    check(
        "AICKMakeFrontMatter present",
        frontmatter_pos != -1,
        "macro not found",
    )
    check(
        "AICKMethodologyPage present",
        methodology_pos != -1,
        "macro not found",
    )
    check(
        "first \\section{...} present",
        first_section_pos != -1,
        "no \\section{...} found",
    )

    if frontmatter_pos != -1 and first_section_pos != -1:
        check(
            "AICKMakeFrontMatter appears before first \\section",
            frontmatter_pos < first_section_pos,
            f"frontmatter at {frontmatter_pos}, first section at {first_section_pos}",
        )
    if methodology_pos != -1 and first_section_pos != -1:
        check(
            "AICKMethodologyPage appears before first \\section",
            methodology_pos < first_section_pos,
            f"methodology at {methodology_pos}, first section at {first_section_pos}",
        )

    begin_doc = len(re.findall(r"\\begin\{document\}", text))
    end_doc = len(re.findall(r"\\end\{document\}", text))
    begin_doc_pos = text.find(r"\begin{document}")
    end_doc_pos = text.find(r"\end{document}")
    check(
        "\\begin{document}/\\end{document} balanced (exactly one each)",
        begin_doc == 1 and end_doc == 1,
        f"begin count={begin_doc}, end count={end_doc}",
    )
    if begin_doc == 1 and end_doc == 1:
        check(
            "\\begin{document} appears before \\end{document}",
            begin_doc_pos < end_doc_pos,
        )

    begin_refs = len(re.findall(r"\\begin\{AICKReferences\}", text))
    end_refs = len(re.findall(r"\\end\{AICKReferences\}", text))
    check(
        "\\begin{AICKReferences}/\\end{AICKReferences} balanced",
        begin_refs == end_refs,
        f"begin count={begin_refs}, end count={end_refs}",
    )

    print()
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
