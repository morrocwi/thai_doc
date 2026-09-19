# Thai World-Class Publication System v2.1

Standalone fail-closed skill pack for Thai academic, formal, and publication production across **Google Docs, DOCX/PDF, Typst/PDF, and XeLaTeX/arXiv**.

## Read this first

The core rule is not “use prettier spaces”. The core rule is:

**Meaning → Thought Unit → Breath Weight → Rhythm Variation → Line Fit → Renderer → QA**

The skill explicitly guards against known AI failures such as spacing-first repair, mixed Unicode separators in justified Thai, orphan phrases repaired with joiners, alignment escape, mixed-script stretch, stale renderer workarounds, cross-render contamination, and claiming verification after layout-only QA.

See `SKILL.md` first. Its warning and hard execution contract are mandatory.

## What v2.1 adds

v2.1 adds a **Typst compositor + layout-oracle route** based on a current review of:

- `whs/typst-govdoc` for Thai formal-document structural ideas; and
- `typst/typst` v0.15.1/current source for modern Thai line breaking, optimized paragraph composition, and justification controls.

Important: the old 2023 Typst workaround that manually inserts spacing for Thai wrapping is explicitly rejected. Current Typst uses ICU4X line segmentation and has Thai line-break regression tests.

Use Typst when:

- the final artifact is a polished PDF and editable DOCX is not required;
- a formal Thai letter needs deterministic page geometry;
- Google Docs justification needs a comparison renderer to distinguish semantic defects from renderer defects;
- a regression renderer is useful during Thai composition development.

Typst never replaces semantic reasoning. The semantic source stays renderer-neutral.

## Included house profiles

- `A_ONE_COLUMN`
- `C_TWO_COLUMN`

Profiles excluded: B and D.

## Fonts

The pack does **not** bundle fonts. Typst, DOCX, and XeLaTeX routes must use fonts available in the target environment.

## Typst provenance and license note

`typst/typst` is Apache-2.0. `whs/typst-govdoc` has no GitHub SPDX/license metadata; its README states `ไม่สงวนลิขสิทธิ์`. v2.1 therefore **does not copy its template verbatim**. It independently reimplements general layout concepts such as grids, margins, Thai numeral conversion, and unbreakable signature blocks. See `RESEARCH_NOTES_TYPST_2.1.md`.
