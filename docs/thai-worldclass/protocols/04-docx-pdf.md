# DOCX / Final PDF Route — Mandatory Thai Composition and QA

Use for formal Thai reports, letters, books, journal-style documents, and final PDFs when an editable Word/office master is required or a DOCX template governs the deliverable.

If editable DOCX is **not** required and the goal is a deterministic polished Thai PDF, consider the Typst route in `09-typst.md` before choosing DOCX solely as an intermediate renderer.

## Semantic gate

Thai prose MUST pass `01-thai-semantic-breathing.md` before DOCX layout work.

Do not import Google Docs thin-space hacks as the semantic source. Rebuild renderer-specific spacing from the semantic model.

## Paragraph system

For publication/book/journal prose, use first-line indent + zero or restrained extra paragraph gap unless the genre requires otherwise.

For formal letters, follow the target letter convention while preserving thought-unit and line-composition gates.

Do not use large paragraph gaps to compensate for weak sentence rhythm.

## Mixed script

Thai and Latin may need separate runs for optical balance. Preserve source-exact URLs, DOI strings, citations, identifiers, and quotations.

Protected atoms may use no-break behavior when semantically necessary, but no-break formatting MUST NOT be used to conceal a composition defect.

## Mandatory QA loop

`semantic compose → author DOCX → render DOCX → inspect every page → recompose/repair → export PDF → render PDF → inspect every page → text-integrity check`

The first repair action for a Thai rhythm defect MUST be recomposition, not spacing manipulation.

## Final acceptance

Do not claim layout success from document XML or text extraction alone.

A final DOCX/PDF MUST pass:

- Thai semantic rhythm gate;
- no abnormal stretched gaps;
- no orphan dependent phrase where avoidable;
- no clipping/overlap;
- stable page breaks;
- readable mixed script;
- font/text integrity checks where applicable.

## Google Docs fallback

When a native Google Doc is the collaboration master but its PDF or justified Thai fails, retain the clean semantic content. Rebuild the final publication copy in Typst/PDF when no editable DOCX is required; otherwise rebuild in DOCX/PDF. Do not preserve broken Google-specific separator choices merely for visual similarity.
