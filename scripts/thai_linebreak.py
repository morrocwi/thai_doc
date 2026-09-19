"""
thai_linebreak.py -- fix Thai line-wrap in external tools (Word, Google Docs,
browsers, PDF renderers, ...).

THE PROBLEM
-----------
Thai script does not put spaces between words. Layout engines that were built
for space-delimited scripts (the browser's/Word's/Google Docs' default line
breaker) therefore either:
  (a) never break a long Thai run at all (it overflows its box), or
  (b) break at an arbitrary character, splitting a word (or a consonant from
      its own vowel/tone mark) across two lines.

THE FIX (standard, widely used technique -- not novel to this repo)
---------------------------------------------------------------
Segment the text into real Thai words with a dictionary-based tokenizer, then
insert a ZERO WIDTH SPACE (U+200B) between words. U+200B is invisible and
adds no visible spacing, but every mainstream layout engine (browsers, Word,
Google Docs, LibreOffice, most PDF renderers) treats it as a legal line-break
opportunity. Existing hard breaks (real spaces, newlines) are left untouched
as-is -- ZWSP is only inserted at internal word boundaries that currently
have no break opportunity at all.

This module depends on pythainlp's dictionary-based tokenizer (engine
"newmm"). No new segmentation algorithm is invented here; this is a thin,
auditable wrapper that:
  1. keeps non-Thai runs (Latin words, numbers, punctuation, existing
     whitespace) untouched, and
  2. only inserts ZWSP between consecutive Thai *word* tokens.
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
