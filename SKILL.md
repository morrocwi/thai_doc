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
