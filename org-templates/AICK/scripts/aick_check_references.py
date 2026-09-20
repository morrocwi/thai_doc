#!/usr/bin/env python3
"""
aick_check_references.py -- thin reference-checker wrapper for the
Center for AI Civic Knowledge (AICK) Thai preprint house template.

This script does NOT implement any citation-verification logic itself.
It only:
  1. Extracts reference strings from a candidate AICK source, either
     a rendered .tex file (the \\item lines inside the AICKReferences
     environment -- see org-templates/AICK/source/aick-paper-template.tex)
     or a structured data file (the `references:` list, validated
     against org-templates/AICK/schema/aick_paper.schema.json).
  2. For each reference string, shells out to glosa's ad-hoc single
     reference checker (scripts/cite_check_adhoc.py) and captures its
     JSON output verbatim.
  3. Prints a combined report: the full JSON array of per-reference
     results, plus a short human-readable summary table.

glosa location: this script never hardcodes a worktree path. It reads
the glosa repo root from the GLOSA_REPO_PATH environment variable,
defaulting to ~/ANSE.ASIA/glosa (the normal checkout). If that path
does not exist, or scripts/cite_check_adhoc.py is not found inside it,
this script FAILS LOUDLY (non-zero exit, clear stderr message) instead
of silently skipping reference checking.

Usage
-----
    python3 aick_check_references.py --tex <candidate.tex>
    python3 aick_check_references.py --data <data.yaml|data.json>

    GLOSA_REPO_PATH=/path/to/glosa python3 aick_check_references.py --data ...
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

import yaml

_HERE = pathlib.Path(__file__).parent
_AICK_ROOT = _HERE.parent

_DEFAULT_GLOSA_REPO_PATH = pathlib.Path.home() / "ANSE.ASIA" / "glosa"
_GLOSA_CHECKER_RELPATH = pathlib.Path("scripts") / "cite_check_adhoc.py"

# Matches one \item's body up to the next \item or the end of the
# AICKReferences environment. Mirrors the exact syntax in
# org-templates/AICK/source/aick-paper-template.tex:
#   \begin{AICKReferences}
#   \item ผู้แต่ง. (ปี). ชื่อบทความ. ...
#   \item ผู้แต่ง. (ปี). \textit{ชื่อหนังสือ}. สำนักพิมพ์.
#   \end{AICKReferences}
_REFERENCES_ENV_RE = re.compile(
    r"\\begin\{AICKReferences\}(.*?)\\end\{AICKReferences\}",
    re.DOTALL,
)
_ITEM_RE = re.compile(r"\\item\s+(.*?)(?=\\item\s|\Z)", re.DOTALL)


def resolve_glosa_checker() -> pathlib.Path:
    """Return the path to glosa's cite_check_adhoc.py, or fail loudly."""
    repo_path_str = os.environ.get("GLOSA_REPO_PATH")
    repo_path = pathlib.Path(repo_path_str).expanduser() if repo_path_str else _DEFAULT_GLOSA_REPO_PATH

    if not repo_path.exists():
        sys.exit(
            "aick_check_references.py: FATAL -- glosa repo not found at "
            f"'{repo_path}'. Reference checking depends on glosa's "
            "scripts/cite_check_adhoc.py and cannot proceed without it. "
            "Set GLOSA_REPO_PATH to a valid glosa checkout, or clone/update "
            f"the default location ({_DEFAULT_GLOSA_REPO_PATH})."
        )

    checker_path = repo_path / _GLOSA_CHECKER_RELPATH
    if not checker_path.exists():
        sys.exit(
            "aick_check_references.py: FATAL -- glosa repo found at "
            f"'{repo_path}' but its citation checker is missing at "
            f"'{checker_path}'. Reference checking cannot proceed without "
            "it -- refusing to silently skip reference checking. Confirm "
            "glosa's citation-checker work has been merged/pulled into "
            "this checkout."
        )

    return checker_path


def extract_references_from_tex(tex_path: pathlib.Path) -> list[str]:
    text = tex_path.read_text(encoding="utf-8")
    env_match = _REFERENCES_ENV_RE.search(text)
    if not env_match:
        sys.exit(
            f"aick_check_references.py: FATAL -- no AICKReferences environment "
            f"found in '{tex_path}' (expected \\begin{{AICKReferences}} ... "
            "\\end{AICKReferences} as in "
            "org-templates/AICK/source/aick-paper-template.tex)."
        )
    body = env_match.group(1)
    items = [m.group(1).strip() for m in _ITEM_RE.finditer(body)]
    items = [item for item in items if item]
    return items


def extract_references_from_data(data_path: pathlib.Path) -> list[str]:
    text = data_path.read_text(encoding="utf-8")
    if data_path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)

    if not isinstance(data, dict):
        sys.exit(
            f"aick_check_references.py: FATAL -- '{data_path}' did not parse "
            "to a mapping matching org-templates/AICK/schema/aick_paper.schema.json."
        )

    references = data.get("references", [])
    if references is None:
        references = []
    if not isinstance(references, list) or not all(isinstance(r, str) for r in references):
        sys.exit(
            f"aick_check_references.py: FATAL -- '{data_path}' has a "
            "`references` field that is not a list of strings, per "
            "org-templates/AICK/schema/aick_paper.schema.json."
        )
    return references


def run_glosa_check(checker_path: pathlib.Path, reference: str) -> dict:
    """Shell out to glosa's cite_check_adhoc.py for one reference string."""
    try:
        proc = subprocess.run(
            [sys.executable, str(checker_path), "--reference", reference],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        sys.exit(
            "aick_check_references.py: FATAL -- could not execute glosa's "
            f"citation checker at '{checker_path}': {exc}"
        )

    if proc.returncode != 0:
        sys.exit(
            "aick_check_references.py: FATAL -- glosa's citation checker "
            f"exited with status {proc.returncode} for reference "
            f"{reference!r}.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(
            "aick_check_references.py: FATAL -- glosa's citation checker "
            f"produced non-JSON output for reference {reference!r}: {exc}\n"
            f"stdout was:\n{proc.stdout}"
        )


def truncate(text: str, width: int = 60) -> str:
    text = " ".join(text.split())
    if len(text) <= width:
        return text
    return text[: width - 1] + "\u2026"


def render_table(results: list[dict]) -> str:
    header = f"{'#':>2}  {'reference':<62}  {'existence_tier':<16}  {'venue_tier':<28}  disclosure"
    lines = [header, "-" * len(header)]
    for i, result in enumerate(results, start=1):
        ref_short = truncate(result.get("reference", ""), 60)
        existence_tier = result.get("existence_tier", "")
        venue_tier = (result.get("venue_tier") or {}).get("tier", "")
        disclosure = truncate(result.get("disclosure", ""), 50)
        lines.append(
            f"{i:>2}  {ref_short:<62}  {existence_tier:<16}  {venue_tier:<28}  {disclosure}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Thin wrapper: extract AICK reference-list entries (from a "
            "rendered .tex or a structured data file) and check each one "
            "via glosa's ad-hoc citation checker."
        )
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--tex", type=pathlib.Path, help="Path to a candidate AICK .tex file.")
    source_group.add_argument(
        "--data", type=pathlib.Path, help="Path to a data.yaml/data.json matching aick_paper.schema.json."
    )
    args = parser.parse_args()

    checker_path = resolve_glosa_checker()

    if args.tex is not None:
        if not args.tex.exists():
            sys.exit(f"aick_check_references.py: FATAL -- --tex path not found: '{args.tex}'.")
        references = extract_references_from_tex(args.tex)
    else:
        if not args.data.exists():
            sys.exit(f"aick_check_references.py: FATAL -- --data path not found: '{args.data}'.")
        references = extract_references_from_data(args.data)

    if not references:
        print("aick_check_references.py: no references found -- nothing to check.", file=sys.stderr)
        print("[]")
        return

    results = [run_glosa_check(checker_path, reference) for reference in references]

    print(json.dumps(results, indent=1, ensure_ascii=False))
    print()
    print(render_table(results))


if __name__ == "__main__":
    main()
