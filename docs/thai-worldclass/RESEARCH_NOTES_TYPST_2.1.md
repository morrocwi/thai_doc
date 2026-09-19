# Typst research notes for skill v2.1

Research date: 2026-09-19

## Sources inspected

### whs/typst-govdoc

- Repository: https://github.com/whs/typst-govdoc
- Commit inspected: `b0ca4535c92f70aa94ace3f9bcffeae501df893b` (2023-03-26; repository's only commit at review time)
- Files inspected: `README.md`, `govdoc.typ`, `thai.typ`, `govdoctest.typ`
- GitHub repository metadata has no SPDX/license object; README says `ไม่สงวนลิขสิทธิ์`.

Useful concepts extracted and independently reimplemented in v2.1:

- A4 formal page geometry;
- 16pt Thai formal typography;
- `lang: "th"`, `region: "TH"`;
- first-line indent and justification as paragraph properties;
- structured grids for metadata/attachments instead of literal-space tabs;
- unbreakable signature/sender blocks;
- Thai numeral conversion;
- measurement/alignment instead of manual tabs.

Historical behavior explicitly NOT copied:

- manual Thai spacing/wrapping workaround documented in 2023;
- `#h(2.5cm)` as the way to indent the first body paragraph;
- Garuda asset for private-company correspondence;
- assumptions tied to the early Typst version used in 2023.

No file from `typst-govdoc` is bundled verbatim in this skill.

### typst/typst

- Repository: https://github.com/typst/typst
- Latest stable release inspected: `v0.15.1` (published 2026-07-17)
- Main source snapshot inspected: `094b9634d2aa506757d342103411a33a347e3012` (2026-09-18)
- License: Apache-2.0

Important current capabilities verified in source/tests:

1. `crates/typst-layout/src/inline/linebreak.rs` creates the general ICU4X line segmenter with `icu_segmenter::LineSegmenter::new_lstm(LineBreakOptions::default())`.
2. The general breakpoint path consumes Unicode/UAX #14 opportunities; only Chinese/Japanese use a separate tailored segmenter.
3. The upstream test suite includes `linebreak-thai` and `issue-4468-linebreak-thai` cases, so Thai breaking is actively regression-tested.
4. Optimized line breaking is a Knuth-Plass-style global paragraph optimization, not only greedy first-fit.
5. `par.justification-limits` can constrain word spacing and optionally character tracking.
6. Typst documents that word-space maxima may still be exceeded if no other justification solution exists, so visual QA remains mandatory.
7. `par.first-line-indent` is a modern paragraph property and can apply to all paragraphs through `(amount: ..., all: true)`.
8. Typst's semantic paragraph model affects paragraph styling and export structure; body prose should therefore remain proper paragraphs rather than being simulated with arbitrary blocks/spaces.

## v2.1 design decision

Typst is added as a separate compositor and layout oracle. It never receives Google Docs renderer hacks. The semantic source stays renderer-neutral; Google Docs, Typst, DOCX, and XeLaTeX each derive their own rendering adaptations.

The skill targets Typst >=0.15.1 because this is the reviewed stable release containing the modern paragraph/line-break behavior used by v2.1.

## Why this improves our previous Google Docs approach

Google Docs gives limited control over the justification algorithm, which forced renderer-specific Unicode adaptation. Typst exposes line-breaking strategy and justification limits directly, while also providing structured grids/blocks and deterministic compilation. Therefore v2.1 can:

- preserve semantics without spacing hacks in the clean source;
- diagnose whether a bad line is semantic or Google-renderer-specific;
- set explicit space-stretch bounds rather than relying only on separator substitutions;
- keep signature/attachment geometry structural;
- regression-test a deterministic PDF compositor.

Typst still does not replace semantic breathing. Automatic legal line-break opportunities can be linguistically legal yet rhetorically poor; semantic rhythm and rendered inspection remain mandatory.

## Verification limitation in this build environment

The current build environment did not expose a `typst` CLI binary. Therefore v2.1's Typst source, linter, and packaging can be statically validated here, but a live Typst compile is marked **CANNOT VERIFY** until run in an environment with Typst >=0.15.1 and an available Thai font. This limitation is intentionally fail-closed in `scripts/typst_preflight.py --compile`.
