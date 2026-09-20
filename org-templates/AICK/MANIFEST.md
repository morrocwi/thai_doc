# org-templates/AICK — Center for AI Civic Knowledge Thai preprint house template

Source of the house style: founder-supplied `aick-thai-preprint.cls` +
`aick-paper-template.tex` + logo + brand-rules note, plus a
structured-data generate/check pipeline built on top of them, mirroring
`gov-templates/`'s `source/` + `MANIFEST.md` + `README.md` convention
(adapted for a LaTeX house class rather than DOCX letters). See
`README.md` for the policy and `QUICKSTART.md` for the fast path.

| File | Type | Purpose |
|------|------|---------|
| `source/BRAND_RULES_ORIGINAL.md` | founder-supplied brand rules (verbatim) | The original "กฎแบรนด์" note: what the class is for, the mandatory page structure, what is editable, the recommended abstract length, house-template version status. |
| `source/aick-thai-preprint.cls` | **locked house class** | The canonical LaTeX class. Defines the `\AICK...` metadata API, the locked palette, running header/footer, front-matter layout, page-2 methodology-page mechanism, and end-matter helpers. Never edited by a per-article paper — see README "Locked" list. |
| `source/aick-paper-template.tex` | reference article template | A complete example article using the class directly (hand-editable metadata + body), the same shape `aick_generate.py`'s output must match. |
| `source/ai-civic-knowledge-full-logo.png` | brand asset | The center's logo, placed by the class as a fixed top-right overlay on page 1. Checked clean of embedded metadata (empty PIL `info` dict) — see README "Metadata scrub". |
| `source/aick-thai-preprint-template-preview.pdf` | reference render | A compiled preview PDF of the template, for visual reference. Metadata checked clean (standard LaTeX-toolchain fields only) — see README "Metadata scrub". |
| `schema/aick_paper.schema.json` | JSON Schema (draft-07) | Structured-data contract for `scripts/aick_generate.py`'s input: every required field (`title`, `subtitle`, `author`, `authorshort`, `orcid`, `affiliation`, `shorttitle`, `version`, `date`, `abstract`, `keywords`, `methodology_note`, `sections`) plus optional `acknowledgements`/`declarations`/`references`, each mapped to the class's `\AICK...` macros or body structure. |
| `scripts/aick_generate.py` | generator | `data.yaml/json -> rendered .tex`. Validates against the schema (via `jsonschema` if installed, else a hand-rolled fallback with the same required-field/shape checks), then renders `templates/aick_paper.tex.j2` with Jinja2 (`StrictUndefined`). Never modifies `source/`. |
| `scripts/verify_aick_tex.py` | checker (structural, post-generation) | Regex-based sanity check on a rendered `.tex`: documentclass line present, front matter and methodology page both precede the first `\section`, `document`/`AICKReferences` environments balanced. Does not compile. |
| `scripts/aick_template_lock.py` | checker (house-style conformance gate) | Mirrors `gov-templates/`'s `gov_template_lock.py`: fails closed on a wrong/optioned `\documentclass`, any locked palette/front-matter macro redefinition, a section before the methodology page, or the methodology page before the front matter. `check <candidate.tex>` subcommand. Never reads/judges the Thai prose. |
| `templates/aick_paper.tex.j2` | Jinja2 template | The template `aick_generate.py` renders against; produces a `.tex` file in the same shape as `source/aick-paper-template.tex` from structured data. |
| `examples/example_paper.data.yaml` | example data | One real, schema-valid example data file exercising every field, used to verify the generate → structural-check → lock-check pipeline end to end (see README "Generator and checker scripts"). |
| `README.md` | official policy doc | The 100%-house-template rule (quoting the founder's own brand rules verbatim), the locked-vs-editable list, real generator/checker usage and results, disclosed checker limitations, and the metadata-scrub record. |
| `MANIFEST.md` | this file | File-by-file index of everything under `org-templates/AICK/`. |
| `QUICKSTART.md` | fast-path doc | The single short file an AI should read before producing one AICK paper: schema fields, generate command, check command, compile command. |
