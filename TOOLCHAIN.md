# TOOLCHAIN.md — everything this repo needs installed, from a bare machine

This repo targets multiple output routes (Python scripts, LaTeX/XeLaTeX, DOCX, Google Docs,
Typst). Each route needs different system-level tools. This file lists exactly what's needed,
per route, with the real install command and a real verification command — so a fresh machine
(or a fresh AI session) can go from nothing to "fully working" without guessing.

**Status legend:** ✅ = verified installed + a real compile/run confirmed working on this
workstation, on the date noted. ⚠️ = the route exists in this repo but the tool has not been
installed/verified here — do not claim it works until you've actually run the verification
command yourself and it succeeds.

## 1. Python (all routes)

```bash
python3 --version   # 3.10+ recommended
pip install -r requirements.txt
```

Installs: `pythainlp` (Thai NLP/tokenization, used by `scripts/thai_linebreak.py` and
`docs/thai-worldclass/scripts/thai_semantic_lint.py`), `python-docx` (DOCX generation),
`jinja2` (template rendering — `scripts/generate_doc.py`, `org-templates/AICK/scripts/
aick_generate.py`), `pyyaml` (YAML data files), `jsonschema` (schema validation for
`org-templates/AICK/scripts/aick_generate.py` — has a hand-rolled fallback if absent, but install
it for the real Draft7 validation path, not the fallback).

**Verify:** `python3 -c "import pythainlp, docx, jinja2, yaml, jsonschema; print('ok')"` → `ok`

## 2. LaTeX / XeLaTeX route (org-templates/AICK, docs/thai-worldclass/latex/)

Two apt packages beyond a bare `texlive-latex-base` install (all the actual LaTeX *packages* the
AICK class uses — `fontspec`, `orcidlink`, `tikz`, `hyperref`, `fancyhdr`, `titlesec`, etc. — are
already covered by `texlive-latex-extra`/`texlive-pictures`/`texlive-fonts-recommended`, which are
commonly preinstalled; check with `kpsewhich <package>.sty` before assuming a wider TeX Live
install is needed):

```bash
sudo apt update
sudo apt install -y texlive-xetex fonts-thai-tlwg
```

- `texlive-xetex` → gives the `xelatex` binary itself (the AICK class requires XeLaTeX
  specifically, for `fontspec`/`\XeTeXlinebreaklocale`; `pdflatex` will NOT compile it).
- `fonts-thai-tlwg` → gives the Thai font families the class hard-requires:
  `\setmainfont{Laksaman}`, `\setsansfont{Garuda}` (plus other TLWG faces like Kinnari, Loma,
  Norasi, Sawasdee, Umpush, Waree — useful for other Thai LaTeX work in this repo even though AICK
  only uses these two).

**Verify:**
```bash
which xelatex                        # /usr/bin/xelatex
fc-list | grep -iE "laksaman|garuda" # 8 lines: Laksaman/Garuda in Regular/Bold/Italic/BoldItalic
```

**Verified end-to-end on this workstation, 2026-09-20** — both the raw template and the
generator's example output compiled to real 4-page PDFs with zero errors:
```bash
cd org-templates/AICK/source
latexmk -xelatex -interaction=nonstopmode -halt-on-error aick-paper-template.tex
# -> Output written on aick-paper-template.pdf (4 pages, 947976 bytes)

python3 ../scripts/aick_generate.py ../examples/example_paper.data.yaml -o /tmp/example.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error /tmp/example.tex
# -> Output written on example.pdf (4 pages, 944806 bytes)
```
One real warning was found and fixed at the source (not silenced): `fancyhdr` reported
`\headheight` too small (16.0pt, needs ≥16.22998pt given the class's font/margin choices) — fixed
in `aick-thai-preprint.cls` (`\setlength{\headheight}{16.23pt}`, class version bumped to v1.0.1
per this center's own "fix the class, bump the version" rule in `org-templates/AICK/source/
BRAND_RULES_ORIGINAL.md`). Recompiled after the fix: warning gone, PDF still correct.

## 3. DOCX route (scripts/generate_doc.py -f docx)

No extra system package — `python-docx` (already in `requirements.txt`) is pure Python.

**Verify:** `python3 scripts/generate_doc.py templates/formal_letter.txt.j2
examples/formal_letter.example.yaml -o /tmp/out.docx -f docx` → file written, no error.

## 4. Google Docs route (docs/google-docs-mcp-integration.md)

Not a local toolchain install — a live path needs a Google Cloud OAuth credential + either this
repo's own `scripts/google_docs_batch.py --apply-live` (bring-your-own-credentials, never
exercised against a real Doc in this environment — see repo root `README.md` "Status / open
decisions") or the vetted external MCP server that doc recommends. ⚠️ Neither path is installed/
verified on this workstation as of 2026-09-20.

## 5. Typst route (docs/thai-worldclass/typst/, docs/thai-worldclass/scripts/typst_preflight.py)

⚠️ **Not installed on this workstation.** `docs/thai-worldclass/BUILD_REPORT.md` already discloses
this as a "CANNOT VERIFY" gap for the pack's own build; still true as of 2026-09-20 (`which typst`
→ nothing). Typst is not in this machine's apt repos (`apt-cache policy typst` → no candidate);
the two real install paths, neither run here:
```bash
# snap (confirmed available on this machine via `snap info typst`, not installed):
sudo snap install typst
# or build from source (cargo is present on this machine):
cargo install --locked typst-cli
```
**Verify (once installed, not yet done here):** `typst --version`, then compile
`docs/thai-worldclass/typst/examples/formal_private_to_government.typ` per
`docs/thai-worldclass/protocols/09-typst.md` and visually check the rendered PDF (Thai
line-breaking/justification needs a human look, not just a successful exit code).

## Summary table

| Route | System package(s) | Status here (2026-09-20) |
|---|---|---|
| Python scripts (all routes) | — (pip only) | ✅ verified |
| LaTeX/XeLaTeX (AICK, docs/thai-worldclass/latex/) | `texlive-xetex`, `fonts-thai-tlwg` | ✅ verified, real PDF compiled twice |
| DOCX | — (pip only) | ✅ (pure Python, no new system dep) |
| Google Docs (live) | Google Cloud OAuth credential | ⚠️ not verified, no credentials here |
| Typst | `typst` (snap or cargo) | ⚠️ not installed here |
