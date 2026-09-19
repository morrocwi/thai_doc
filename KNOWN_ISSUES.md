# KNOWN ISSUES — READ THIS BEFORE TOUCHING thai_doc

This file exists so every AI session (Claude, Codex, Gemini, or any other
vendor) that works on `thai_doc` next reads the same catalog of *already
found* bugs and design mistakes before doing anything else, and does not
repeat them. If you are an AI about to edit this repo: read this file in
full first. If a change you are about to make matches a pattern below,
stop and re-read the referenced section.

Founder instruction that produced this file (2026-09-19, verbatim intent):
"ตีปัญหาให้แตกฉานก่อนและทำให้เอไอทุกตัวรู้ว่ามันมีบั๊กและมีปัญหาอะไร เพื่อไม่ให้ผิดซ้ำ"
— diagnose the problem thoroughly first, and make every AI aware of the
bugs/issues that exist, so the same mistake is never repeated.

---

## ISSUE 1 (architectural, CRITICAL) — v1's "insert ZWSP at every word boundary" approach is a known-wrong pattern, empirically proven

**Status: superseded. Do not use `scripts/thai_linebreak.py`'s ZWSP-everywhere
strategy as the primary/default line-break fix going forward.**

### What v1 did (commit `674b632`)

`scripts/thai_linebreak.py` dictionary-tokenized Thai text (pythainlp
`newmm`) and inserted a ZERO WIDTH SPACE (U+200B) between *every* pair of
adjacent Thai word tokens, uniformly, with no distinction between:
- a semantic whole that must never be split (e.g. `ความไว้วางใจ` = "trust",
  one indivisible concept made of two dictionary words), and
- a real breath/clause boundary where a break is actually appropriate.

### Why this is wrong (not a style opinion — reproduced empirically)

A separately-obtained reference system, `thai-worldclass-publication-system`
v2.1.0 (merged into this repo — see `README.md` "Provenance" section),
explicitly documents this exact pattern as one of ~17 *known recurring AI
failure modes* when generating Thai text (see
`docs/thai-worldclass/SKILL.md` failure modes #2 "spacing-first failure",
#3 "mixed-separator failure", #4 "Unicode-patch failure"), and its own
protocols state outright:

> "U+2060 WORD JOINER, U+200B ZERO WIDTH SPACE, or NBSP MUST NOT be used as
> a general orphan-repair technique." (`docs/thai-worldclass/protocols/01-thai-semantic-breathing.md` §10)

This is not merely a documented objection — it is mechanically enforced.
Running that system's own lint tool against v1's actual output reproduces
the failure:

```bash
python3 docs/thai-worldclass/scripts/thai_semantic_lint.py <v1-output.txt> --mode google-docs-justified
```

Result on v1's example output (`examples/formal_letter.example.yaml`
rendered through `generate_doc.py -f txt`): **every single inserted ZWSP
was flagged as a hard failure** — dozens of findings, 100% of insertions,
zero false negatives tolerated. Example finding:

```
ZERO WIDTH SPACE U+200B found at 9:5; recomposition must precede
no-break/control-character repair; context='ียน​ตัวอย่าง​วิทยา↵↵ด้วย​หน่วยงาน​ของ​เรา​มี​กำห'
```

### Root cause

1. **No thought-unit/breath-level model.** v1 tokenizes at the *word*
   level and treats every word-word boundary as an equal, context-free
   break opportunity. It never asks "is this a semantic whole that must
   stay continuous" (breath Level 0) vs. "is this a real clause/argument
   boundary" (Level 2-4). Word segmentation and breath/rhythm segmentation
   are different problems; v1 conflated them.
2. **ZWSP does not solve the failure mode that actually matters most in
   practice.** ZWSP only helps the case of "the layout engine has *zero*
   break opportunities in a long Thai run and the text overflows its box
   unbroken." It does **not** address the far more common, more visibly
   broken failure: Google Docs **justified** Thai stretching ordinary
   U+0020 spaces into ugly, uneven gaps across a line (a problem this
   affects even *pure-Latin phrases embedded inside* Thai-dominant
   justified paragraphs — see `docs/thai-worldclass/protocols/03-google-docs.md`
   "Latin-run exemption failure"). v1 never touched ordinary spaces at
   all, so it left the dominant real-world complaint completely unfixed
   while introducing a new problem (indiscriminate splitting of semantic
   wholes).
3. **No lookahead/orphan handling.** v1 has no concept of a dependent
   connector (`หาก`, `โดย`, `ซึ่ง`, `เพื่อ`, ...) being stranded at a line
   end and needing recomposition rather than a character patch.

### What to do instead

Use the merged `docs/thai-worldclass/` protocol pipeline (`Meaning →
Thought Unit → Breath Weight → Rhythm Variation → Line Fit → Renderer
Adaptation → Preflight → Render Feedback → Release Gate`) documented in
`docs/thai-worldclass/SKILL.md`, which:
- for Google Docs JUSTIFIED Thai, uses U+2009 THIN SPACE only at
  classified Level 1-2 breath boundaries, never as a blanket word-boundary
  patch, and forbids ordinary U+0020 between visible tokens in a
  Thai-dominant justified paragraph (`protocols/03-google-docs.md`);
- for a deterministic final PDF, prefers the Typst route
  (`protocols/09-typst.md`), which uses Typst's own ICU4X-based automatic
  Thai line segmentation — no manual space/ZWSP insertion needed at all,
  because the compositor itself now understands Thai word boundaries.

`scripts/thai_linebreak.py` is **kept in the repo for one narrow, correctly-scoped case only**: producing a first-pass pythainlp word segmentation as *diagnostic input* to a human/AI building the thought-unit model — never as a direct-to-output line-break fix. See the updated module docstring.

---

## ISSUE 2 (real code bug, FIXED) — docx East-Asian/complex-script font slot was silently never set

**Status: fixed in commit `674b632` (same commit as v1's initial push,
caught by pre-publish adversarial review before it ever shipped to a
user). Recorded here so the *pattern* is not reintroduced elsewhere.**

`scripts/generate_doc.py::write_docx` set `style.font.name = font_name`,
then checked `if rfonts is None:` before setting the `w:eastAsia`/`w:cs`
XML attributes needed so Word doesn't silently fall back to a default
font for Thai glyphs. But `style.font.name = ...` *itself* creates a
`w:rFonts` element (with only `ascii`/`hAnsi` set) as a side effect of
python-docx's `Font.name` setter — so `rfonts is None` was false by the
time the check ran, and the `eastAsia`/`cs` attributes were never set, on
every single call, silently.

**Pattern to avoid elsewhere:** when touching python-docx `rFonts` (or
any OOXML element that a high-level property setter may have already
created as a side effect), do not gate attribute-setting on
`if element is None:` — find-or-create the element, then set every
attribute you need unconditionally. See the fixed code and comment in
`scripts/generate_doc.py::write_docx`.

---

## ISSUE 3 (minor, open) — `#...#` section-marker parsing false-positive

`scripts/generate_doc.py::parse_sections` treats any line that both
starts and ends with `#` as a new section marker. A body paragraph line
that happens to read like `#hashtag#` or a markdown `#### heading ####`
would be misparsed as a section boundary. Low risk (template format is
author-controlled) but not yet fixed — noted in `README.md` and here so
it isn't silently rediscovered as "new."

---

## ISSUE 4 (external, self-disclosed by the source pack, carried forward) — Typst route cannot be verified end-to-end in this environment

The merged `docs/thai-worldclass/` v2.1 Typst route was built and its own
`BUILD_REPORT.md` states the build environment had **no `typst` CLI**, so
its static preflight/lint passes, but a live Typst >=0.15.1 compile +
rendered-page visual inspection is **CANNOT VERIFY** until run somewhere
with the Typst CLI and Thai-capable fonts (Sarabun / TH Sarabun New /
Noto Sans Thai) installed. Verified again in this repo:
`which typst` → not found in this workstation either, as of 2026-09-19.
**Do not claim a Typst/PDF output from this repo is "verified" or
"publication-ready" until this gate is actually closed** (compile +
visual page inspection), per the source pack's own fail-closed rule
(`protocols/09-typst.md` "Fail-closed conditions").

No font files are bundled by design (license/size reasons) — any
Typst/DOCX/XeLaTeX render depends on the target environment having a
Thai-capable font available.

---

## Provenance / license note (carried forward, do not re-litigate)

The merged `docs/thai-worldclass/` content independently reimplements
structural ideas from `whs/typst-govdoc` (no SPDX license metadata on
that upstream repo; its README states `ไม่สงวนลิขสิทธิ์`) rather than
copying it verbatim, and uses `typst/typst` (Apache-2.0) concepts. See
`docs/thai-worldclass/RESEARCH_NOTES_TYPST_2.1.md` for the full
provenance trail. Do not bundle upstream template files (e.g. a Garuda
emblem asset) — this was a deliberate decision in the source pack,
carried forward here.
