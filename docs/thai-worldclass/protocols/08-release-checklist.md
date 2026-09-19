# Mandatory Release Checklist

An artifact may be marked **READY** only when every applicable item passes. If an item is unavailable, status is NOT READY unless the item is genuinely not applicable.

## 0. Execution proof

- [ ] Required protocol files were read for the chosen route.
- [ ] Thai semantic composition was executed, not merely referenced.
- [ ] Spacing was chosen after thought-unit/breath classification.
- [ ] Renderer-specific fixes did not replace semantic repair.
- [ ] Renderer-specific adaptations were not leaked into another renderer.

## 1. Thai semantic composition

- [ ] semantic wholes kept intact;
- [ ] thought units vary naturally;
- [ ] breath levels 0–4 applied conceptually;
- [ ] previous 3–5 units reviewed for mechanical cadence;
- [ ] current + next 1–2 units considered for layout-sensitive breaks;
- [ ] no avoidable orphan connector/phrase;
- [ ] no abnormal stretched gap;
- [ ] visible pauses correspond to semantic boundaries.

For Google Docs JUSTIFIED:

- [ ] no ordinary stretchable U+0020 remains between visible tokens anywhere in a Thai-dominant justified body paragraph after renderer adaptation; this includes embedded Latin↔Latin word spaces;
- [ ] U+2009 used only after semantic classification;
- [ ] no WORD JOINER / ZERO WIDTH SPACE used as generic repair;
- [ ] NBSP limited to genuine protected atoms;
- [ ] rendered PDF inspected after the last composition change.

For Typst:

- [ ] `protocols/09-typst.md` read;
- [ ] target engine is Typst >=0.15.1 for final verification;
- [ ] Thai text sets or inherits `lang: "th"` and `region: "TH"`;
- [ ] justified Thai uses `linebreaks: "optimized"` explicitly or through the verified house module;
- [ ] Typst source is the clean semantic source, not Google Docs U+2009-adapted text;
- [ ] no generic WORD JOINER / ZERO WIDTH SPACE repair;
- [ ] manual Thai spaces/hard breaks were not inserted merely to force wrapping;
- [ ] layout structure uses grid/block/alignment primitives rather than literal-space tabs;
- [ ] private-company correspondence does not inject a Garuda/government-origin emblem without an authoritative supplied/authorized template;
- [ ] `scripts/typst_preflight.py` static gate passes;
- [ ] Typst compilation passes when final Typst/PDF verification is claimed;
- [ ] final Typst PDF text layer checked when tooling is available;
- [ ] every final Typst PDF page visually inspected.

## 2. Content / identity

- [ ] title/author/affiliation correct;
- [ ] ORCID correct when included;
- [ ] corresponding author correct;
- [ ] no fabricated DOI/arXiv/journal acceptance metadata;
- [ ] version/date/status correct.

## 3. Typography

- [ ] correct A or C profile when house style applies;
- [ ] no B/D remnants;
- [ ] mixed Thai/Latin optically balanced;
- [ ] section hierarchy consistent;
- [ ] running headers/footers correct;
- [ ] page x/y correct where required.

## 4. Math / data / figures

- [ ] no equation clipping;
- [ ] no severe scaling;
- [ ] table headers readable;
- [ ] wide objects promoted/split before shrinking;
- [ ] figures/captions remain associated.

## 5. PDF / render

- [ ] every final page rendered and inspected;
- [ ] no clipping/overlap;
- [ ] no abnormal whitespace;
- [ ] all fonts embedded where required;
- [ ] ToUnicode present where required;
- [ ] no missing glyph;
- [ ] no U+FFFD;
- [ ] references/citations resolved;
- [ ] PDF searchable/copyable;
- [ ] source/text-layer fidelity checked when meaningful.

## 6. arXiv/source package

- [ ] current processor verified for actual submission environment;
- [ ] source lint passes;
- [ ] preflight passes;
- [ ] source ZIP contains only required source/assets;
- [ ] arXiv-generated PDF inspected before final submission.

## Mandatory status language

- **READY** — all applicable gates pass.
- **DRAFT / NOT READY** — one or more mandatory gates remain.
- **CANNOT VERIFY** — a required gate could not be performed.

Do not use “final”, “verified”, “publication-ready”, or equivalent wording when status is DRAFT / NOT READY / CANNOT VERIFY.
