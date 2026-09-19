# gov-templates/NIA

Official document templates for **NIA — สำนักงานนวัตกรรมแห่งชาติ (National
Innovation Agency, Thailand)**, Social Innovation grant program
correspondence. See `MANIFEST.md` for the file-by-file index.

## The 100% conformance rule (founder instruction, verbatim intent)

> "เทมเพลทต้องตามนี้ 100% เลยว่าทำตามเทมเพลททุกส่วนต้องตรงกับเทมเพลท ทำตัวบล็อกไว้ด้วยหละ"
> — the template must be followed 100%, every part must match the
> template, and a block/gate must exist for it.

This is not a style preference. When drafting any NIA letter from these
templates, an AI (any vendor) MUST:

1. Start from the exact file in `source/` for the letter type needed —
   never re-derive the wording from memory or paraphrase it "in the spirit
   of" the original.
2. Keep every fixed institutional phrase byte-for-byte as written in the
   source, including punctuation and the curly quotation marks (`“`/`”`)
   NIA's own templates use — do not silently swap them for straight quotes.
3. Fill in every blank (the `..........` / `……….` dot-leader runs, with or
   without an inline `(label)`) with real content — no dot-leader run may
   survive into the final document.
4. Two whole-paragraph authoring markers are instructions, not content, and
   must be replaced/removed, never reproduced literally: `-หัวบริษัท-` (or
   `-หัวบริษัท (ถ้ามี)-`) means "put the company letterhead here", and
   `(ตัวอย่าง ร่างจดหมาย)` / `(ตัวอย่าง)` means "(example draft)" — an
   annotation for whoever is using the template, not part of the letter.
5. Run the mechanical gate below before calling any draft final.

## The block: `scripts/gov_template_lock.py`

A general-purpose (not NIA-specific in code) extract+check tool lives at
`<repo>/scripts/gov_template_lock.py`. It is fail-closed for the cases
below, each independently adversarially reviewed and reproduced (see git
history) —

- a correctly filled-in letter → **PASS**;
- the same letter with one fixed phrase paraphrased → **FAIL**, pinpointing
  the exact paragraph and the exact wording that no longer matches;
- the still-blank source template itself → **FAIL**, listing every
  unresolved placeholder — proving a blank template cannot slip through as
  "conformant";
- a fixed phrase with an extra word glued directly onto the START or END
  of a paragraph (e.g. a negator like "ไม่" prepended with no space,
  flipping "อนุมัติ" **approve** into "ไม่อนุมัติ" **not** approve) →
  **FAIL**, via the boundary check on paragraph-opening/closing fixed text.

**Known limitation, not yet closed — read before trusting a PASS on
anything with heavy internal negation/qualification wording**: the
boundary check above only protects the FIRST and LAST fixed segment of
each paragraph. A fixed segment in the MIDDLE of a paragraph, directly
adjacent to a placeholder (e.g. `.....(ชื่อโครงการ).....อนุมัติ`), is
**not** boundary-checked — the same word-gluing/negation-flip attack still
works there and will currently produce a false PASS. This is a real,
independently-reproduced gap (not a hypothetical edge case), disclosed
rather than silently absorbed. Closing it needs dictionary-aware Thai
tokenization of the candidate to distinguish "the template's own designed
adjacency" from "an inserted extra word" — not yet built. Until it is,
read a PASS as "no full fixed-phrase paraphrase/deletion/reordering and no
paragraph-edge word-gluing detected," not as an unconditional guarantee
against every possible one-word insertion anywhere in the letter — a human
should still read the filled letter once before it goes out, the same way
any official correspondence should be read before sending regardless of
what tooling exists.

### Usage

```bash
# one-time, already done for every locked letter in MANIFEST.md:
python3 scripts/gov_template_lock.py extract \
  gov-templates/NIA/source/"2.1_จดหมายขอเบิกเงินทุนอุดหนุน (Social).docx" \
  -o gov-templates/NIA/locks/2.1.lock.json

# every time a draft is produced from a locked template:
python3 scripts/gov_template_lock.py check \
  gov-templates/NIA/locks/2.1.lock.json \
  path/to/your_draft.docx   # or .txt
```

Exit code 0 + `TEMPLATE LOCK PASS` = every fixed segment survived intact,
in order, and no placeholder was left unfilled. Any other result is a hard
block — fix the draft and re-check, do not proceed to send/submit it.

**What a PASS does NOT mean**: the tool checks wording fidelity to the
template, not whether the filled-in content (amounts, dates, project
names) is itself correct. That remains the drafter's responsibility.

## Discovery — how a skill finds "NIA lives here"

See the repo-root `SKILL.md` "Government-agency templates" section: before
drafting any official letter to a Thai government agency, check whether
`gov-templates/<AGENCY_CODE>/` exists in this repo. If it does, that
folder's `source/` files are the *only* authoritative starting point —
do not invent a generic layout, and do not treat `docs/thai-worldclass/`'s
general Typst/DOCX formal-letter guidance as a substitute for an
agency-supplied template when one exists. General guidance may still apply
for things the template doesn't specify (e.g. Thai semantic-breathing
composition of the blanks you fill in), but the template's own fixed
structure always wins.

## Not yet built (disclosed, not guessed at)

- Locks only exist for the 10 `.docx` letters, not the 3 legacy `.doc`
  report forms (`2.2`, `3.2`, `4.2`) or the `.xlsx`/`.pdf` reference files
  — those are structured forms/tables rather than prose letters and need a
  different extraction approach (table-cell-aware, not paragraph-dot-leader
  based) than `gov_template_lock.py` currently implements.
- No automated Jinja2/`generate_doc.py` integration yet for NIA letters —
  a drafter currently fills the blanks by hand (or an AI drafts prose into
  a copy) and then runs `gov_template_lock.py check` afterward. Wiring
  `generate_doc.py` to emit NIA-conformant `.docx` directly from a data
  file is future work.
- Only NIA is populated so far. The `gov-templates/<AGENCY>/` layout is
  meant to generalize to other agencies as they're supplied, following the
  same `source/` + `locks/` + `MANIFEST.md` + `README.md` convention.
