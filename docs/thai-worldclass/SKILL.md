---
name: thai-worldclass-publication-system
description: Create, revise, typeset, convert, and preflight Thai academic and formal publications with fail-closed semantic composition across Google Docs, DOCX/PDF, Typst/PDF, and XeLaTeX/arXiv. Use for Thai formal letters, reports, journal articles, preprints, one-column or two-column papers, Thai semantic breathing and line composition, renderer diagnostics, deterministic PDF composition, ORCID/DOI/arXiv metadata, overflow prevention, PDF text integrity, and source packaging. The only house visual profiles are A_ONE_COLUMN and C_TWO_COLUMN.
---

# Thai World-Class Publication System

## CRITICAL — KNOWN AI FAILURE MODES. READ THIS BEFORE ANY OTHER SECTION.

This skill exists because an AI can produce Thai text that is factually correct yet visually and cognitively wrong. The following failures are known, recurrent, and MUST be assumed possible on every task:

1. **False skill-use failure.** The AI may read a Thai-writing guideline and then claim the skill was “used” even though no mandatory semantic pipeline or validator was applied. Reading a reference is NOT execution.
2. **Spacing-first failure.** The AI may draft prose first, justify it, observe ugly gaps, and then patch spaces. This reverses the required pipeline and is forbidden.
3. **Mixed-separator failure.** In justified Thai, the AI may mix ordinary U+0020 spaces, U+2009 thin spaces, NBSP, or zero-width characters without classifying the semantic boundary first. This causes stretched gaps and unstable wrapping.
4. **Unicode-patch failure.** The AI may repair an orphan phrase by inserting WORD JOINER, NBSP, or another no-break character instead of recomposing the sentence. Renderer characters MUST NOT substitute for semantic composition.
5. **No-thought-map failure.** The AI may write long Thai paragraphs without explicitly distinguishing semantic wholes, thought units, and breath levels. If no thought-unit model exists internally, Thai semantic breathing has not been executed.
6. **No-lookahead failure.** The AI may allow connectors such as “หาก”, “โดย”, “ซึ่ง”, “เพื่อ”, or another dependent phrase to become an orphan at a line or page boundary because it did not inspect the next 1–2 units.
7. **Mechanical-rhythm failure.** The AI may create repeated medium/medium/medium or equal-length cadence while believing that “natural language” was achieved. Rhythm MUST be checked across the previous 3–5 units.
8. **Layout-only QA failure.** The AI may inspect only clipping, overflow, or page count and miss stretched gaps, broken thought units, repetitive rhythm, or bad semantic line breaks. A document can be visually un-clipped and still FAIL.
9. **Renderer-leak failure.** A Google Docs spacing workaround may be copied into DOCX or LaTeX. Renderer adaptations are local and MUST NOT contaminate the semantic source.
10. **Premature verification failure.** The AI may say “checked”, “passed”, or “publication-ready” after only one layer of QA. Verification requires the gates defined below; otherwise status MUST remain unverified.
11. **Alignment-escape failure.** The AI may switch Thai body text from JUSTIFIED to START/LEFT simply because Google Docs justification is difficult. This hides the renderer/composition defect instead of solving it. Alignment is a document requirement, not a safety valve. The AI MUST NOT change alignment merely to make QA easier.
12. **Mixed-script stretch failure.** The AI may correctly replace Thai-to-Thai breath spaces yet leave ordinary U+0020 beside Latin tokens, parentheses, numbers, or protected names inside a Thai-dominant JUSTIFIED paragraph. Google Docs can still stretch those spaces dramatically. Renderer adaptation must cover mixed-script boundaries too.
13. **Latin-run exemption failure.** The AI may assume that U+0020 spaces *inside a purely Latin phrase* are safe because neither side is Thai. This is false in a Thai-dominant JUSTIFIED paragraph: Google Docs justifies the line, not the script run, so a single internal Latin word space can expand across the entire remaining line (for example `ENTERPRISE                 CO.,`). In Thai-dominant JUSTIFIED body text, ordinary U+0020 between visible tokens is forbidden throughout the paragraph after renderer adaptation, including inside embedded English names. Use a non-stretching renderer separator chosen by semantic role; use U+202F/ NBSP only for genuine protected micro-atoms, not as a generic patch.
14. **Stale-reference failure.** The AI may copy a workaround from an old renderer/template after the underlying engine has changed. The 2023 `typst-govdoc` note that Thai needs manual spacing for line breaking is historical and MUST NOT be treated as a current Typst rule. Current capability must be verified against the target engine version.
15. **Cross-render contamination failure.** The AI may pass Google Docs U+2009 thin-space adaptations into Typst or XeLaTeX. Typst MUST receive the clean semantic source; renderer-specific separators remain isolated to Google Docs.
16. **Authority-emblem failure.** The AI may copy a government-origin Garuda/header template into a private-company letter merely because the recipient is a government agency. Private-to-government correspondence MUST preserve the sender's private identity and MUST NOT imply government origin.
17. **Compositor-as-semantics failure.** The AI may accept a cleaner Typst line break as proof that the wording is semantically good. Typst is a layout oracle/compositor, never the semantic authority. If the wording or thought-unit model is wrong, a clean Typst page does not make it right.

### Mandatory response to these risks

The AI MUST use a **fail-closed** workflow. If any mandatory gate cannot be performed or verified, it MUST stop the affected route, preserve the requested/template/genre alignment intent, choose a different compositor when necessary, or clearly state that the artifact is not fully verified. It MUST NOT silently downgrade a hard rule into a suggestion, and MUST NOT switch to START/LEFT merely to escape a justification defect.

---

## HARD EXECUTION CONTRACT

For every substantial Thai writing or rewriting task, the following order is mandatory and MUST NOT be skipped or reordered:

**Meaning → Thought Unit → Breath Weight → Rhythm Variation → Line Fit → Renderer Adaptation → Preflight → Render Feedback → Release Gate**

The following are hard invariants:

- **Spacing MUST follow thought. Thought MUST NOT follow spacing.**
- The AI MUST build an internal semantic thought-unit model before renderer-specific spacing.
- Unicode separators MUST be chosen only after thought units and breath weights are settled.
- If the output is Thai + Google Docs + JUSTIFIED, `protocols/01-thai-semantic-breathing.md` and `protocols/03-google-docs.md` are mandatory reads before the first content write.
- If the output or diagnostic route uses Typst, `protocols/09-typst.md` is mandatory before generating `.typ` source. Typst receives the clean semantic source, never Google Docs renderer-adapted text.
- If a rendered defect is found, repair MUST begin with recomposition, not spacing manipulation.
- A renderer-specific workaround MUST NOT be promoted into a language rule.
- A task is not READY until every applicable release gate in `protocols/08-release-checklist.md` passes.
- For Typst, current v2.1 contract targets Typst >=0.15.1, `lang: "th"`, `region: "TH"`, and optimized line breaking for justified Thai. A missing/older CLI makes final Typst verification CANNOT VERIFY.

### Mandatory stop conditions

STOP or change route when any of these is true:

- Thai semantic composition was not performed before spacing/rendering.
- A justified Thai-dominant body paragraph still contains ordinary stretchable U+0020 between visible tokens anywhere in the paragraph after renderer adaptation, including inside embedded Latin phrases. Pure-English paragraphs are outside this gate; Thai-dominant mixed-script paragraphs are not.
- A line/page orphan is repaired only with joiners or non-breaking spaces rather than recomposition.
- A visually inspected page contains abnormal stretched gaps.
- The AI cannot distinguish semantic whole vs breath boundary for a disputed phrase.
- A Google Docs justified layout cannot pass rendered QA after recomposition; in that case, change compositor rather than silently changing alignment.
- The final PDF cannot be inspected when the user requested a final/polished deliverable.
- A Typst route inherits manual Thai spacing/wrapping from a stale 2023 reference instead of current automatic Thai segmentation.
- Typst source contains Google-Docs-only U+2009 thin-space adaptation or generic control-character repair.
- A private-company letter injects a Garuda/government-origin emblem without an authoritative supplied/authorized template.
- Typst CLI is unavailable or older than 0.15.1 when final Typst/PDF verification is required.
- Font/text integrity, identifiers, citations, equations, tables, or accessibility cannot be verified where required.

When a Google Docs JUSTIFIED route fails, DO NOT silently switch to START/LEFT. Recompose first. If native Google Docs still cannot pass, use Typst/PDF as the preferred deterministic compositor when no editable DOCX is required; otherwise use DOCX/PDF or XeLaTeX as appropriate. Preserve the justified-layout intent unless the user or an authoritative template explicitly requires a different alignment.

Typst may also be used as a **layout oracle**: render the same clean semantic source in Typst to help distinguish a semantic/composition failure from a Google Docs renderer failure. This comparison is diagnostic only; it never overrules meaning.

---

## Non-negotiable output profiles

Only two house profiles exist:

- `A_ONE_COLUMN` — global preprint / theory / philosophy / social science / long-form research.
- `C_TWO_COLUMN` — scientific letter / mathematics / physics / technical paper.

B/D profiles do not exist. An official venue template may override house visuals, but it MUST NOT override Thai semantic composition, overflow safety, or QA gates unless the venue explicitly requires an incompatible behavior and the conflict is disclosed.

---

## Mandatory routing

Before authoring, classify the output route using `protocols/00-routing.md`.

1. Native Google Docs collaboration → `protocols/03-google-docs.md`.
2. DOCX or editable office master → `protocols/04-docx-pdf.md`.
3. Typst / deterministic Thai PDF / formal-letter PDF / renderer diagnostic → `protocols/09-typst.md`.
4. LaTeX / arXiv / equation-heavy / table-heavy → `protocols/05-latex-arxiv.md`.
5. One-column publication → `protocols/06-style-a.md`.
6. Two-column publication → `protocols/07-style-c.md`.
7. If collaboration plus publication outputs are needed, keep one renderer-neutral semantic source and derive each renderer output independently.

The semantic source is authoritative. Renderer hacks are not.

---

## Mandatory Thai semantic gate

Before substantial Thai prose generation, revision, or layout-sensitive conversion, read `protocols/01-thai-semantic-breathing.md`.

The AI MUST internally determine:

- semantic wholes that must not be split;
- thought-unit boundaries;
- breath level 0–4 at each meaningful boundary;
- rhythm pattern across the previous 3–5 units;
- line-fit implications and next 1–2 unit lookahead;
- renderer-specific separator only after the above.

Do not expose private chain-of-thought. The internal semantic map is an execution requirement, not a user-facing reasoning trace.

For Google Docs JUSTIFIED Thai, run the mechanical checks in `scripts/thai_semantic_lint.py` when text can be exported or staged as plain text. Mechanical lint does not replace semantic judgment.

---

## Publication metadata

For publication-style outputs, support when known:

- full author name(s), affiliation(s), city/country;
- ORCID for each author;
- corresponding-author marker and email;
- article type;
- article ID or internal manuscript ID;
- DOI only when assigned; draft placeholders must be clearly marked;
- arXiv ID only when assigned; draft placeholders must be clearly marked;
- received / revised / accepted / updated dates when relevant;
- version number;
- open-access license when known;
- PDF metadata;
- running header, short title, footer, and page `x / y` for house styles.

Never fabricate a DOI, arXiv ID, journal volume/issue, acceptance date, publication status, author identity, affiliation, or source.

---

## Equations, tables, figures

Read `protocols/02-overflow-and-qa.md` before equation-heavy, table-heavy, or figure-heavy work.

Invariant: **structure before scaling**.

- Long equation escalation: semantic restructuring → aligned/split/multline → factor/define intermediates → full-width object → scaling only as last resort.
- Wide table escalation: semantic reflow/tabularx → full-width → split/appendix → multi-page/landscape → scaling only as last resort.
- Severe pre-scale overflow above the configured threshold MUST fail closed.
- “Technically fits” is not enough if readability fails.

---

## PDF acceptance

A PDF is not final because it compiles or looks plausible at a glance. Final QA MUST include every applicable check:

- no clipped or overlapping content;
- no meaningful overfull box beyond limit;
- no missing glyphs;
- all fonts embedded;
- ToUnicode present;
- references/citations resolved;
- Thai text searchable and copyable;
- no U+FFFD replacement characters;
- text-layer/source comparison when source is known;
- every page visually inspected;
- Thai rhythm and line composition checked, not only overflow;
- equations, tables, figures, captions, running heads, footers, page numbers, and column balance checked.

For strict final-publication PDF where source text is available, target normalized text fidelity ≥99.5% when meaningful. If Google Docs PDF export cannot meet the gate, preserve it as the collaboration copy and create the final publication copy through Typst/PDF when editability is not required, or through DOCX/PDF / XeLaTeX/PDF when those routes better fit the deliverable.

---

## LaTeX engine

Use XeLaTeX. The bundled `latex/thaiarxiv.sty` does not bundle font files.

Before real arXiv submission, verify current arXiv processor/TeX Live support and run:

```bash
python latex/tools/source_lint.py <source-root-or-main.tex>
python latex/tools/preflight.py <main.tex>
```

Then render every page and inspect it. Automated PASS never replaces visual QA.

---

## Required references by task

- Routing → `protocols/00-routing.md`
- Thai prose, formal Thai letters, Thai reports → `protocols/01-thai-semantic-breathing.md`
- equations/tables/figures/PDF QA → `protocols/02-overflow-and-qa.md`
- Google Docs → `protocols/03-google-docs.md`
- DOCX/final PDF → `protocols/04-docx-pdf.md`
- Typst/final PDF/layout oracle/formal letter → `protocols/09-typst.md`
- LaTeX/arXiv → `protocols/05-latex-arxiv.md`
- A one-column → `protocols/06-style-a.md`
- C two-column → `protocols/07-style-c.md`
- release → `protocols/08-release-checklist.md`

Do not skip a required reference because the task looks simple if it crosses that reference's trigger condition.

---

## Final fail-closed principle

If semantic composition, line fit, rendered rhythm, layout, text integrity, font availability, identifiers, citations, equations, tables, or accessibility cannot be verified, the AI MUST NOT claim READY, publication-ready, final, verified, or equivalent status.

Deliver the safest verified artifact and explicitly identify the remaining gate.
