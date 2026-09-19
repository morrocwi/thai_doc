# google_docs_batch.py

Generates Google Docs API `documents.batchUpdate` requests. Two modes,
both `--dry-run` by default (no network call, no credentials needed):

## General document

```bash
# sections.json: {"TITLE": "...", "BODY": "para one\n\npara two"} --
# the same shape scripts/generate_doc.py's parse_sections() produces.
python3 scripts/google_docs_batch.py from-sections sections.json -o requests.json
```

Body paragraphs get a structural `indentFirstLine` (2.5cm, matching
`generate_doc.py`'s docx/html output and `docs/thai-worldclass/`'s Typst/
LaTeX house style — one paragraph-start convention everywhere) and
`JUSTIFIED` alignment (override with `--alignment`); `TITLE` gets neither.

## Detailed sub-template (e.g. an NIA locked letter)

```bash
# Find out what a given lock needs first -- every placeholder has a stable
# "id" (ph0, ph1, ...), and ALSO a "label" when the source template had an
# inline (label) like "(ชื่อโครงการ)". Not all placeholders have a label --
# a bare date blank or a signature line usually doesn't.
python3 -c "
import json
lock = json.load(open('gov-templates/NIA/locks/2.1.lock.json', encoding='utf-8'))
for p in lock['paragraphs']:
    for t in p:
        if t['type'] == 'placeholder':
            print(t['id'], '|', t.get('label'), '|', t['raw'][:40])
"

# values.json: key by label when one exists (one value then fills every
# occurrence of that label in the letter), otherwise by id -- EVERY
# placeholder must have a key one way or the other, or the tool refuses.
python3 scripts/google_docs_batch.py from-lock \
  gov-templates/NIA/locks/2.1.lock.json values.json -o requests.json
```

Reconstructs the flattened final text (fixed wording verbatim, placeholders
substituted), runs `gov_template_lock.check_conformance` against it
internally, and **refuses to emit any request** (`ValueError`, non-zero
exit) if any placeholder — labeled or not — has no supplied value, or if
the result doesn't conform — the same fail-closed check
`gov-templates/<AGENCY>/README.md` requires manually, just also run
automatically here before anything reaches a live document. (Fixed
2026-09-19: an earlier version of this function only looked values up by
label, which meant it could never succeed against any real NIA lock at
all, since every one of them has at least one unlabeled placeholder — see
the module docstring on `build_requests_from_lock` for the fix.)

## Applying to a live Google Doc

Not exercised in this repo (no Google account/credentials available in the
environment this was built in) — the request-building and index math are
tested (`tests/test_google_docs_batch.py`), the actual live API call is
not. `apply_live(document_id, requests, credentials_path=...)` exists and
lazily imports `google-api-python-client`/`google-auth` (not in
`requirements.txt` — install them yourself: `pip install
google-api-python-client google-auth`). Credentials are **never** shipped
or read from anywhere but `GOOGLE_DOCS_CREDENTIALS_PATH` (env var) or an
explicit `credentials_path` argument — bring your own service-account
file, this repo manages none for you.

## Index safety

Every index is computed via `utf16_len()`, never Python's `len()` — Google
Docs API indices are UTF-16 code-unit offsets, and Python `len()` silently
undercounts anything outside the Basic Multilingual Plane (emoji, some
rare CJK). See `tests/test_google_docs_batch.py`'s surrogate-pair test for
the proof this actually matters, and `docs/thai-worldclass/protocols/03-google-docs.md`'s
"Index safety" rule for why this is a hard requirement, not a nicety.
