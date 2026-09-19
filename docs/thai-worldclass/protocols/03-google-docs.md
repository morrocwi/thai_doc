# Native Google Docs Route — Strict Thai Enforcement

Google Docs is a collaboration surface. It is NOT assumed to be a reliable final compositor for justified Thai.

## Mandatory pre-write gates

Before the first substantial Thai body-text write:

1. Read `01-thai-semantic-breathing.md`.
2. Compose semantic wholes and thought units.
3. Classify breath boundaries 0–4.
4. Review rhythm over the previous 3–5 units.
5. Consider line budget and current + next 1–2 units.
6. Only then choose Google Docs separators/alignment.

If steps 2–5 were not done, STOP. Do not write justified Thai body text.

## Alignment resolution — NO safety default

There is **no START/LEFT safety default** for Thai body text.

Alignment MUST be resolved from the authoritative source in this order:

1. explicit user instruction;
2. supplied template or existing document convention;
3. established output/genre standard;
4. only if still genuinely unspecified, choose the alignment appropriate to the artifact — but never choose START/LEFT merely because it is easier to render.

For formal Thai business/government correspondence, preserve the established body alignment required by the target template or house standard. If that standard is JUSTIFIED, the AI MUST keep JUSTIFIED and satisfy the hard gates below.

Changing JUSTIFIED to START/LEFT in order to hide stretched gaps, orphan phrases, or bad line composition is an **alignment-escape failure** and is forbidden.

## JUSTIFIED Thai route with hard gates

When JUSTIFIED is required by the user, template, or output standard, apply the following rules.

### Thai-dominant paragraph U+0020 hard gate

Mixed-script and embedded-Latin spaces are both covered by this gate.

For Thai JUSTIFIED body paragraphs:

- Level 0 MUST have no separator.
- Level 1–2 SHOULD use U+2009 THIN SPACE after semantic composition.
- Level 3–4 MUST use punctuation/syntax/sentence/paragraph structure, not wider spaces.
- Ordinary U+0020 between visible tokens anywhere inside a Thai-dominant JUSTIFIED body paragraph is forbidden after renderer adaptation. The renderer justifies the entire line, so this rule includes Thai↔Thai, Thai↔Latin, Latin↔Thai, Thai↔number, Thai↔punctuation, and **Latin↔Latin spaces inside embedded English phrases**.
- There is **no purely-Latin-run exemption** inside a Thai-dominant justified paragraph. A phrase such as `ARAYA NIKAH SOCIAL ENTERPRISE CO., LTD.` must not retain ordinary word spaces merely because the phrase itself is English. Use U+2009 for tested breakable lexical separation, and use U+202F/NBSP only for a genuine protected micro-atom such as `CO., LTD.` when continuity requires it.
- A paragraph that is genuinely English-dominant/pure English is outside this Thai-dominant rule and may use ordinary U+0020 according to its own renderer behavior.
- U+2060 WORD JOINER and U+200B ZERO WIDTH SPACE are forbidden as generic composition repairs.
- NBSP is allowed only for a genuine protected atom, usually short Latin text or number+unit.
- Never replace all spaces mechanically.
- Never insert thin spaces at fixed word intervals.

## Three kinds of spaces MUST be distinguished

Before mutation, classify each visible spacing case as one of:

1. **lexical/protected space** — e.g. short Latin phrase, identifier, proper name, or number/unit atom;
2. **semantic breath boundary** — governed by breath level;
3. **formatting space** — metadata labels, tabular/letter formatting, not prose rhythm.

Do not treat these categories as interchangeable. Classification does **not** make U+0020 safe. In Thai-dominant JUSTIFIED prose, a visible space touching Thai script must still be rendered with a non-stretching separator chosen after semantics. Inside a Thai-dominant JUSTIFIED paragraph, purely Latin internal spaces do **not** receive an exemption: ordinary U+0020 is still stretchable and must be adapted. Pure-English paragraphs are handled separately.

## Forbidden repair behavior

If a line/page breaks badly, DO NOT first:

- insert WORD JOINER;
- add NBSP;
- add/double spaces;
- delete spaces blindly;
- shrink font solely to hide the issue.

Repair order MUST be:

1. recompose thought units;
2. reorder clauses;
3. move an optional modifier;
4. adjust a legitimate breath boundary;
5. rebalance paragraph/page flow;
6. only then adjust renderer separator.

## Line and page lookahead

Before accepting a rendered break, inspect at least current unit + next 1–2 units.

Dependent connectors such as `หาก`, `โดย`, `ซึ่ง`, `เพื่อ`, `เมื่อ`, `เพราะ`, `แต่`, `และ`, `หรือ`, `โดยเฉพาะ` MUST NOT be stranded when a semantic recompose can keep the phrase intact.

## Mechanical lint

When body text can be staged/exported to UTF-8 text, run:

```bash
python scripts/thai_semantic_lint.py <file.txt> --mode google-docs-justified
```

For rendered line text, add:

```bash
python scripts/thai_semantic_lint.py <rendered.txt> --mode google-docs-justified --rendered-lines
```

A lint PASS is necessary where applicable but not sufficient; semantic and visual gates remain mandatory.

## Index safety

Never compute Thai edit/style ranges from guessed Unicode character counts. Use provider-returned ranges, live indexes, exact structure, or verified text ranges.

## Mandatory render loop

For any final/polished Google Doc with substantial Thai body text:

1. write;
2. export PDF;
3. render every page;
4. inspect stretched gaps, line rhythm, orphan phrases, mixed script, page breaks, clipping;
5. if failure occurs, return to semantic composition before spacing repair;
6. re-export and re-inspect affected pages.

If the Google Docs JUSTIFIED route still fails after recomposition, DO NOT switch to START/LEFT as a repair. Fail closed on the native-Docs final-layout route. Use Typst/PDF as the preferred deterministic final compositor when no editable DOCX is required; otherwise use DOCX/PDF or XeLaTeX according to the deliverable. Preserve the required alignment intent. In this protocol, **fail closed** means the native-Docs final-layout route is rejected rather than weakening alignment or semantic rules.

## Final PDF rule

If Google Docs PDF is visually acceptable but text-integrity QA fails strict publication requirements, keep the Google Doc as collaboration copy and create the final publication output through Typst/PDF when editability is not required, or through DOCX/PDF / XeLaTeX when those routes fit better. Do not add more spacing hacks.


## Typst comparison render (v2.1)

When the defect is ambiguous after semantic recomposition, the AI MAY use Typst as a layout oracle under `09-typst.md`:

1. return to the clean semantic source before any U+2009 Google Docs adaptation;
2. render the same prose in Typst with Thai language/region and optimized line breaking;
3. compare the line/page behavior;
4. classify semantic defect vs Google Docs renderer defect;
5. keep every renderer workaround local.

Do not export the Google-Docs-adapted thin-space text directly into Typst.
