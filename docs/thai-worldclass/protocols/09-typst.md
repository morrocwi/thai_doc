# Typst Route — Thai Layout Oracle and Final PDF Compositor (v2.1)

Use this route for polished Thai PDF output, formal letters, reports, and layout diagnostics when Google Docs justification is unstable and an editable Word/DOCX master is not required.

## Research basis

v2.1 was designed after inspecting two upstream repositories on 2026-09-19:

### `whs/typst-govdoc`

- repository: https://github.com/whs/typst-govdoc
- inspected commit: `b0ca4535c92f70aa94ace3f9bcffeae501df893b` (2023-03-26)
- inspected files: `README.md`, `govdoc.typ`, `thai.typ`, `govdoctest.typ`
- GitHub exposes no SPDX/license metadata for the repository; its README states `ไม่สงวนลิขสิทธิ์`

The skill does **not** copy this template verbatim. It independently reimplements general structural ideas.

### `typst/typst`

- repository: https://github.com/typst/typst
- inspected stable release: `v0.15.1` (2026-07-17)
- inspected source snapshot on main: `094b9634d2aa506757d342103411a33a347e3012` (2026-09-18)
- license: Apache-2.0

The old 2023 `typst-govdoc` README records a historical limitation that Typst did not automatically break Thai and therefore required manual spacing. **That instruction MUST NOT be carried forward.** Typst 0.15.1's general line-break path uses `icu_segmenter::LineSegmenter::new_lstm(...)`, consumes UAX #14 opportunities, and the upstream test suite contains Thai line-break regression cases, including `linebreak-thai` and `issue-4468-linebreak-thai`.

Automatic Thai segmentation is a renderer capability, **not a semantic parser**. It does not replace this skill's thought-unit/breath model.

## What is extracted into v2.1

### From `typst-govdoc` — structural concepts only

- A4 formal page geometry;
- Thai 16pt baseline for formal documents;
- `lang: "th"` / `region: "TH"`;
- first-line indentation as paragraph geometry;
- document fields (`ที่`, `วันที่`, `เรื่อง`, `เรียน`, `อ้างถึง`, `สิ่งที่ส่งมาด้วย`) as structured layout objects;
- grids rather than literal-space tabs;
- Thai-digit conversion utility;
- unbreakable signature/sender regions;
- content measurement/alignment instead of manual tabs.

### From current Typst — compositor capabilities

- ICU4X LSTM-backed general line segmentation that includes Thai handling;
- optimized Knuth-Plass-style line breaking;
- explicit `par.justification-limits` for word-space and optional character tracking;
- modern `par.first-line-indent` including `all: true`;
- semantic paragraph structure useful for reliable layout/export behavior;
- deterministic compile/watch workflow suitable for regression rendering.

## Roles of Typst in this skill

Typst may serve as any of the following:

1. **Final PDF compositor** — preferred for deterministic Thai formal PDF when no editable DOCX is required.
2. **Layout oracle** — render the same clean semantic source in Typst to diagnose whether a Google Docs defect comes from semantics or from the Docs renderer.
3. **Formal-letter geometry engine** — use grids/blocks/measurements instead of literal spaces for metadata, attachments, dates, signatures, and sender blocks.
4. **Regression renderer** — compare rendered line/page behavior after changes to Thai semantic composition.

Typst is a renderer/compositor, not the semantic authority. A visually cleaner Typst result does not prove that the source wording is semantically well composed.

## Hard semantic boundary

The Typst route MUST consume the **clean semantic source**, not the Google Docs renderer-adapted source.

Therefore:

- remove Google-Docs-only U+2009 thin-space adaptations before Typst composition;
- reject WORD JOINER U+2060 and ZERO WIDTH SPACE U+200B as generic repairs;
- preserve NBSP/narrow NBSP only for genuine protected micro-atoms;
- do not inject spaces merely to create Thai word boundaries or line breaks;
- do not copy manual line-break placement from the 2023 `typst-govdoc` example into new Thai body prose;
- renderer-specific Typst controls MUST NOT be promoted back into semantic Thai rules.

## Minimum engine

The v2.1 verified design contract targets **Typst 0.15.1 or newer**.

If the Typst CLI is unavailable or older than the minimum, static source lint may still run, but final Typst/PDF status is **CANNOT VERIFY** until the document is compiled and visually inspected in a compatible environment.

## Required Thai text settings

A Thai Typst compositor MUST set or inherit:

```typst
#set text(
  lang: "th",
  region: "TH",
)
```

For deterministic output, also declare a Thai-capable font priority. The bundled house module uses:

```typst
font: ("Sarabun", "TH Sarabun New", "Noto Sans Thai")
```

No font files are bundled.

## Paragraph settings

For justified Thai body prose, v2.1 requires or inherits:

```typst
#set par(
  justify: true,
  linebreaks: "optimized",
)
```

Typst 0.15.1 uses optimized breaking automatically for justified paragraphs when `linebreaks: auto`, but the skill sets `"optimized"` explicitly for auditability.

### Justification limits

Typst exposes `par.justification-limits` to control how word spacing and tracking may vary. The house baseline is intentionally conservative:

```typst
#set par(
  justification-limits: (
    spacing: (min: 90%, max: 120%),
    tracking: (min: 0em, max: 0em),
  ),
)
```

This is a **renderer policy**, not a semantic rule. Typst's own documentation notes that spaces may exceed the configured `max` when no other justification solution exists. Therefore `justification-limits` is not a guarantee; rendered-page inspection remains mandatory.

Character-level tracking MUST NOT be enabled for Thai by default. Thai combining clusters and mark positioning are font-sensitive. Any nonzero tracking policy requires actual rendered regression evidence for the chosen font.

## Thai automatic line breaking

Current Typst uses the ICU4X general line segmenter for Thai. Consequences:

- Thai prose SHOULD NOT be manually split into pseudo-words merely to provide line-break points;
- old manual-spacing workarounds are stale;
- line-fit repair starts with semantic recomposition, then lets Typst select legal break opportunities;
- explicit hard body line breaks are exceptional and require a structural/semantic reason;
- automatic segmentation can choose legal renderer breaks, but it does not know this skill's semantic breath weights; visual and semantic QA still apply.

## Measure-assisted line composition

Typst's `measure`/layout primitives are useful after semantic composition for:

- estimating protected-atom width;
- aligning formal metadata without manual spaces;
- testing whether a thought unit is too wide for the target measure;
- regression comparison across fonts or margin changes.

Do not measure first and then change meaning to make a line fit. The order remains:

**meaning → thought unit → rhythm → line fit → Typst measurement/rendering**.

## Formal-letter architecture

The house Typst modules are:

- `typst/thai-worldclass.typ` — Thai page/text/paragraph compositor;
- `typst/formal-letter.typ` — structured private-formal fields and unbreakable signature/sender blocks;
- `typst/examples/formal_private_to_government.typ` — clean semantic-source example.

The useful formal layout decisions are:

- A4 margins: top 2.5cm, left 3cm, right 2cm, bottom 2cm unless authoritative template overrides;
- 16pt Thai body baseline;
- 2.5cm first-line indent implemented by `par.first-line-indent`, never leading literal spaces;
- attachments use a grid rather than repeated spaces;
- signature and sender blocks use `breakable: false`;
- Thai numerals come from a utility function rather than manual conversion.

### Private-company letter to a government agency

For a private company writing to a Thai government agency:

- use the `private-formal` mode;
- **do not insert the Garuda emblem** merely because the recipient is a government agency;
- use the sender's corporate identity/header if supplied;
- use formal Thai metadata/body conventions without impersonating a government-origin document.

The skill deliberately does not bundle `garuda.svg`.

### Official government-origin mode

An official emblem or exact government template may be used only when the user supplies/authorizes the required official template or asset and the task genuinely concerns an authorized government-origin document. Recipient identity alone is not authorization.

## Grid-not-spaces rule

This is forbidden when the alignment is created with literal spaces:

```text
สิ่งที่ส่งมาด้วย  ๑. ...
                  ๒. ...
```

Use a grid/table/layout object. Literal spaces may appear in semantic text, but they MUST NOT act as tab stops or geometry controls.

Similarly, do not reproduce the old workaround:

```typst
#h(2.5cm)ด้วย ...
```

for the first body paragraph. Modern Typst supports `first-line-indent`; use it.

## Layout-oracle workflow

When Google Docs JUSTIFIED fails:

1. return to the clean semantic source;
2. render the same prose in Typst with Thai `lang/region`, optimized line breaking, and conservative justification limits;
3. inspect the Typst PDF;
4. classify the difference:
   - both renderers fail similarly → likely semantic/composition defect;
   - Typst is clean but Google Docs stretches/breaks badly → likely Google Docs renderer defect;
   - Typst alone fails → inspect Typst font/settings/justification before changing semantics;
5. repair semantics first whenever a semantic defect exists;
6. keep renderer-specific workarounds isolated to their renderer.

Typst MUST NOT be used to overrule meaning simply because its page looks cleaner.

## Typst QA loop

`semantic compose → clean .typ source → static preflight → compile → PDF text check → page rasterization → visual inspection → repair → recompile`

Mandatory checks:

- correct Thai language/region;
- explicit optimized line breaking for justified Thai;
- deterministic Thai-capable font priority;
- no Google Docs thin-space contamination;
- no control-character patches;
- no manual-space geometry;
- no stale manual Thai wrapping workaround;
- no orphan dependent phrase where avoidable;
- no abnormal space expansion;
- no clipped/missing glyphs or unexpected fallback;
- signature/attachment blocks remain structurally intact;
- PDF remains searchable/copyable when required;
- every final page visually inspected.

Run:

```bash
python scripts/typst_preflight.py --self-test
python scripts/typst_preflight.py typst/examples/formal_private_to_government.typ --document-kind private
```

For compile verification when Typst is installed:

```bash
python scripts/typst_preflight.py typst/examples/formal_private_to_government.typ \
  --document-kind private --compile
```

## Fail-closed conditions

Typst route is NOT READY when:

- CLI is missing for a requested final Typst/PDF verification;
- engine version is below 0.15.1;
- Thai `lang` / `region` settings are absent and not inherited from the house module;
- deterministic Thai font selection is absent and not inherited;
- justified Thai does not use optimized line breaking;
- justified custom source omits a defined justification policy;
- Google Docs U+2009 adaptations leaked into Typst source;
- source uses repeated literal spaces as layout tabs;
- `#h(...)` is used as a manual first-paragraph indent hack;
- body line breaks/spaces were manually inserted merely to make lines wrap;
- private-company mode injects government-origin identity without authorization;
- final PDF was not rendered and visually inspected for a polished deliverable.
