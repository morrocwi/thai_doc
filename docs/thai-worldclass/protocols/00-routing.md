# Mandatory Routing Matrix

Routing MUST be decided before authoring or layout work. The semantic source is renderer-neutral and authoritative; renderer adaptations are derived artifacts.

| Request | Required route | Master profile | Mandatory Thai semantic gate |
|---|---|---|---|
| Thai Google Doc for collaboration | Native Google Docs | A/C only if visual identity requested | YES |
| Formal Thai business/government letter in Google Docs | Native Google Docs | neutral formal | YES; JUSTIFIED adds strict renderer gate |
| Thai report/book/journal DOCX | DOCX | A by default | YES |
| Final PDF where editable DOCX is required | DOCX → PDF | A by default | YES |
| Polished Thai PDF where editable DOCX is NOT required | Typst → PDF preferred | A or neutral formal | YES |
| Private-company formal letter to a government agency, final PDF only | Typst `private-formal` preferred | neutral formal | YES |
| Google Docs justification diagnostic / layout oracle | Clean semantic source → Typst comparison render | same semantic source | YES |
| arXiv / LaTeX / preprint | XeLaTeX | A by default | YES |
| technical short paper / math / physics | XeLaTeX | C by default | YES |
| explicit one-column | Typst/XeLaTeX/DOCX as deliverable requires | A | YES |
| explicit two-column | XeLaTeX by default; Typst only when specifically designed/tested | C | YES |
| official venue template supplied | venue template | house visual overridden | YES; semantic/QA rules remain |

## Hard routing rules

1. The semantic source MUST be composed before renderer adaptation.
2. Google Docs spacing adaptations MUST NOT be copied into Typst, DOCX, or LaTeX.
3. Typst receives the clean semantic source. U+2009 introduced only for Google Docs is a renderer leak and MUST fail Typst preflight.
4. If Google Docs JUSTIFIED cannot pass semantic/render QA, recompose first. If native Docs still fails:
   - use Typst/PDF when deterministic final PDF is wanted and editable DOCX is not required;
   - use DOCX/PDF when office editability is required;
   - use XeLaTeX for arXiv, equation-heavy, or source-submission workflows.
   Never auto-switch to START/LEFT as a safety fallback.
5. Typst may be used as a **layout oracle** to distinguish semantic defects from a Google Docs renderer defect, but it MUST NOT overrule the semantic source.
6. Do not inherit manual Thai wrapping from old Typst references. v2.1 targets Typst >=0.15.1 and requires current automatic Thai segmentation plus optimized line breaking.
7. For private-company → government correspondence, do not add Garuda/government-origin identity merely because the recipient is a government agency.
8. If the user requests final/polished output, a route without rendered-page QA is incomplete.
9. Never route B/D; they do not exist.
10. An official venue template can override visual styling, but MUST NOT silently disable semantic Thai or safety QA.
