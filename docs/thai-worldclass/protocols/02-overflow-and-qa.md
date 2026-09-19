# Mandatory Equation, Table, Figure, Thai Rhythm, and PDF QA Policy

## Global rule

**Meaning before spacing. Structure before scaling. Rendered evidence before READY.**

No artifact may pass because it merely compiles or has no clipping.

## Thai prose QA

For any layout-sensitive Thai output, QA MUST include:

- stretched-gap inspection;
- thought-unit continuity;
- orphan connector/phrase inspection;
- rhythm variation across adjacent units;
- semantic boundary vs visible separator check;
- mixed Thai/Latin wrap check;
- page-break continuity.

A page with no overflow can still FAIL if its Thai rhythm or spacing is abnormal.

## Equations

Mandatory escalation:

1. restructure mathematics semantically;
2. use `aligned`, `split`, `multline`, or logical line breaks;
3. factor repeated terms or define intermediates;
4. in C two-column, promote genuinely wide math to full text width;
5. scale only if the object must remain one line;
6. fail closed if severe pre-scale width remains beyond threshold.

Never make subscripts, fractions, operators, or labels unreadably small to hide overflow.

## Tables

Mandatory escalation:

1. rewrite headers and remove repetition;
2. use flexible/semantic columns;
3. promote to full width in C when justified;
4. split table or move secondary dimensions to appendix/supplement;
5. use multi-page table when appropriate;
6. use landscape for genuinely wide data;
7. scale only as final resort;
8. fail if scaling damages readability.

Use booktabs-style rules unless the data model genuinely requires a grid.

## Figures

- Prefer vector output for diagrams/plots when possible.
- Labels MUST remain readable at final physical size.
- Wide figures in C SHOULD span both columns rather than be blindly shrunk.
- Captions MUST stay associated with the correct figure.

## Automated preflight

`latex/tools/preflight.py` checks compile status, meaningful overfull boxes, unresolved refs/cites, missing glyphs, embedded fonts, ToUnicode, U+FFFD, and Thai text-layer coverage.

For staged/exported Thai body text, `scripts/thai_semantic_lint.py` provides mechanical checks for dangerous separator patterns. It cannot prove semantic quality and MUST NOT replace human/model semantic review.

## Visual QA is mandatory for final/polished output

Render every page and inspect:

- clipping/overlap;
- abnormal whitespace;
- Thai stretched gaps;
- line/column balance;
- orphan/widow behavior;
- equation numbers and relation alignment;
- table readability;
- caption association;
- Thai marks and mixed-script baselines;
- running headers/footers/page numbers;
- float order;
- page-break continuity of the argument.

If rendered QA is unavailable, the result MUST NOT be called final or publication-ready.
