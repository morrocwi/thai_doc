# arXiv Submission Checklist — Thai XeLaTeX (Mandatory)

## Before upload

The submission MUST NOT proceed until:

- Thai semantic composition is complete upstream of TeX;
- `tools/source_lint.py` passes;
- `tools/preflight.py main.tex` passes;
- every page is rendered and inspected for Thai marks, line rhythm, equations, tables, float order, page balance, and clipping;
- every figure is in a final XeLaTeX-friendly format;
- unused figures and generated build artifacts are removed;
- `thaiarxiv.sty` is included beside the main source unless guaranteed by the environment;
- no font files are bundled when using the toolkit's TeX Live font strategy.

## During arXiv submission

- Choose XeLaTeX when required by the source.
- Verify the current processor/TeX Live version offered by arXiv at submission time.
- Let arXiv generate its normal processing configuration unless a special case requires otherwise.
- Inspect the PDF produced by arXiv; local PASS is not enough.

## Reject the submission draft if

- Thai semantic rhythm breaks after arXiv rendering;
- any equation/table is unreadably scaled;
- an overfull box changes visible content or crosses a margin;
- a Thai glyph/mark is missing or detached;
- references/citations remain unresolved;
- fonts are not embedded or lack usable ToUnicode mapping;
- copy/search of Thai text is materially corrupted;
- a wide table/equation is forced into a narrow column when a structural/full-width solution exists.
