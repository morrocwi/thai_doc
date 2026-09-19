---
name: thai_doc
description: Load before generating, fixing, or reviewing any Thai-language document meant for an external tool (Google Docs, Word/DOCX, a browser, a PDF, Typst, LaTeX/arXiv). Covers the "ตัดบรรทัดไม่ได้"/justified-Thai-spacing problem and template-accurate document generation. Trigger on "พิมพ์ภาษาไทย", "ตัดบรรทัดภาษาไทย", "จัดหน้าเอกสารภาษาไทย", "สร้างเอกสารภาษาไทยตามเทมเพลท", "paste Thai text into Google Docs/Word", Thai formal letters/reports/academic papers, or any Thai justified-text layout problem.
---

# thai_doc

Public repo: https://github.com/morrocwi/thai_doc (MIT license, code only).

## READ FIRST — `KNOWN_ISSUES.md`

Before doing anything else, read `<repo>/KNOWN_ISSUES.md` in full. It
records real bugs and a real architectural mistake already found in this
repo's own history (a v1 approach that inserted zero-width spaces
everywhere, which is a documented and mechanically-provable-wrong pattern),
so the same mistake is not repeated. This applies to every AI vendor
session, not just the one that wrote it.

## Primary system: `docs/thai-worldclass/`

The actual Thai composition discipline lives in
`<repo>/docs/thai-worldclass/SKILL.md` (a merged external pack, "Thai
World-Class Publication System" v2.1.0) — **read that file next, it is the
primary authority for HOW to compose/fix Thai text**, not this file. It
gives:

- 17 documented, named AI failure modes for Thai composition (read them —
  they are specific and empirically demonstrated, not generic advice);
- the mandatory pipeline: Meaning → Thought Unit → Breath Weight → Rhythm
  Variation → Line Fit → Renderer Adaptation → Preflight → Render Feedback
  → Release Gate;
- per-route protocols (`docs/thai-worldclass/protocols/`) for Google Docs,
  DOCX/PDF, Typst, LaTeX/arXiv, one-column vs two-column house styles, and
  a release checklist;
- mechanical (non-semantic) lint/preflight scripts that catch known-unsafe
  patterns (control characters used as spacing patches, stretchable spaces
  in Thai-dominant justified paragraphs, orphaned dependent connectors).

## Government-agency templates: `gov-templates/<AGENCY>/`

**MANDATORY, fail-closed — this is the only thing that actually prevents
the bug class this section exists to stop.** Before drafting ANY official
letter/document to a Thai government agency, check whether
`gov-templates/<AGENCY_CODE>/` exists in this repo (see
`gov-templates/README.md` for the index of agencies covered). If it does:

1. The `source/` files in that folder are the *only* authoritative
   starting point. Do not invent a generic layout, do not paraphrase the
   agency's fixed wording "in the spirit of" the original, and do not
   substitute `docs/thai-worldclass/`'s general Typst/DOCX formal-letter
   guidance for an agency-supplied template when one exists — the general
   guidance still governs things the template leaves open (e.g. how to
   compose the prose that fills a blank), but the template's own fixed
   structure always wins where the two would conflict.
2. If a `.lock.json` exists for the letter type under `locks/`, running
   `python3 scripts/gov_template_lock.py check <lock> <your_draft>` is
   **mandatory before the draft is considered done** — not optional, not
   a nice-to-have. A non-PASS result is a hard block: do not send, submit,
   or hand off the draft. This is the actual enforcement mechanism (a
   mechanical, adversarially-tested gate — see `gov-templates/NIA/README.md`
   for the reproduced PASS/FAIL test cases AND the one known, disclosed gap
   in what it catches — read that section before treating a PASS as an
   unconditional guarantee), not merely a written instruction an AI might
   skip under time pressure. A PASS is still real evidence and still
   mandatory to obtain; it is just not the ONLY check a real letter needs
   (a human reads the final letter too, same as always).
3. Read the agency's own `README.md` in its folder (e.g.
   `gov-templates/NIA/README.md`) for anything agency-specific (whole-line
   authoring-instruction markers that must be replaced rather than kept
   literally, known-not-yet-locked file types, etc.) before drafting.

## This repo's own tooling (`scripts/`)

- `scripts/generate_doc.py` — Jinja2 template + yaml/json data →
  `.txt`/`.html`/`.docx`. It does **not** auto-patch Thai spacing (see
  `KNOWN_ISSUES.md` ISSUE 1 for why that was removed). Run with `--lint` to
  get a mechanical report from `docs/thai-worldclass/scripts/thai_semantic_lint.py`
  against the rendered text; add `--strict` to fail the run on hard
  findings. A lint PASS is necessary but not sufficient — the semantic
  thought-unit/breath-level work in `docs/thai-worldclass/protocols/01-thai-semantic-breathing.md`
  still has to actually happen for the source prose, this script cannot do
  it for you.
- `scripts/thai_linebreak.py` — demoted, diagnostic-only pythainlp word
  segmentation. Do not use its output directly in a user-facing document;
  read its module docstring and `KNOWN_ISSUES.md` ISSUE 1 before touching
  it.
- `scripts/google_docs_batch.py` — generates Google Docs API
  `documents.batchUpdate` requests from already-composed text (a general
  document, or a `gov-templates/*/locks/*.lock.json` detailed
  sub-template). Bring-your-own-credentials, dry-run by default, no
  network call without explicit credentials. See
  `scripts/README_google_docs_batch.md`. Like `generate_doc.py`, it does
  not decide Thai composition/spacing for you — feed it text that already
  went through the semantic pipeline in `docs/thai-worldclass/`.
- For an actually-live Google Docs connection (not just dry-run request
  JSON), see `docs/google-docs-mcp-integration.md` — a vetted, external,
  NOT-vendored MCP server recommendation
  (github.com/a-bonus/google-docs-mcp), bring-your-own-credentials, with
  this repo's own vetting notes (license, maintenance, red-flag scan,
  scope-limiting advice for installers who only want the Docs surface).

## How to use this skill end to end

1. Read `KNOWN_ISSUES.md`.
2. Read `docs/thai-worldclass/SKILL.md` and the specific protocol file for
   your output route (`docs/thai-worldclass/protocols/00-routing.md` tells
   you which one).
3. Compose/revise the Thai source following that protocol's semantic
   pipeline — this is judgment work an AI does while writing, not something
   a script does after the fact.
4. If generating from a template/data pair, use `scripts/generate_doc.py
   --lint` to get a mechanical sanity check on the rendered text.
5. Follow the release checklist: `docs/thai-worldclass/protocols/08-release-checklist.md`.
6. Never claim "verified", "publication-ready", or "fixed" unless the
   applicable gates in step 5 actually passed — this repo's own fail-closed
   principle (inherited from the merged pack) applies to claims about this
   repo's own output too.
