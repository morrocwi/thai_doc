# Installation / Import

This ZIP is a standalone skill folder. Its root contains `SKILL.md`.

Install/import it only in an environment that supports custom skill folders or skill ZIPs.

## Critical post-install smoke test

Do not test only whether the skill can generate Thai. Test whether it FAILS unsafe Thai composition.

Recommended smoke prompts:

1. “Create a justified Thai Google Doc paragraph and apply the Thai Semantic Breathing hard gates.”
2. “Show that ordinary U+0020 stretch spaces are rejected in a Thai-dominant Google Docs justified body.”
3. “Create a line-break case where ‘หาก’ would become orphaned and recompose the sentence instead of using WORD JOINER.”
4. “Render the same clean Thai semantic source in Typst as a layout oracle without carrying Google Docs U+2009 into `.typ`.”
5. “Create a private-company letter to a ministry in Typst and verify that no Garuda/government-origin emblem is injected.”
6. “Create A_ONE_COLUMN Thai paper with a long equation and require semantic + PDF preflight.”
7. “Convert to C_TWO_COLUMN without shrinking math/tables below readability.”

## Mechanical linters

```bash
python scripts/thai_semantic_lint.py --self-test
python scripts/typst_preflight.py --self-test
python scripts/validate_pack.py
```

## Typst route

v2.1 targets **Typst >=0.15.1** for verified final Typst/PDF output.

```bash
typst --version
python scripts/typst_preflight.py typst/examples/formal_private_to_government.typ --document-kind private
python scripts/typst_preflight.py typst/examples/formal_private_to_government.typ --document-kind private --compile
```

If Typst is not installed, static preflight still works, but final Typst/PDF verification status is **CANNOT VERIFY** until compilation and rendered-page QA are performed in an environment with the required engine and Thai fonts.

The pack intentionally does not bundle font files. XeLaTeX routes require the declared TeX-Live fonts in the build environment; Typst routes require an available Thai-capable font such as Sarabun, TH Sarabun New, or Noto Sans Thai.
