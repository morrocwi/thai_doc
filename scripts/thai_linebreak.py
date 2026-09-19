"""
thai_linebreak.py -- pythainlp word-tokenization helper. DEMOTED, read
KNOWN_ISSUES.md ("ISSUE 1") before using this for anything user-facing.

THIS IS NOT THE PRIMARY LINE-BREAK FIX FOR THIS REPO ANYMORE.
---------------------------------------------------------------
v1 of this repo used this module to insert a ZERO WIDTH SPACE (U+200B)
between *every* adjacent pair of dictionary-tokenized Thai words and shipped
that as "the fix" for Thai line-wrapping. That was wrong, and the mistake is
recorded in detail in ../KNOWN_ISSUES.md ("ISSUE 1"): it conflates word
segmentation with breath/rhythm segmentation (so it can split a genuine
semantic whole, e.g. splitting "ความไว้วางใจ" mid-concept), it does not fix
the failure mode that actually dominates in practice (Google Docs JUSTIFIED
Thai stretching ordinary spaces into ugly gaps -- ZWSP never touches those),
and running `docs/thai-worldclass/scripts/thai_semantic_lint.py` against its
own output reproduces a 100% failure rate (every inserted ZWSP flagged).

**For an actual fix, use the merged `docs/thai-worldclass/` protocol
pipeline** (`SKILL.md` there is the entry point): it classifies real
breath-level boundaries before choosing any renderer separator, and for
Google Docs JUSTIFIED Thai it forbids exactly the blanket-ZWSP pattern this
module used to produce as the direct output.

**What this module is still useful for**: producing a first-pass pythainlp
word segmentation as *diagnostic input* to a human or AI that is building
the thought-unit/breath-level model by hand -- i.e. "where would a
dictionary tokenizer split this" is one useful signal among several, never
the final answer. `fix_thai_linebreaks()` below is kept, tested, and
functionally unchanged from v1 (it is not broken code -- the mistake was
treating its output as a finished document rather than diagnostic input);
do not call it and paste the result directly into a user-facing document.

This module depends on pythainlp's dictionary-based tokenizer (engine
"newmm").
"""
from __future__ import annotations

import re
import unicodedata

try:
    from pythainlp.tokenize import word_tokenize
except ImportError as exc:  # pragma: no cover - surfaced to the caller
    raise ImportError(
        "thai_linebreak requires pythainlp (pip install pythainlp). "
        "This dependency is not vendored/bundled by this repo."
    ) from exc

ZWSP = "​"

# A run is "Thai" if it contains at least one Thai-block codepoint.
_THAI_RANGE = re.compile(r"[฀-๿]")


def _is_thai_word(token: str) -> bool:
    return bool(_THAI_RANGE.search(token))


def fix_thai_linebreaks(text: str, engine: str = "newmm") -> str:
    """Return *text* with U+200B inserted between adjacent Thai word tokens
    so external layout engines gain a legal break point inside long Thai
    runs. Existing whitespace/newlines/punctuation are never altered or
    removed; this function only ever *inserts* ZWSP characters.

    Idempotent: running this twice does not insert a second ZWSP at the same
    boundary (existing ZWSP is treated as an already-fixed boundary).
    """
    if not text:
        return text

    # Normalize first so combining marks (tone marks, vowels) stay attached
    # to their base consonant when pythainlp tokenizes -- NFC is the correct
    # normal form for Thai text interchange.
    text = unicodedata.normalize("NFC", text)

    out_parts: list[str] = []
    # Process line by line so we never insert a ZWSP where a real newline
    # already provides a break opportunity, and so tokenization runs on
    # one visual line at a time (matches how the text will actually wrap).
    for line_idx, line in enumerate(text.split("\n")):
        if line_idx > 0:
            out_parts.append("\n")
        out_parts.append(_fix_line(line, engine))
    return "".join(out_parts)


def _fix_line(line: str, engine: str) -> str:
    if not line.strip():
        return line

    tokens = word_tokenize(line, engine=engine, keep_whitespace=True)
    pieces: list[str] = []
    prev_was_thai_word = False
    for tok in tokens:
        if tok == "":
            continue
        is_thai = _is_thai_word(tok) and tok.strip() != ""
        is_whitespace = tok.strip() == ""
        if (
            pieces
            and prev_was_thai_word
            and is_thai
            and not is_whitespace
            and not pieces[-1].endswith(ZWSP)
        ):
            pieces.append(ZWSP)
        pieces.append(tok)
        prev_was_thai_word = is_thai and not is_whitespace
    return "".join(pieces)


def strip_zwsp(text: str) -> str:
    """Inverse operation -- remove every ZWSP this tool (or anything else)
    inserted. Useful for diffing/testing round-trip fidelity: strip_zwsp
    must reproduce the exact original text, since fix_thai_linebreaks only
    ever inserts characters, never deletes or reorders any."""
    return text.replace(ZWSP, "")


if __name__ == "__main__":
    import sys

    src = sys.stdin.read() if not sys.stdin.isatty() else " ".join(sys.argv[1:])
    sys.stdout.write(fix_thai_linebreaks(src))
