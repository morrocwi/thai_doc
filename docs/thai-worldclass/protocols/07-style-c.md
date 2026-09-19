# C_TWO_COLUMN — Scientific Letter (Mandatory House Profile)

Purpose: mathematics, physics, computational/technical papers, short scientific reports, information-dense articles.

Reference source: `latex/examples/C_worldclass_twocolumn.tex`
Reference PDF: `latex/examples/C_worldclass_twocolumn.pdf`

## Semantic precedence

Narrow columns increase line-break risk. Thai semantic composition, lookahead, and protected-whole rules MUST be applied before the two-column layout.

## Visual grammar

- A4 scientific two-column body.
- Strong but minimal top rule/article-type strip.
- Compact title and author block above columns.
- Author + ORCID + affiliation + article history.
- DOI/arXiv/ORCID line under abstract metadata when known.
- Running header: author / short title / status.
- Footer: article ID / page x/y / license+DOI.
- Controlled gutter and strict overflow policy.
- Normal equations remain one-column; genuinely wide equations may span full text width.
- Wide tables/figures may span both columns; do not shrink blindly.
- Body is dense but MUST remain readable.

## Float and line discipline

- Avoid uncontrolled floats that detach content from discussion.
- Critical full-width math/table objects SHOULD use deterministic placement.
- Narrow-column Thai MUST be checked for orphan connectors and repetitive short-line rhythm.

## Hard failures

C output MUST fail release if:

- Thai line composition creates repeated orphan phrases;
- equations/tables are shrunk below readability;
- overflow crosses margins;
- any final page has not been visually inspected when final output is requested.
