# thai_doc

Accurate Thai-language document generation for external tools (desktop apps,
Google Docs, browsers, PDF renderers, ...): fixes Thai line-wrapping and
generates documents from a template + data file, with the same content
guaranteed across every output format.

## The problem this solves

Thai script has no spaces between words. Most layout engines (Word's,
Google Docs', browsers') were built assuming space-delimited text, so a long
Thai run either overflows its box unbroken, or gets broken at a random
character -- sometimes splitting a consonant from its own vowel/tone mark.

## The fix

`scripts/thai_linebreak.py` segments Thai text into real words with
[PyThaiNLP](https://pythainlp.org/)'s dictionary-based tokenizer (`newmm`
engine) and inserts a zero-width space (`U+200B`) between word boundaries.
ZWSP is invisible and adds no visible spacing, but every mainstream layout
engine treats it as a legal break point. This is a standard, widely used
technique -- this module is a thin, tested, auditable wrapper around it, not
a new algorithm.

Properties (see `tests/test_thai_linebreak.py`):
- **Lossless**: `strip_zwsp(fix_thai_linebreaks(text)) == text` always.
- **Idempotent**: running it twice never double-inserts.
- **Non-Thai-safe**: Latin words, numbers, and existing whitespace/newlines
  are left untouched.

## Usage

### Just fix line-wrapping in a block of text

```bash
python3 scripts/thai_linebreak.py "ข้อความภาษาไทยยาวๆที่อยากให้ตัดบรรทัดถูกต้อง" > out.txt
```

Paste the contents of `out.txt` directly into Google Docs, Word, an email,
a chat box -- anywhere. The ZWSP characters travel with the text through
copy-paste and give the destination editor real break points.

### Generate a document from a template

```bash
pip install -r requirements.txt
python3 scripts/generate_doc.py \
  templates/formal_letter.txt.j2 \
  examples/formal_letter.example.yaml \
  -o out.docx -f docx
```

Supported `-f/--format`: `txt` (paste-ready, ZWSP-fixed plain text),
`html` (lang="th", Thai-safe font stack), `docx` (python-docx, sets both
the Latin and East-Asian/complex-script font slots so Word doesn't silently
fall back to a default font for the Thai glyph run).

Template format: a Jinja2 text file with `#SECTION_NAME#` markers (see
`templates/formal_letter.txt.j2`). Data is a `.yaml` or `.json` file mapping
template variable names to values. Caveat: any rendered body line that
itself both starts and ends with `#` (e.g. a literal `#hashtag#`, or a
markdown `#### heading ####`) is misparsed as a new section marker -- avoid
that shape in body text until this is tightened. The pipeline is: render Jinja2
placeholders -> split into named sections -> apply the line-break fix to
each section's final text -> write the requested format. The fix runs last,
on the final text, so a placeholder value can never reintroduce an
un-fixed Thai run.

## Status / open decisions (not yet resolved -- read before extending)

This is a first working version built to a general spec ("พิมพ์ภาษาไทยแม่นยำ
ในเครื่องมือภายนอกทั้งในคอมและ Google Docs และแก้ปัญหาการตัดบรรทัด"). A few
scope questions were left open rather than guessed silently:

1. **Direct Google Docs API integration** (create/update a Doc
   programmatically via OAuth) is *not* built yet -- the current `txt`
   output is copy-paste-ready into Docs, which needs no credentials, but a
   founder decision on OAuth scope/credential storage is needed before
   building a live API integration (this workspace's `safe-live-connect`
   and credential-handling rules apply to any such integration).
2. Only one example template (a formal letter) exists. Real target template
   types (certificates, official forms, contracts, ...) need to be supplied
   or specified before more templates are built.
3. `docx` output defaults to font "TH Sarabun New" (the Thai government's
   standard official-document font, THSarabunPSK lineage) -- confirm this is
   the right default, vs. e.g. Noto Sans Thai / Noto Serif Thai for other
   use cases.
4. PDF output is not implemented yet (candidates: LibreOffice headless
   conversion of the `docx` output, or a LaTeX/WeasyPrint HTML->PDF path
   using the same `html` output -- needs a decision on which toolchain to
   depend on).

## License

MIT.
