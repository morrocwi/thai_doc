# XeLaTeX / arXiv Route — Mandatory Gates

Use XeLaTeX for Thai Unicode shaping and scientific typesetting.

## Semantic source first

Thai semantic composition MUST occur upstream of TeX.

- Meaning/thought units/breath levels MUST be settled before TeX macros.
- Google Docs U+2009 choices MUST NOT be copied mechanically into LaTeX.
- TeX line breaking and semantic breathing macros are renderer behavior, not the semantic model.

## Portability

- Do not bundle font files.
- Prefer TeX-Live fonts by filename in arXiv-targeted source.
- Before real submission, verify current arXiv processor and TeX Live availability.
- Keep source package minimal: `.tex`, local `.sty`, required `.bib/.bbl`, and final figures only.
- Exclude generated PDF, aux, log, XDV, caches, and unused assets from submission ZIP.

## Overflow discipline

Apply `02-overflow-and-qa.md`.

Structure MUST precede scaling for equations, tables, and figures.

## Build gates

Before release, MUST run:

```bash
python latex/tools/source_lint.py <source-root-or-main.tex>
python latex/tools/preflight.py <main.tex>
```

Both must pass, subject to explicitly disclosed non-blocking warnings.

Then render every page and inspect visually. Automated PASS is not release approval.

## arXiv identity

This skill is arXiv-compatible, not an official arXiv visual template. Do not imply arXiv endorsement or a universal arXiv house style.
