# Thai LaTeX Publication Policy — Mandatory

## Core invariants

**Meaning before spacing. Structure before scaling. Render before release.**

The typesetter MUST NOT repair Thai prose, equations, or tables by blindly compressing or spacing the artifact until it fits.

## Thai prose

1. Compose semantic thought units first.
2. Classify breath weight before renderer macros.
3. Vary short/medium/long units according to content; fixed cadence is forbidden.
4. Level 1–2 may use subtle renderer breathing macros.
5. Level 3–4 MUST use syntax, punctuation, sentence, or paragraph structure.
6. Let XeTeX Thai line breaking handle ordinary wrapping after semantic composition.
7. Protect only genuine short lexical atoms; do not put long clauses in unbreakable boxes.
8. A line-break defect MUST be repaired by recomposition before no-break tricks.

## Equations

**Structure → break → full width → scale**

- Prefer `aligned`, `split`, `multline`, definitions of intermediate variables, or appendix derivations.
- Two-column wide math SHOULD use `WideEquation` when a column cannot preserve structure.
- `FitEquation` is last resort.
- Pre-scaling width >115% of available width is a hard failure.
- An equation that fits numerically but is unreadable still fails visual QA.

## Tables

**Reflow → widen → split → multi-page/landscape → scale**

- Prefer semantic column redesign and `tabularx`.
- Use `WideTable` / `table*` for justified full-width two-column tables.
- Use appendices for secondary dimensions.
- Use `FullWidthLongTable` for multi-page tables.
- Use `FullWidthLandscape` for genuinely wide structures.
- Scale only as a last resort.
- Pre-scaling width >115% is a hard failure.

## Build acceptance

A paper is NOT publication-ready until all applicable gates pass:

- semantic Thai gate;
- compile gate;
- overflow gate;
- reference/citation gate;
- glyph gate;
- PDF font embedding and ToUnicode gates;
- Thai text-layer coverage gate;
- every rendered page visually inspected;
- no equation/table made unreadable merely to silence a warning.
