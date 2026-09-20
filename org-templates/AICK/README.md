# org-templates/AICK

Official house template for **Center for AI Civic Knowledge (AICK)**
Thai-language preprints. See `MANIFEST.md` for the file-by-file index and
`QUICKSTART.md` for the short, copy-paste path to producing one paper.

## The brand rule (founder-supplied, verbatim)

The founder's own brand rules live at `source/BRAND_RULES_ORIGINAL.md`.
Its "กฎแบรนด์" (brand rule) section, quoted here exactly, byte-for-byte:

> ใช้ `aick-thai-preprint.cls` เป็น class หลักเท่านั้นสำหรับ preprint
> ภาษาไทยของศูนย์ฯ ที่ใช้ house style นี้ อย่าแก้ตำแหน่งโลโก้, PREPRINT,
> front matter, page 2 methodology note, running header/footer หรือ
> palette ในไฟล์ `.tex` รายบทความ หากต้องแก้ระบบภาพรวม ให้แก้ class กลาง
> และเพิ่ม version ของ template แทน

In English: use `aick-thai-preprint.cls` as the *only* main class for the
center's Thai-language house-style preprints. Do not change the logo
position, PREPRINT marker, front matter, page-2 methodology note, running
header/footer, or palette inside a per-article `.tex` file. If the overall
system needs a change, edit the central class and bump the template's
version instead.

**This is official policy, not a style suggestion.** ALL of AICK's
Thai-language preprint output MUST use this house template
(`source/aick-thai-preprint.cls`). An author or an AI drafting an AICK
paper does not get to opt out of it, and does not get to hand-roll an
equivalent-looking `.tex` file from scratch.

## What an author/AI may edit vs what is locked

**Editable** — the `\AICK...` metadata API and body content, all supplied
either directly in a `.tex` file following `source/aick-paper-template.tex`,
or via the structured-data pipeline (`schema/` + `scripts/aick_generate.py`,
see `QUICKSTART.md`):

- Metadata macros: `\AICKTitle`, `\AICKSubtitle`, `\AICKAuthor`,
  `\AICKAuthorShort`, `\AICKORCID`, `\AICKAffiliation`, `\AICKShortTitle`,
  `\AICKVersion`, `\AICKDate`, `\AICKAbstract`, `\AICKKeywords`.
- The page-2 methodology/status note text (the argument passed to
  `\AICKMethodologyPage{...}`) — the note must exist and appear on its own
  page (that structural requirement is locked; its wording is not).
- Body content: `\section`/`\subsection` headings and prose from page 3
  onward, `\AICKAcknowledgements{...}`, `\AICKDeclarations{...}`, and the
  `AICKReferences` environment's `\item` entries.

**Locked** — defined once in `source/aick-thai-preprint.cls`, never
redefined or bypassed in a per-article `.tex` file (these are exactly the
class's own `LOCKED` comment blocks):

- **Palette**: `\definecolor{AICKnavy}`, `AICKgold`, `AICKgray`,
  `AICKrulegray` (cls lines 49–52).
- **Running header/footer identity** (cls lines 96–115, `LOCKED RUNNING
  IDENTITY` block): the `fancyhdr` setup, header left/right content
  (author-short / short-title), the footer text
  `AI CIVIC KNOWLEDGE · PREPRINT · <version>` and page-number format, and
  the distinct `AICKfirstpage` style used on page 1.
- **Front matter layout** (cls lines 117–159, `LOCKED FRONT MATTER`
  block), reached only through `\AICKMakeFrontMatter`: the logo's absolute
  `tikzpicture` overlay position (top-right, does not push the title
  block), the `PREPRINT` marker plus version/date line, the left-aligned
  title/subtitle/author block, the gold horizontal rule, and the
  abstract → one-line breathing space → keywords layout on page 1.
- **Logo position**: fixed inside `\AICKMakeFrontMatter` as a
  `remember picture, overlay` node anchored to the page's north-east
  corner — not something a per-article `.tex` file places or resizes.
- **Page-2 methodology page mechanism**: `\AICKMethodologyPage{...}`
  (cls lines 161–169) always renders as its own page and always
  `\clearpage`s before the next section, so body content structurally
  cannot start before page 3. A per-article file supplies the note's
  *text*; it may not redefine the macro or skip calling it.
- **Document class name and options**: `\documentclass{aick-thai-preprint}`
  with no `[options]` — a per-article file that adds an option or renames
  the class has left the house style.

If the overall system needs a change, edit `source/aick-thai-preprint.cls`
itself and bump `\AICK@version`/the class's own version comment — never
patch around a locked block from inside an article.

## Generator and checker scripts — real usage, real results

Three scripts live in `scripts/`, run 2026-09-20 against the checked-in
`examples/example_paper.data.yaml` in this worktree to confirm the
pipeline actually works end to end (not asserted from memory):

### 1. `aick_generate.py` — structured data → rendered `.tex`

```bash
python3 org-templates/AICK/scripts/aick_generate.py \
  org-templates/AICK/examples/example_paper.data.yaml \
  -o /tmp/example_paper.tex
```

Validates the data file against `schema/aick_paper.schema.json` (via the
`jsonschema` library when installed, else a hand-rolled equivalent-shape
check), then renders `templates/aick_paper.tex.j2` against it with Jinja2
(`StrictUndefined`, so a missing field fails loudly instead of rendering
a blank). Actual output, this run:

```
schema validation: PASS
wrote /tmp/example_paper.tex
```

### 2. `verify_aick_tex.py` — structural check on the generated `.tex`

Does not compile the document; checks the textual invariants
`aick-thai-preprint.cls` needs to render correctly (documentclass line
present, front matter and methodology page both appear before the first
`\section`, `\begin{document}`/`\end{document}` and
`\begin{AICKReferences}`/`\end{AICKReferences}` are balanced). Actual
output on the file generated above, this run:

```
[PASS] documentclass{aick-thai-preprint} present
[PASS] AICKMakeFrontMatter present
[PASS] AICKMethodologyPage present
[PASS] first \section{...} present
[PASS] AICKMakeFrontMatter appears before first \section
[PASS] AICKMethodologyPage appears before first \section
[PASS] \begin{document}/\end{document} balanced (exactly one each)
[PASS] \begin{document} appears before \end{document}
[PASS] \begin{AICKReferences}/\end{AICKReferences} balanced

OVERALL: PASS
```

### 3. `aick_template_lock.py` — house-class conformance gate

Mirrors `gov-templates/`'s `gov_template_lock.py` pattern: a structural
gate that never reads or judges the Thai prose itself. It fails closed on
four independent violations — wrong/optioned `\documentclass`, any of the
locked palette/frontmatter macros redefined in the candidate, a
`\section`/`\subsection` appearing before the methodology page, or the
methodology page appearing before the front matter.

```bash
python3 org-templates/AICK/scripts/aick_template_lock.py check /tmp/example_paper.tex
```

Actual output, this run: `TEMPLATE LOCK PASS: /tmp/example_paper.tex`.
The same check was also run directly against
`source/aick-paper-template.tex` (the founder-supplied original) and
against the file rendered from `aick_generate.py`: both PASS.

### What the checkers do NOT verify (disclosed)

- **Neither checker compiles the document.** No `xelatex`/`latexmk` run
  was performed to confirm the `.tex` actually typesets — this sandbox
  does not have an `xelatex` binary installed (only `latexmk` and
  `texlive-latex-base`/`texlive-latex-extra`, not `texlive-xetex`), so a
  real compile plus the Thai fonts the class requires (`Laksaman`,
  `Garuda`, `DejaVu Sans Mono`) has not been exercised here. Treat a
  PASS from these two scripts as "structurally well-formed and
  house-style-conformant," not as "confirmed to typeset." Run the real
  compile command below on a machine with `xelatex` + those fonts before
  treating a paper as final.
- **`aick_template_lock.py` never reads or judges the Thai prose itself**
  — grammar, register, factual accuracy, and the abstract-length
  guideline (~1,400–1,700 Thai characters, from
  `source/BRAND_RULES_ORIGINAL.md`) are entirely outside its scope.
- **`verify_aick_tex.py` is a text-shape check, not a LaTeX parser** — it
  uses regexes on the raw source, so it can be fooled by, e.g., a
  commented-out `\section{` inside a multi-line comment block, or pass on
  a file whose macros are well-ordered but whose LaTeX is otherwise
  broken (unbalanced braces, undefined commands elsewhere).
- **`aick_template_lock.py`'s locked-redefinition list is a fixed set of
  names** (the palette colors and the two front-matter macros) copied
  verbatim from the current `.cls` — if the `.cls` is ever revised to add
  a new locked identity element, that check needs a matching update; it
  will not automatically catch a brand-new locked name it doesn't know
  about.
- **Compile command**, once `xelatex` is available (not yet run in this
  environment — do not report a compile PASS/FAIL beyond what is stated
  here until it actually is):
  ```bash
  latexmk -xelatex -interaction=nonstopmode -halt-on-error \
    org-templates/AICK/source/aick-paper-template.tex
  ```

## Metadata scrub — already checked clean

Two source files were checked for embedded personal metadata before being
committed here, verified directly (not asserted from a prior report):

- `source/ai-civic-knowledge-full-logo.png` — opened with Pillow;
  `Image.open(...).info` returns an **empty dict** (`{}`). No embedded
  author/creator metadata of any kind.
- `source/aick-thai-preprint-template-preview.pdf` — opened with
  `pikepdf`; `docinfo` contains only standard LaTeX-toolchain fields —
  `/Producer: xdvipdfmx (20260305)`, `/Creator: LaTeX with hyperref`,
  `/CreationDate: D:20260920025931Z` — **no personal name, no author
  field**. This is the ordinary toolchain fingerprint every XeLaTeX/
  hyperref PDF carries, not identifying information about a person.

## Discovery — how a session finds "AICK lives here"

See the repo-root `SKILL.md`, "Center for AI Civic Knowledge (AICK) house
template" section: before drafting any AICK paper, check
`org-templates/AICK/` and read `QUICKSTART.md` first — the same mandatory,
not-optional discovery pattern already used for `gov-templates/<AGENCY>/`.

## Not yet built / open items (disclosed, not guessed at)

- No live `xelatex` compile has been run in this development environment
  (see "What the checkers do NOT verify" above) — the pipeline is
  verified up to rendered, schema-valid, structurally-conformant `.tex`,
  not to a rendered PDF.
- `aick_template_lock.py` only checks the four structural invariants
  listed above; it has no equivalent yet to `gov_template_lock.py`'s
  paragraph-level fixed-phrase fidelity check, because AICK papers are
  free-form prose (not a fill-in-the-blank letter) — a different kind of
  drift than NIA's dot-leader letters, and not the same problem to solve.
- Only one house class (`aick-thai-preprint`) exists so far. The
  `org-templates/<ORG>/` layout is meant to generalize the same way
  `gov-templates/<AGENCY>/` does, if more center/org house styles are
  supplied later.
