# thai_doc

Thai-language document generation and layout-fix system for external tools
(Google Docs, Word/DOCX, browsers, PDF, Typst, LaTeX/arXiv).

## Start here

1. **`KNOWN_ISSUES.md`** — real bugs and a real architectural mistake
   already found and recorded in this repo's own history. Read this before
   changing anything; it exists specifically so the mistake is not
   repeated by a future session (any AI vendor).
2. **`docs/thai-worldclass/SKILL.md`** — the primary Thai-composition
   discipline (merged v2.1.0 pack, see "Provenance" below). This is the
   authority on *how* to fix Thai line-wrap/justification/layout problems.
3. **`SKILL.md`** (this repo's own) — the entry point that ties the above
   two together and describes this repo's own scripts.

## What actually changed here (history, short version)

- **v1** (first push) shipped a naive fix: dictionary-tokenize Thai text
  and insert a zero-width space (U+200B) between every word pair, then a
  template→docx/html/txt generator that applied this automatically.
- A much more thoroughly researched external pack,
  `thai-worldclass-publication-system` v2.1.0, was obtained and — per an
  explicit founder instruction — merged in as the **primary** direction,
  with v1's own naive approach demoted after being shown, mechanically and
  reproducibly, to be exactly the kind of failure that pack documents (see
  `KNOWN_ISSUES.md` ISSUE 1: running the merged pack's own lint against
  v1's output flagged 100% of the inserted characters as hard failures).
- `scripts/generate_doc.py` still exists and is still useful (template +
  data → txt/html/docx), but it no longer auto-patches Thai spacing. It now
  offers `--lint`, a mechanical report-only gate powered by the merged
  pack's linter.

## Repo layout

```
KNOWN_ISSUES.md              read first
SKILL.md                     this repo's entry-point skill file
docs/thai-worldclass/        merged v2.1.0 pack -- the primary composition system
  SKILL.md                   its own entry point / 17 named AI failure modes
  protocols/                 per-route rules (Google Docs, DOCX, Typst, LaTeX/arXiv, ...)
  scripts/                   thai_semantic_lint.py, typst_preflight.py, validate_pack.py
  typst/, latex/             house Typst modules + LaTeX/arXiv style + examples
scripts/
  generate_doc.py            template+data -> txt/html/docx, with --lint
  thai_linebreak.py           demoted; diagnostic word-segmentation only, see KNOWN_ISSUES.md
templates/, examples/         this repo's own Jinja2 template + example data
tests/                        tests for scripts/thai_linebreak.py
```

## Usage

### Generate a document from a template

```bash
pip install -r requirements.txt
python3 scripts/generate_doc.py \
  templates/formal_letter.txt.j2 \
  examples/formal_letter.example.yaml \
  -o out.docx -f docx --lint
```

`--lint` runs the merged pack's mechanical Thai lint against the rendered
text and reports findings to stderr; it does not modify the output. Add
`--strict` to make the command exit non-zero on hard findings. Note: the
bundled example template's prose was written as ordinary Thai body text and
is **not** gate-clean out of the box (it still contains ordinary spaces at
what would need to be classified breath boundaries) — this is intentional
and disclosed, not hidden: it demonstrates that `--lint` catches real,
unremediated issues rather than only ever reporting PASS. Fixing the
example's prose to actually pass the gate means applying
`docs/thai-worldclass/protocols/01-thai-semantic-breathing.md`'s semantic
pipeline to it by hand (or by an AI doing that work deliberately), which is
future work, not yet done.

For a deterministic, already-gate-passing Thai formal-letter example, see
`docs/thai-worldclass/typst/examples/formal_private_to_government.typ` and
`docs/thai-worldclass/protocols/09-typst.md`.

### Fixing/composing Thai prose for Google Docs, Word, or anywhere else

Do not run a script and expect a patched-up answer. Read
`docs/thai-worldclass/SKILL.md` and the protocol for your output route
(`docs/thai-worldclass/protocols/00-routing.md`), and apply its semantic
pipeline while writing/revising the Thai text. Use
`docs/thai-worldclass/scripts/thai_semantic_lint.py` as a mechanical sanity
check afterward, never as the fix itself.

## Status / open decisions

See `docs/thai-worldclass/BUILD_REPORT.md` "Verification limitation" for
what that pack itself discloses as unverified (no `typst` CLI in the build
environment used, so a live Typst compile + rendered-page visual QA is
CANNOT VERIFY until run somewhere with the CLI and Thai fonts installed —
also true of this workstation as of 2026-09-19, verified again here).

Still open / not yet built, not guessed at:

1. `scripts/google_docs_batch.py` builds batchUpdate request JSON
   (dry-run, tested) and has a bring-your-own-credentials `apply_live()`
   path, but that live path has never been exercised against a real
   Google Doc in this environment (no credentials available here). For an
   actually-live, more full-featured connection, see
   `docs/google-docs-mcp-integration.md` — a vetted external MCP server
   recommendation, not vendored into this repo.
2. `scripts/generate_doc.py`'s `#SECTION#` marker parsing has a known false
   -positive edge case (`KNOWN_ISSUES.md` ISSUE 3).
3. The bundled example template/data is not yet a gate-clean demonstration
   (see above) — a real one requires doing the semantic composition work,
   not just running a script.
4. `scripts/google_docs_batch.py`'s `from-sections`/`from-lock` output is
   not currently wired to `docs/google-docs-mcp-integration.md`'s
   recommended MCP server — the two are complementary delivery paths, not
   yet connected by an adapter (see that doc's "future work" note).

## Provenance

`docs/thai-worldclass/` is a merged copy of a separately obtained pack,
`thai-worldclass-publication-system` v2.1.0. Its own research/provenance
notes (`docs/thai-worldclass/RESEARCH_NOTES_TYPST_2.1.md`,
`docs/thai-worldclass/BUILD_REPORT.md`) document that it independently
reimplements structural ideas from `whs/typst-govdoc` (no SPDX license
metadata upstream; not copied verbatim) and uses `typst/typst`
(Apache-2.0) concepts. Carried forward unchanged into this repo.

## License

MIT (this repo's own `scripts/`, `templates/`, `examples/`, `tests/`).
`docs/thai-worldclass/` carries its own provenance notes as described
above; treat it as a distinct merged component, not originated in this
repo. `gov-templates/` is likewise a distinct component: it is real
third-party government-agency material (see `gov-templates/README.md` and
each agency's own `MANIFEST.md`), not authored by this repo and not
covered by its MIT license — treat it as reference material republished
for drafting purposes, not as licensed code/content of this repository.
