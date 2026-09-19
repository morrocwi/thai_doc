"""
google_docs_batch.py -- generate Google Docs API `documents.batchUpdate`
requests from either (a) a general document (a sections dict, the same
shape scripts/generate_doc.py's parse_sections() produces) or (b) a
"detailed sub-template" (a gov-templates/*/locks/*.lock.json spec plus a
dict of placeholder values to fill in).

Why this exists and what it does NOT do
----------------------------------------
This module is a DELIVERY MECHANISM, not a composition system. The actual
Thai-composition judgment (thought units, breath levels, which renderer
separator to use where) belongs to a human or an AI following
docs/thai-worldclass/protocols/01-thai-semantic-breathing.md and
protocols/03-google-docs.md BEFORE calling anything here -- this module
takes already-composed text and turns it into correct, index-safe
batchUpdate requests. It does not decide Thai line-break/justification
separators for you (consistent with scripts/generate_doc.py, which also
stopped doing that -- see ../KNOWN_ISSUES.md ISSUE 1).

The one thing this module DOES decide structurally: paragraph-start
(first-line indent), via paragraphStyle.indentFirstLine, using the same
BODY_FIRST_LINE_INDENT_CM value scripts/generate_doc.py uses for docx/html
-- one convention, every output format (see generate_doc.py's module-level
comment for the full reconciliation history, 2026-09-19).

Index safety (the hard part)
-----------------------------
Google Docs API indices are UTF-16 CODE-UNIT offsets, not Python character
counts. docs/thai-worldclass/protocols/03-google-docs.md already states the
rule in prose: "Never compute Thai edit/style ranges from guessed Unicode
character counts. Use provider-returned ranges, live indexes, exact
structure, or verified text ranges." This module follows that rule
mechanically: every index computation goes through utf16_len() below,
never Python's plain len(). For all text this repo actually handles (Thai,
Latin, digits, common punctuation -- everything in the Thai Unicode block
plus ASCII/Latin-1 supplement), every codepoint is a single UTF-16 code
unit (all are within the Basic Multilingual Plane), so utf16_len() and
Python len() happen to agree for THIS repo's content today -- but the
computation is still done the provably-correct way, not the "happens to
agree" way, because that assumption breaks silently the moment anyone
pastes in an emoji, a rare CJK extension character, or anything else
outside the BMP. See test_google_docs_batch.py for the combining-mark
proof.

Bring-your-own-credentials
----------------------------
This module ships NO credentials, NO client ID/secret, and makes NO
network call in --dry-run mode (the only mode usable without any Google
account setup at all). A live-apply path exists (`apply_live`) but only
imports google-api-python-client lazily, inside that function, so the
dry-run path has zero new hard dependencies. Credentials for the live path
are read from a path given by the GOOGLE_DOCS_CREDENTIALS_PATH environment
variable -- never hardcoded, never committed, always supplied by whoever
installs this (see ../SKILL.md and ../README.md for the installer-brings-
their-own-credentials model this whole repo follows).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_template_lock import check_conformance, tokenize_paragraph  # noqa: E402

BODY_FIRST_LINE_INDENT_CM = 2.5  # kept in sync with generate_doc.py by convention; see that
                                  # file's module-level comment for the reconciliation history.
NON_BODY_SECTIONS = {"_preamble", "TITLE"}

BODY_START_INDEX = 1  # a new Google Doc's body always starts at index 1


def utf16_len(s: str) -> int:
    """The number of UTF-16 code units `s` occupies -- what the Google Docs
    API actually counts as one index step. NEVER use Python's plain len()
    for a Google Docs index computation; use this. Encoding to UTF-16LE and
    dividing the byte count by 2 is the standard, dependency-free way to
    get this count correctly for any string, including characters outside
    the Basic Multilingual Plane (which encode as a surrogate pair -- 4
    bytes / 2 code units -- where Python's len() would still only count 1
    character)."""
    return len(s.encode("utf-16-le")) // 2


def _paragraph_style_request(start: int, end: int, indent: bool, alignment: str | None) -> dict:
    style: dict = {}
    fields = []
    if indent:
        style["indentFirstLine"] = {"magnitude": BODY_FIRST_LINE_INDENT_CM, "unit": "CENTIMETERS"}
        fields.append("indentFirstLine")
    if alignment:
        style["alignment"] = alignment
        fields.append("alignment")
    return {
        "updateParagraphStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "paragraphStyle": style,
            "fields": ",".join(fields) if fields else "*",
        }
    }


def build_requests_from_sections(
    sections: dict, alignment: str | None = "JUSTIFIED"
) -> list[dict]:
    """General-document path: same sections shape as
    generate_doc.py.parse_sections() (dict of section name -> text, with
    paragraphs inside a section separated by "\\n\\n"). Returns a list of
    Google Docs API Request objects ready for `documents.batchUpdate`,
    fully index-safe (see module docstring)."""
    requests: list[dict] = []
    index = BODY_START_INDEX

    for name, text in sections.items():
        if name == "_preamble" or not text.strip():
            continue
        is_body = name not in NON_BODY_SECTIONS
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for para in paragraphs:
            content = para + "\n"
            start = index
            requests.append(
                {"insertText": {"location": {"index": start}, "text": content}}
            )
            index += utf16_len(content)
            end = index  # end is exclusive; includes the trailing newline,
                          # which Google Docs requires for a paragraph-style
                          # range to actually apply to that paragraph.
            requests.append(
                _paragraph_style_request(
                    start, end, indent=is_body, alignment=alignment if is_body else None
                )
            )

    return requests


def build_requests_from_lock(
    lock: dict, values: dict, alignment: str | None = None
) -> tuple[list[dict], str]:
    """Detailed-sub-template path: given a gov-templates/*/locks/*.lock.json
    spec (produced by an extract_lock() that assigns every placeholder an
    "id", not only the ones with an inline (label) -- see
    gov_template_lock.extract_lock) and a dict of fill-in values, reconstruct
    the flattened final text (fixed wording verbatim, placeholders
    substituted) and emit index-safe batchUpdate requests for it. Returns
    (requests, flattened_text) -- the caller MUST run
    scripts/gov_template_lock.check_conformance-equivalent verification on
    flattened_text (this function does it internally, see below) before
    ever sending these requests to a live document.

    Value lookup order per placeholder: `values[label]` first if the
    placeholder has a label AND that label is a key in `values` (lets one
    supplied value fill every occurrence of a repeated label, e.g.
    "ชื่อโครงการ" appearing three times in one letter); otherwise
    `values[id]` (the stable per-placeholder key gov_template_lock assigns
    to EVERY placeholder, labeled or not -- this is the only way to
    address an unlabeled blank such as a bare date or signature line; run
    `gov_template_lock.py extract` and read the resulting .lock.json's
    "id"/"label"/"raw" fields to see what a given template needs). Fixed
    2026-09-19 (adversarial review): the previous version only ever looked
    up by label, so a lock with any unlabeled placeholder -- true of every
    NIA lock shipped in this repo -- could never be satisfied by any
    values dict at all.

    Fail-closed: raises ValueError, refusing to emit any request, if the
    reconstructed text does not conform to the lock spec (e.g. a
    placeholder has no supplied value under either lookup) -- this reuses
    gov_template_lock's own conformance logic rather than re-deriving a
    second notion of "conformant.\""""
    lines = []
    for paragraph in lock["paragraphs"]:
        parts = []
        for tok in paragraph:
            if tok["type"] == "meta":
                continue  # authoring instructions, never reproduced literally
            if tok["type"] == "fixed":
                parts.append(tok["text"])
            elif tok["type"] == "placeholder":
                label = tok.get("label")
                ph_id = tok.get("id")
                if label is not None and label in values:
                    value = values[label]
                elif ph_id is not None and ph_id in values:
                    value = values[ph_id]
                else:
                    raise ValueError(
                        f"no value supplied for placeholder {tok.get('raw')!r} "
                        f"(label={label!r}, id={ph_id!r}) -- supply a value under "
                        f"the label if present, otherwise under the id -- refusing "
                        f"to emit requests for an incompletely-filled locked template"
                    )
                parts.append(str(value))
        line = "".join(parts).strip()
        if line:
            lines.append(line)
    flattened = "\n\n".join(lines)

    # Fail-closed self-check: verify the very text we're about to turn into
    # live requests actually conforms to the lock, using the SAME checker
    # gov-templates/*/README.md tells a human/AI to run manually. This
    # catches a bug in the substitution above, not just bugs in the
    # caller's input. If this raises because a SUPPLIED value itself
    # happens to look like an unresolved placeholder (a dot-leader run) or
    # reintroduces a boundary violation, the findings below will say so
    # explicitly (e.g. "UNRESOLVED PLACEHOLDER") -- that message describes
    # the flattened OUTPUT, not a bug in this substitution step; if you see
    # it, check whether one of your own supplied values contains "..." or
    # similar before assuming the code is broken.
    tmp_fd, tmp_name = tempfile.mkstemp(suffix=".txt", prefix="google_docs_batch_selfcheck_")
    os.close(tmp_fd)
    tmp = pathlib.Path(tmp_name)
    tmp.write_text(flattened, encoding="utf-8")
    try:
        ok, findings = check_conformance(lock, tmp)
    finally:
        tmp.unlink(missing_ok=True)
    if not ok:
        raise ValueError(
            "reconstructed text does NOT conform to the lock spec -- refusing to "
            "emit batchUpdate requests. Findings:\n" + "\n".join(findings)
        )

    sections = {"BODY": flattened}
    requests = build_requests_from_sections(sections, alignment=alignment)
    return requests, flattened


def apply_live(document_id: str, requests: list[dict], credentials_path: str | None = None) -> dict:
    """Send `requests` to a real Google Doc via the live API. Lazily
    imports google-api-python-client / google-auth so the dry-run path
    above has zero hard dependency on them. Credentials are read from
    `credentials_path` or the GOOGLE_DOCS_CREDENTIALS_PATH environment
    variable -- this repo ships none, bundles none, and never will; bring
    your own (see module docstring)."""
    cred_path = credentials_path or os.environ.get("GOOGLE_DOCS_CREDENTIALS_PATH")
    if not cred_path:
        raise RuntimeError(
            "no Google credentials configured -- set GOOGLE_DOCS_CREDENTIALS_PATH "
            "to your own service-account/OAuth credentials file. This repo does not "
            "ship or manage credentials for you."
        )
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise ImportError(
            "live-apply requires google-api-python-client and google-auth "
            "(pip install google-api-python-client google-auth) -- these are "
            "intentionally NOT in requirements.txt since the dry-run path doesn't "
            "need them"
        ) from exc

    creds = service_account.Credentials.from_service_account_file(
        cred_path, scopes=["https://www.googleapis.com/auth/documents"]
    )
    service = build("docs", "v1", credentials=creds)
    return service.documents().batchUpdate(
        documentId=document_id, body={"requests": requests}
    ).execute()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("from-sections", help="general document from a generate_doc.py-shaped sections JSON")
    gen.add_argument("sections_json", type=pathlib.Path, help='JSON file: {"TITLE": "...", "BODY": "..."}')
    gen.add_argument("-o", "--out", type=pathlib.Path, required=True, help="output path for the batchUpdate request JSON")
    gen.add_argument("--alignment", default="JUSTIFIED", choices=["JUSTIFIED", "START", "END", "CENTER"])

    lck = sub.add_parser("from-lock", help="detailed sub-template from a gov-templates/*/locks/*.lock.json")
    lck.add_argument("lock_json", type=pathlib.Path)
    lck.add_argument("values_json", type=pathlib.Path, help="JSON: {\"placeholder label\": \"value\", ...}")
    lck.add_argument("-o", "--out", type=pathlib.Path, required=True)

    args = ap.parse_args()

    if args.cmd == "from-sections":
        sections = json.loads(args.sections_json.read_text(encoding="utf-8"))
        requests = build_requests_from_sections(sections, alignment=args.alignment)
        args.out.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out}: {len(requests)} requests (dry-run, no network call)")
        return 0

    if args.cmd == "from-lock":
        lock = json.loads(args.lock_json.read_text(encoding="utf-8"))
        values = json.loads(args.values_json.read_text(encoding="utf-8"))
        try:
            requests, flattened = build_requests_from_lock(lock, values)
        except ValueError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        args.out.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out}: {len(requests)} requests (dry-run, no network call)")
        print(f"conformance self-check: PASS ({len(flattened)} chars flattened text)")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
