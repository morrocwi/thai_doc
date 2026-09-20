# AICK Thai preprint — quickstart

Full policy, locked-vs-editable list, and checker limitations: **`README.md`**.

## Schema fields (`schema/aick_paper.schema.json`)

- `title` — main title (page 1, large bold)
- `subtitle` — subtitle line (empty string to omit)
- `author` — full author name shown on page 1
- `authorshort` — surname/short name for running header
- `orcid` — bare ORCID id (empty string to omit the icon)
- `affiliation` — shown next to author, e.g. `Center for AI Civic Knowledge`
- `shorttitle` — short title for running header
- `version` — e.g. `v1.0`
- `date` — Thai-formatted date string
- `abstract` — page-1 abstract prose (~1,400–1,700 Thai characters)
- `keywords` — one semicolon-separated string
- `methodology_note` — required page-2 status/human-AI-role note
- `sections` — array of `{heading, body}`, rendered from page 3 on
- `acknowledgements` — optional end-matter prose
- `declarations` — optional status/COI/data-availability prose
- `references` — optional array of full reference-entry strings

## Generate

```bash
python3 org-templates/AICK/scripts/aick_generate.py \
  <your_data.yaml> -o <out.tex>
```

## Check

```bash
python3 org-templates/AICK/scripts/verify_aick_tex.py <out.tex>
python3 org-templates/AICK/scripts/aick_template_lock.py check <out.tex>
```

`verify_aick_tex.py`: `OVERALL: PASS` = structurally well-formed (macro
order, balanced environments). `aick_template_lock.py`: `TEMPLATE LOCK
PASS` = uses the locked class unmodified, no locked macro/palette
redefined, correct page order. Neither compiles the document or checks
Thai prose quality — see `README.md` for what is NOT verified.

## Compile

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error <out.tex>
```

Requires `xelatex` plus the fonts `Laksaman`, `Garuda`, `DejaVu Sans Mono`.
