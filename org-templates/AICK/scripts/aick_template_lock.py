r"""
aick_template_lock.py -- deterministic, fail-closed conformance checker for
the Center for AI Civic Knowledge (AICK) Thai preprint house class.

Mirrors the pattern of `scripts/gov_template_lock.py` / `gov-templates/NIA`:
a locked institutional visual/structural identity lives in a fixed class
file (`aick-thai-preprint.cls`, see org-templates/AICK/source/), and every
per-article `.tex` candidate must use it WITHOUT redefining any locked
piece. This tool is a structural gate only -- it never reads or judges the
Thai prose content itself.

What it checks (all four are hard, independent failures; ANY one violation
is a FAIL, exit code 2):

  (a) `\documentclass{aick-thai-preprint}` line -- must be present with the
      exact class name and NO options. Whitespace and a same-line trailing
      `%` comment are tolerated; a different class name or any
      `[options]` block is a violation (the real template ships with no
      options at all, so any option is "added").

  (b) None of the LOCKED class-level identity/color redefinitions may
      appear in the candidate -- these belong only in the .cls:
        \renewcommand{\AICKMakeFrontMatter}
        \renewcommand{\AICKMethodologyPage}
        \def\AICKMakeFrontMatter
        \definecolor{AICKnavy}
        \definecolor{AICKgold}
        \definecolor{AICKgray}
        \definecolor{AICKrulegray}
      (exact names read from the real .cls, org-templates/AICK/source/
      aick-thai-preprint.cls -- not guessed.)

  (c) No `\section` or `\subsection` command may appear before the first
      `\AICKMethodologyPage{` call -- main content must not start before
      the required methodology/status page.

  (d) `\AICKMethodologyPage{` must not appear before `\AICKMakeFrontMatter`
      -- front matter must come first.

A PASS means "the candidate uses the locked class, unmodified, and the
required page order (front matter -> methodology page -> body) holds." It
does NOT check content quality, correct Thai grammar, or the abstract
length guideline (~1,400-1,700 Thai characters) -- see the "What this
checker does NOT check" section in this repo's docs / README for the full
disclosure. This is a structural check only.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

# --- (b) locked identity/color redefinitions -------------------------------
# Exact names taken verbatim from org-templates/AICK/source/aick-thai-preprint.cls
# (\definecolor{AICKnavy}, AICKgold, AICKgray, AICKrulegray; \newcommand{\AICKMakeFrontMatter},
# \newcommand{\AICKMethodologyPage}). We forbid a candidate re-touching any of them via
# \renewcommand, \def, or \definecolor.
_LOCKED_REDEFINITIONS = [
    (r"\renewcommand", r"\AICKMakeFrontMatter"),
    (r"\renewcommand", r"\AICKMethodologyPage"),
    (r"\def", r"\AICKMakeFrontMatter"),
    (r"\definecolor", r"AICKnavy"),
    (r"\definecolor", r"AICKgold"),
    (r"\definecolor", r"AICKgray"),
    (r"\definecolor", r"AICKrulegray"),
]


def _strip_comments(text: str) -> str:
    """Remove LaTeX `%` line comments (an unescaped `%` to end of line),
    leaving line breaks intact so later position-based checks (order of
    \\section vs \\AICKMethodologyPage) still refer to real content, not a
    commented-out mention of the same macro name."""
    out_lines = []
    for line in text.split("\n"):
        i = 0
        cut = len(line)
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line):
                i += 2
                continue
            if line[i] == "%":
                cut = i
                break
            i += 1
        out_lines.append(line[:cut])
    return "\n".join(out_lines)


def _check_documentclass(text: str) -> list[str]:
    findings = []
    m = re.search(r"\\documentclass(\s*\[[^\]]*\])?\s*\{\s*([^}]*?)\s*\}", text)
    if m is None:
        findings.append(
            "(a) missing \\documentclass{aick-thai-preprint} line entirely"
        )
        return findings
    opts, cls_name = m.group(1), m.group(2)
    if cls_name != "aick-thai-preprint":
        findings.append(
            f"(a) \\documentclass uses a different class name: {cls_name!r} "
            "(must be exactly 'aick-thai-preprint')"
        )
    if opts is not None and opts.strip():
        findings.append(
            f"(a) \\documentclass has added options not present in the original "
            f"template: {opts.strip()!r} (the locked line takes no options)"
        )
    return findings


def _check_locked_redefinitions(text: str) -> list[str]:
    findings = []
    for cmd, target in _LOCKED_REDEFINITIONS:
        # e.g. \renewcommand{\AICKMakeFrontMatter} or \renewcommand \AICKMakeFrontMatter
        # target may itself start with a backslash (macro) or be a bare color name.
        pattern = (
            re.escape(cmd)
            + r"\s*\{?\s*"
            + re.escape(target)
            + r"\b"
        )
        m = re.search(pattern, text)
        if m is not None:
            findings.append(
                f"(b) LOCKED redefinition detected: candidate attempts "
                f"'{cmd}{{{target}}}' -- this identity/color belongs only in "
                f"the .cls, never in a per-article .tex "
                f"(context: {text[max(0, m.start()-10):m.end()+15]!r})"
            )
    return findings


def _find_first(text: str, pattern: str) -> "re.Match | None":
    return re.search(pattern, text)


def _check_page_order(text: str) -> list[str]:
    findings = []

    frontmatter_m = _find_first(text, r"\\AICKMakeFrontMatter\b")
    methodology_m = _find_first(text, r"\\AICKMethodologyPage\s*\{")
    section_m = _find_first(text, r"\\(?:sub)?section\*?\s*\{")

    # (c) no \section/\subsection before the first \AICKMethodologyPage{ call
    if methodology_m is not None and section_m is not None:
        if section_m.start() < methodology_m.start():
            findings.append(
                "(c) a \\section/\\subsection command appears BEFORE the first "
                "\\AICKMethodologyPage{ call -- main content must not start "
                f"before the required methodology page "
                f"(section at char {section_m.start()}, methodology page call at "
                f"char {methodology_m.start()})"
            )

    # (d) \AICKMethodologyPage{ must not appear before \AICKMakeFrontMatter
    if methodology_m is not None and frontmatter_m is not None:
        if methodology_m.start() < frontmatter_m.start():
            findings.append(
                "(d) \\AICKMethodologyPage{ appears BEFORE \\AICKMakeFrontMatter "
                "-- front matter must come first "
                f"(methodology page call at char {methodology_m.start()}, "
                f"front matter call at char {frontmatter_m.start()})"
            )

    return findings


def check(candidate_path: pathlib.Path) -> tuple[bool, list[str]]:
    raw = candidate_path.read_text(encoding="utf-8")
    text = _strip_comments(raw)

    findings: list[str] = []
    findings += _check_documentclass(text)
    findings += _check_locked_redefinitions(text)
    findings += _check_page_order(text)

    return (len(findings) == 0), findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    ck = sub.add_parser(
        "check", help="check a candidate .tex against the AICK template lock"
    )
    ck.add_argument("candidate", type=pathlib.Path)

    args = ap.parse_args()

    if args.cmd == "check":
        ok, findings = check(args.candidate)
        if ok:
            print(f"TEMPLATE LOCK PASS: {args.candidate}")
            return 0
        print(f"TEMPLATE LOCK FAIL: {args.candidate}")
        for f in findings:
            print(" -", f)
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
