# Thai Semantic Breathing and Line Composition Protocol

## MANDATORY CORE — NOT OPTIONAL STYLE ADVICE

This protocol MUST be executed for substantial Thai prose, formal Thai letters, reports, academic writing, and any Thai body text whose layout is being optimized.

If this protocol was merely read but the gates below were not applied, the skill was NOT executed.

## 1. Semantic rhythm comes before spacing

The system MUST create rhythm from meaning first.

It MUST NOT begin from a target such as “insert a space every N words”, “make lines look even”, or “fix the justified gaps”.

Mandatory processing order:

**Meaning → Thought Unit → Breath Weight → Rhythm Variation → Line Fit → Rendering Separator**

Unicode separator selection is the final rendering stage. It is never the source of semantic rhythm.

## 2. Thought units MUST vary naturally

Thai prose MUST contain thought units whose lengths vary according to meaning, emphasis, contrast, and cognitive load.

Acceptable patterns include:

- short → medium → long
- medium → short → medium
- long → short
- very short → medium → long
- medium → long → short → medium

Forbidden when mechanically imposed:

- 3–3–3–3
- 4–4–4
- 5–5–5–5
- medium → medium → medium → medium without rhetorical need

Word counts are diagnostic only. They MUST NOT become the generator of the rhythm.

## 3. Breath weight MUST be classified

Every meaningful boundary in substantial Thai prose MUST be treated as one of the following before renderer spacing is chosen.

### Level 0 — No pause

A semantic whole MUST remain continuous. No visual breath separator is inserted.

Correct:

`ความไว้วางใจระหว่างผู้คน`

Incorrect when still one semantic unit:

`ความไว้วางใจ ระหว่างผู้คน`

### Level 1 — Light breath

A small modifier or local qualification is introduced while the thought continues.

### Level 2 — Normal breath

A subordinate thought closes and the sentence-level argument continues.

This is the main natural spoken-language boundary.

### Level 3 — Strong breath

The argument changes weight, reason, direction, contrast, or conclusion.

MUST be expressed primarily by syntax, punctuation, clause restructuring, or sentence structure. It MUST NOT be encoded merely by a wider space.

### Level 4 — Sentence / paragraph break

The thought closes clearly. Use sentence or paragraph structure as appropriate.

## 4. Space width MUST NOT encode breath strength

The following progression is forbidden as a semantic system:

`thin space → normal space → double space`

Breath strength MUST be carried by:

- unit length;
- punctuation;
- syntax;
- word order;
- sentence length;
- line position;
- paragraph structure.

Spacing is only a secondary visual cue.

## 5. Human rhythm variation gate

The AI MUST inspect at least the previous 3–5 thought units before finalizing the next sequence.

If adjacent units are suspiciously similar in length, syntactic shape, or cadence, it MUST consider recomposition.

It MUST NOT introduce random variation merely to look human. Intentional rhetorical repetition is allowed.

A passage that repeatedly produces medium → medium → medium → medium without rhetorical reason FAILS this gate.

## 6. Line-aware composition gate

One rendered line is NOT one thought unit. A line may contain multiple breath units.

Before finalizing layout-sensitive Thai, estimate line budget from:

- usable page/column width;
- margins;
- font family;
- font size;
- first-line indent;
- relevant mixed-script width.

Normal body lines should often occupy roughly 85–98% of usable width, but MUST NOT be equalized mechanically.

If a line is short, the AI MUST NOT add filler or fake spaces to fill it.

## 7. Never sacrifice semantics for line fill

Forbidden line-fill repairs:

- adding unnecessary words;
- adding spaces;
- splitting a semantic whole;
- moving a boundary only for appearance;
- inserting WORD JOINER or NBSP merely to hide a composition defect.

Permitted only when meaning is preserved:

- reorder a clause;
- move an optional modifier;
- combine related units;
- split a sentence differently;
- accept a shorter line.

## 8. Lookahead rule is mandatory

Before closing a line or accepting a page break, the composition process MUST consider:

**current unit + next 1–2 units**

This prevents orphan thoughts.

Examples of high-risk Thai connectors that SHOULD NOT be stranded when recomposition can keep them with their complement:

`หาก`, `โดย`, `ซึ่ง`, `เพื่อ`, `เมื่อ`, `เพราะ`, `แต่`, `และ`, `หรือ`, `ดังนั้น`, `อย่างไรก็ตาม`, `โดยเฉพาะ`

The correct repair is recomposition first. A no-break Unicode patch is not a substitute.

## 9. Protected semantic wholes

Do not split when the meaning requires continuity:

- person and organization names;
- identifiers;
- DOI/arXiv/ORCID strings;
- URLs;
- citations;
- formulas;
- numbers + units;
- short Latin lexical atoms;
- source-exact quotations;
- legal/source-exact text.

Protection must be semantic, not decorative.

## 10. Google Docs JUSTIFIED renderer adapter

Only when all are true:

- language = Thai;
- output = Google Docs;
- alignment = JUSTIFIED;

apply renderer adaptation AFTER semantic composition.

### Validated preference

For Level 1–2 Thai breath boundaries, use **THIN SPACE U+2009** where the renderer test supports it.

Rules:

- Level 0 → no separator.
- Level 1–2 → U+2009 may be used as renderer adapter.
- Level 3–4 → punctuation/syntax/sentence/paragraph structure, NOT a wider space.
- In a Thai-dominant JUSTIFIED body paragraph, ordinary U+0020 between visible tokens is a preflight failure anywhere in that paragraph after renderer adaptation. This includes Thai↔Thai, Thai↔Latin, Latin↔Thai, and **Latin↔Latin inside embedded English phrases**. Google Docs justifies the whole line, so an internal English word space can stretch even when no Thai character touches it.
- Pure-English paragraphs are outside this Thai-dominant gate. Embedded English inside a Thai-dominant justified paragraph is not. For breakable lexical spacing inside a short Latin run, prefer a tested non-stretching separator such as U+2009. For a genuinely protected micro-atom such as `CO., LTD.` or `10 kg`, U+202F/NBSP may be used only when semantic continuity requires it and overflow has been checked.
- U+2060 WORD JOINER, U+200B ZERO WIDTH SPACE, or NBSP MUST NOT be used as a general orphan-repair technique.
- NBSP may be used only for a genuine protected lexical atom where semantic continuity requires it, commonly a short Latin phrase or number-unit atom.

U+2009 is a renderer adapter, not a language rule.

## 11. Render feedback loop is mandatory

After writing a layout-sensitive Thai document, export/render and inspect.

The reviewer MUST check:

1. any stretched or abnormal gap;
2. long units filling full lines repeatedly;
3. orphan phrase or dependent connector;
4. repetitive rhythm across lines;
5. whether every visible breath corresponds to a semantic boundary;
6. any phrase split unnaturally;
7. mixed Thai/Latin wrapping;
8. page-break effects on argument continuity.

If any item fails, repair in this order:

1. recompose thought units;
2. reorder clauses;
3. adjust breath boundaries;
4. rebalance line composition;
5. only then adjust renderer separator.

The AI MUST NOT start by adding/removing spaces.

## 12. Mandatory verification language

The AI may say “semantic rhythm verified” only if:

- semantic thought units were actually composed;
- breath levels were applied;
- 3–5 unit rhythm review occurred;
- line/lookahead gate was considered where layout-sensitive;
- renderer output was inspected when required.

Otherwise it MUST say the semantic/render gate was not fully verified.

## Core invariant

**Spacing must follow thought.**

**Thought must not follow spacing.**

For Thai:

**Good rhythm does not come from equal gaps. It comes from thoughts with unequal weight.**
