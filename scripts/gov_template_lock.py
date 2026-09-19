"""
gov_template_lock.py -- extract an exact-conformance "lock" spec from an
authoritative government-agency source document, and mechanically check a
candidate draft against it. This is a hard fail-closed gate, not a style
checker: per founder instruction ("เทมเพลทต้องตามนี้ 100% ... ทำตัวบล็อกไว้ด้วย" --
the template must be followed 100%, build a block/gate for it), the fixed
institutional wording in a `gov-templates/<AGENCY>/source/*.docx` file is
NEVER to be paraphrased, reordered, or dropped by an AI drafting from it.

How it works
------------
An authoritative source document (e.g. an NIA official letter template) is
made of two kinds of content:
  - FIXED text: the agency's own wording, verbatim, that every submission
    using this template must reproduce exactly (subject/greeting boilerplate,
    legal/procedural phrases, closing, signature block labels, ...).
  - PLACEHOLDER spans: dot-leader runs (".........", "……….") that mark where
    a specific submission fills in its own content, often with an inline
    label in parentheses, e.g. ".............(ชื่อโครงการ)............." for
    "project name goes here".

`extract` walks an authoritative .docx paragraph by paragraph and splits
each paragraph's text on placeholder spans, producing an ordered lock spec
(list of {"type": "fixed"|"placeholder", ...} tokens, one list per
paragraph). `check` walks a candidate document (.docx or .txt) and verifies,
in order:
  1. every FIXED segment from the lock spec appears verbatim (only leading/
     trailing/internal-whitespace-run differences are tolerated) at or after
     the previous match position -- so wording cannot be paraphrased,
     reordered, or silently dropped;
  2. no unresolved placeholder-looking dot-run survives in the candidate at
     a position where the lock spec expects one to have been filled in.

A PASS from this tool means "the agency's fixed wording survived intact and
every blank looks filled in." It does NOT mean the filled-in content
(names, amounts, dates) is itself correct -- that is the drafter's
responsibility. See gov-templates/NIA/README.md.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# Matches a Thai/ASCII dot-leader placeholder run, optionally wrapping an
# inline (label). Handles both ".....(label)....." and bare "..........".
PLACEHOLDER_RE = re.compile(
    r"[.…]{2,}(?:\s*\([^)]{1,120}\)\s*[.…]{0,})?"
)

WS_RE = re.compile(r"\s+")

# Whole-paragraph authoring-instruction markers, e.g. "-หัวบริษัท-" ("[insert
# company letterhead here]") or "(ตัวอย่าง ร่างจดหมาย)" ("(example draft
# letter)"). These are instructions to whoever fills in the template, not
# institutional wording -- they must NOT be required verbatim in a final
# candidate, and are excluded from the fixed-text lock entirely. Found by
# testing this exact tool against a synthetic "correctly filled in" letter,
# which the first version of this tool wrongly failed on (see
# gov-templates/NIA/README.md "Known limitation").
META_MARKER_RES = [
    re.compile(r"^-.{1,60}-$"),  # "-หัวบริษัท-", "-หัวบริษัท (ถ้ามี)-"
    re.compile(r"^\(ตัวอย่าง[^)]{0,60}\)$"),  # "(ตัวอย่าง ร่างจดหมาย)", "(ตัวอย่าง)"
]


def is_meta_marker(paragraph_text: str) -> bool:
    s = paragraph_text.strip()
    return any(r.match(s) for r in META_MARKER_RES)


def _normalize(text: str) -> str:
    """Collapse whitespace runs for tolerant-but-exact comparison. This is
    the ONLY normalization applied -- wording itself is never altered,
    reordered, or fuzzy-matched."""
    return WS_RE.sub(" ", text).strip()


def tokenize_paragraph(text: str) -> list[dict]:
    """Split one paragraph's text into an ordered list of fixed/placeholder
    tokens."""
    tokens: list[dict] = []
    pos = 0
    for m in PLACEHOLDER_RE.finditer(text):
        if m.start() > pos:
            fixed = text[pos : m.start()]
            if fixed.strip():
                tokens.append({"type": "fixed", "text": fixed})
        raw = m.group(0)
        label_m = re.search(r"\(([^)]{1,120})\)", raw)
        tokens.append(
            {
                "type": "placeholder",
                "raw": raw,
                "label": label_m.group(1).strip() if label_m else None,
            }
        )
        pos = m.end()
    if pos < len(text):
        fixed = text[pos:]
        if fixed.strip():
            tokens.append({"type": "fixed", "text": fixed})
    return tokens


def extract_lock(docx_path: pathlib.Path) -> dict:
    import docx

    doc = docx.Document(str(docx_path))
    paragraphs = []
    placeholder_counter = 0
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        if is_meta_marker(p.text):
            paragraphs.append([{"type": "meta", "text": p.text.strip()}])
            continue
        toks = tokenize_paragraph(p.text)
        if toks:
            # Mark paragraph-boundary fixed tokens so check_conformance can
            # require a clean (whitespace/string-boundary) edge for them --
            # see check_conformance's docstring for why this matters
            # specifically for Thai text.
            if toks[0]["type"] == "fixed":
                toks[0]["boundary_left"] = True
            if toks[-1]["type"] == "fixed":
                toks[-1]["boundary_right"] = True
            # Every placeholder gets a stable, unique "id" -- NOT only the
            # ones with an inline (label). A real NIA letter has many
            # unlabeled placeholders (a bare date blank, a signature line,
            # ...) that a "label"-only addressing scheme could never let a
            # caller fill in at all (found by adversarial review 2026-09-19:
            # google_docs_batch.py's from-lock command unconditionally
            # refused every real NIA lock, with no value a caller could
            # supply to satisfy an unlabeled placeholder). Assigning every
            # placeholder an id here, in extraction order, gives every
            # blank -- labeled or not -- an addressable key.
            for tok in toks:
                if tok["type"] == "placeholder":
                    tok["id"] = f"ph{placeholder_counter}"
                    placeholder_counter += 1
            paragraphs.append(toks)
    return {
        "source_file": docx_path.name,
        "paragraphs": paragraphs,
    }


def _candidate_text(path: pathlib.Path) -> str:
    if path.suffix == ".docx":
        import docx

        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    return path.read_text(encoding="utf-8")


def _needle_pattern(text: str) -> "re.Pattern | None":
    """Compile a fixed-text segment into a regex that matches it verbatim on
    the RAW candidate, tolerating only whitespace-run differences (a real
    newline vs. a real space, etc.) -- never a fuzzy/substring match. Every
    other character is matched literally (re.escape'd)."""
    norm = _normalize(text)
    if not norm:
        return None
    parts = norm.split(" ")
    pattern = r"\s+".join(re.escape(p) for p in parts)
    return re.compile(pattern)


def check_conformance(lock: dict, candidate_path: pathlib.Path) -> tuple[bool, list[str]]:
    """Returns (ok, findings). ok is True only if every fixed segment is
    found in order AND no unresolved placeholder dot-run remains.

    FIXED 2026-09-19 #1 (adversarial review finding, reproduced and
    confirmed before this fix): the previous version normalized the whole
    remaining candidate to a separate string, found the needle there, then
    tried to re-locate an approximate RAW offset by re-searching only for
    the needle's first word. If that first word recurred earlier in the
    candidate as an unrelated decoy, the cursor could be set to a position
    BEFORE the true match, letting a later fixed-text check silently pass
    against stray/coincidental text instead of the real (possibly deleted
    or reworded) content that should have followed. This version searches
    directly on the RAW candidate with a single regex per fixed segment
    (verbatim except whitespace-run tolerance) and advances the cursor to
    the real match's own end position -- there is no separate "find the
    raw offset afterward" step to be fooled by a decoy, because the match
    position used for the PASS/FAIL decision and the cursor advance are the
    exact same regex match object.

    FIXED 2026-09-19 #2 (second adversarial review, reproduced and
    confirmed): a plain substring match has no word-boundary concept, and
    Thai script has no spaces between words -- so a fixed segment could be
    "satisfied" by being a substring of a DIFFERENT, meaning-changed word
    with something glued directly onto it. Confirmed exploit: fixed segment
    "อนุมัติโครงการ" (approve the project) was satisfied by candidate text
    "ไม่อนุมัติโครงการ" (**not** approve the project) -- a real negation
    flip, not a cosmetic issue, on a tool whose whole purpose is a 100%
    conformance gate for real government correspondence. This version
    requires a CLEAN boundary (start-of-candidate or a whitespace
    character) immediately before a paragraph-INITIAL fixed token's match,
    and immediately after a paragraph-FINAL fixed token's match (see
    extract_lock's boundary_left/boundary_right marking) -- these are
    exactly the positions where a real conformant candidate must not have
    anything glued on, since the template's own paragraph starts/ends
    directly with that fixed wording. KNOWN REMAINING LIMITATION, disclosed
    rather than silently claimed solved: a fixed token in the MIDDLE of a
    paragraph, immediately adjacent to a placeholder on one or both sides
    (e.g. a closing quote right after a filled-in project name), is NOT
    boundary-checked, because the template legitimately has no separator
    there by design -- word-gluing on an interior placeholder/fixed
    boundary is not caught by this version. Closing that gap would need
    dictionary-aware Thai tokenization of the candidate to distinguish
    "expected adjacency" from "an inserted extra word," which is future
    work, not done here."""
    candidate = _candidate_text(candidate_path)
    findings: list[str] = []
    cursor = 0

    def _is_clean_boundary(char: "str | None") -> bool:
        return char is None or char.isspace()

    for p_idx, paragraph in enumerate(lock["paragraphs"]):
        for tok in paragraph:
            if tok["type"] != "fixed":
                continue
            pattern = _needle_pattern(tok["text"])
            if pattern is None:
                continue
            m = pattern.search(candidate, cursor)
            if m is None:
                findings.append(
                    f"paragraph {p_idx}: MISSING, REWORDED, or OUT OF ORDER fixed text: {_normalize(tok['text'])!r}"
                )
                continue
            if tok.get("boundary_left") and not _is_clean_boundary(
                candidate[m.start() - 1] if m.start() > 0 else None
            ):
                findings.append(
                    f"paragraph {p_idx}: BOUNDARY VIOLATION -- extra content directly glued "
                    f"before the paragraph-opening fixed text (no whitespace separator): "
                    f"{_normalize(tok['text'])!r}, context={candidate[max(0, m.start()-15):m.start()+15]!r}"
                )
            if tok.get("boundary_right") and not _is_clean_boundary(
                candidate[m.end()] if m.end() < len(candidate) else None
            ):
                findings.append(
                    f"paragraph {p_idx}: BOUNDARY VIOLATION -- extra content directly glued "
                    f"after the paragraph-closing fixed text (no whitespace separator): "
                    f"{_normalize(tok['text'])!r}, context={candidate[m.end()-15:m.end()+15]!r}"
                )
            cursor = m.end()

    # Unresolved-placeholder check: any leftover dot-leader run anywhere in
    # the candidate after the point where the source had a placeholder is a
    # hard failure -- it means a blank was never filled in.
    leftover = list(PLACEHOLDER_RE.finditer(candidate))
    if leftover:
        for m in leftover[:20]:
            findings.append(
                f"UNRESOLVED PLACEHOLDER still present in candidate at char {m.start()}: {m.group(0)!r}"
            )
        if len(leftover) > 20:
            findings.append(f"... and {len(leftover) - 20} more unresolved placeholders")

    return (len(findings) == 0), findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("extract", help="build a lock spec from an authoritative .docx")
    ex.add_argument("docx", type=pathlib.Path)
    ex.add_argument("-o", "--out", type=pathlib.Path, required=True)

    ck = sub.add_parser("check", help="check a candidate draft against a lock spec")
    ck.add_argument("lock", type=pathlib.Path)
    ck.add_argument("candidate", type=pathlib.Path)

    args = ap.parse_args()

    if args.cmd == "extract":
        lock = extract_lock(args.docx)
        args.out.write_text(json.dumps(lock, ensure_ascii=False, indent=2), encoding="utf-8")
        n_fixed = sum(1 for p in lock["paragraphs"] for t in p if t["type"] == "fixed")
        n_ph = sum(1 for p in lock["paragraphs"] for t in p if t["type"] == "placeholder")
        print(f"wrote {args.out}: {len(lock['paragraphs'])} paragraphs, {n_fixed} fixed segments, {n_ph} placeholders")
        return 0

    if args.cmd == "check":
        lock = json.loads(args.lock.read_text(encoding="utf-8"))
        ok, findings = check_conformance(lock, args.candidate)
        if ok:
            print(f"TEMPLATE LOCK PASS: {args.candidate} conforms to {lock['source_file']}")
            return 0
        print(f"TEMPLATE LOCK FAIL: {args.candidate} does not conform to {lock['source_file']}")
        for f in findings:
            print(" -", f)
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
