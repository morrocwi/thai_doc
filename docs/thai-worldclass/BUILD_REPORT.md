# Build / Smoke-Test Report — v2.1.0 Typst Integration

Rebuilt 2026-09-19 after v2.0.3 closed the Google Docs mixed-script justification bugs. v2.1 adds a separate **Typst compositor + layout-oracle route** without weakening the existing fail-closed Thai semantic contract.

## External research incorporated

### whs/typst-govdoc

Inspected commit `b0ca4535c92f70aa94ace3f9bcffeae501df893b` (2023-03-26). Useful structural concepts were independently reimplemented:

- A4 formal geometry;
- Thai language/region and 16pt formal typography;
- metadata grids;
- Thai numeral conversion;
- unbreakable signature/sender blocks;
- first-line indentation as geometry rather than typed spaces.

The 2023 manual Thai wrapping workaround was explicitly rejected as stale. No Garuda asset or source file from the repository is bundled.

### typst/typst

Inspected stable `v0.15.1` and main snapshot `094b9634d2aa506757d342103411a33a347e3012` (2026-09-18). v2.1 uses verified current concepts:

- ICU4X LSTM-backed general line segmentation with upstream Thai regression tests;
- optimized Knuth-Plass-style line breaking;
- `par.justification-limits`;
- modern `par.first-line-indent`;
- deterministic compilation suitable for regression rendering.

## v2.1 route rules added

- Typst receives the **clean semantic source**, never Google Docs U+2009 renderer-adapted text.
- Typst may be the final PDF compositor when editable DOCX is not required.
- Typst may be a layout oracle for Google Docs diagnosis, but never the semantic authority.
- Justified Thai uses `lang: "th"`, `region: "TH"`, `linebreaks: "optimized"`, and conservative justification limits.
- Character tracking stays zero by default for Thai.
- Manual `#h(...)` body-indent hacks and literal-space tabs fail preflight.
- Private-company → government letters do not inject Garuda/government-origin identity.
- Typst final verification targets version >=0.15.1 and requires compile + rendered-page QA.

## New files

- `protocols/09-typst.md`
- `typst/thai-worldclass.typ`
- `typst/formal-letter.typ`
- `typst/examples/formal_private_to_government.typ`
- `typst/tests/good_clean_thai.typ`
- `typst/tests/bad_google_docs_leak.typ`
- `scripts/typst_preflight.py`
- `RESEARCH_NOTES_TYPST_2.1.md`

## Tests run in this build environment

- `python scripts/thai_semantic_lint.py --self-test` — PASS.
- `python scripts/typst_preflight.py --self-test` — PASS.
- clean Typst Thai static preflight — PASS.
- private-to-government Typst example static preflight — PASS.
- Google Docs U+2009 → Typst contamination negative test — correctly FAILS CLOSED.
- package validator — PASS after manifest rebuild.
- A_ONE_COLUMN source lint — PASS.
- C_TWO_COLUMN source lint — PASS.
- LaTeX regression positive suite — PASS.
- severe-equation negative regression — correctly FAILS CLOSED.
- severe-table negative regression — correctly FAILS CLOSED.

## Verification limitation

The build environment used for v2.1 did not provide a `typst` CLI executable. Therefore the package's Typst source and fail-closed static preflight are verified, but a live Typst 0.15.1+ compile is **CANNOT VERIFY in this environment**. `scripts/typst_preflight.py --compile` intentionally returns CANNOT VERIFY when the CLI is missing or too old. A final Typst PDF still requires compilation, text-layer checks where available, page rasterization, and visual inspection.

## Scope note

No compositor proves semantic quality. Typst improves layout control and diagnostics, but the mandatory semantic order remains:

**Meaning → Thought Unit → Breath Weight → Rhythm Variation → Line Fit → Renderer → QA**.
